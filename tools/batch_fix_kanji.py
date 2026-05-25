"""
batch_fix_kanji.py — Sửa toàn bộ kanji-data.js

Thực hiện:
  1. Parse kanji-data.js → list of dicts
  2. Với mỗi kanji:
     - Verify On/Kun qua kanjiapi.dev
     - Điền JLPT level nếu trống
     - Thêm stroke count
     - Sửa reading từ ghép sai qua Jisho
     - Loại bỏ words có nghĩa tiếng Anh
     - Tạo/cập nhật meaning_jp từ words
  3. Ghi lại kanji-data.js với format gốc (const ALL_KANJI = [...])
  4. Lưu backup + log những thay đổi

Chạy:
    python batch_fix_kanji.py
    python batch_fix_kanji.py --dry-run      # chỉ xem log, không ghi file
    python batch_fix_kanji.py --resume 200   # tiếp tục từ kanji thứ 200
    python batch_fix_kanji.py --no-api       # chỉ lọc tiếng Anh, không gọi API
"""

import json
import re
import sys
import os
import time
import argparse
import shutil
from datetime import datetime

# Thêm đường dẫn tới verify_kanji
SKILL_SCRIPTS = os.path.join(os.path.dirname(__file__),
    ".claude", "skills", "extract-japanese", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)
from verify_kanji import verify_single, is_english_meaning, build_meaning_jp

INPUT_FILE  = "js/kanji-data.js"
OUTPUT_FILE = "js/kanji-data.js"
BACKUP_FILE = "js/kanji-data.backup.js"
LOG_FILE    = "batch_fix_kanji.log"
PROGRESS_FILE = "batch_fix_kanji.progress.json"

# ── Parse JS → list of dicts ──────────────────────────────────────────────────
def parse_kanji_js(filepath: str) -> tuple[list, str, str]:
    """
    Trả về (kanji_list, header, footer).
    header: phần trước ALL_KANJI = [
    footer: phần sau ];
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Tìm vị trí mảng
    start = content.index("const ALL_KANJI = [")
    end   = content.rindex("];") + 2

    header = content[:start]
    footer = content[end:]

    # Lấy nội dung mảng (từng dòng = 1 kanji)
    array_content = content[start + len("const ALL_KANJI = ["):end - 2]

    # Tách từng dòng kanji (bỏ qua dòng comment và dòng trống)
    kanji_lines = []
    current_level = None

    for line in array_content.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("// ====="):
            # Lưu comment level
            kanji_lines.append({"_comment": line_stripped})
        elif line_stripped.startswith("{kanji:"):
            # Parse JS object → Python dict
            obj = js_line_to_dict(line_stripped.rstrip(","))
            if obj:
                kanji_lines.append(obj)

    return kanji_lines, header, footer

# ── Convert 1 dòng JS object → Python dict ───────────────────────────────────
def js_line_to_dict(js_str: str) -> dict:
    """
    Chuyển:
      {kanji:"木",hanviet:"MỘC",on:"ボク",kun:"き",meaning:"cây",meaning_jp:"木",level:"N5",words:[...]}
    Thành Python dict.
    """
    try:
        # Thêm ngoặc kép quanh keys không có ngoặc
        json_str = re.sub(r'(\b)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'"\2":', js_str)
        # Đổi single quotes thành double quotes nếu có
        # (thường không cần vì file dùng double quotes)
        return json.loads(json_str)
    except Exception as e:
        # Thử phương pháp dự phòng
        try:
            # Dùng eval an toàn hơn bằng cách xử lý thủ công
            return parse_js_object_manual(js_str)
        except Exception as e2:
            print(f"  ⚠️  Không parse được: {js_str[:60]}... ({e})", file=sys.stderr)
            return {}

def parse_js_object_manual(js_str: str) -> dict:
    """Fallback parser cho các trường hợp đặc biệt."""
    # Thêm quotes vào keys
    s = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', js_str)
    # Xử lý undefined/null
    s = s.replace(': undefined', ': null')
    return json.loads(s)

# ── Format 1 kanji dict → JS line ─────────────────────────────────────────────
def dict_to_js_line(obj: dict) -> str:
    """Chuyển dict → 1 dòng JS theo format gốc."""
    fields = ["kanji", "hanviet", "on", "kun", "meaning", "meaning_jp", "level", "strokes", "words"]
    parts = []
    for key in fields:
        if key not in obj:
            continue
        val = obj[key]
        if isinstance(val, str):
            # Escape ngoặc kép trong string
            escaped = val.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'{key}:"{escaped}"')
        elif isinstance(val, list):
            # words array → compact JSON
            arr_str = json.dumps(val, ensure_ascii=False, separators=(',', ':'))
            parts.append(f'{key}:{arr_str}')
        elif isinstance(val, (int, float)):
            parts.append(f'{key}:{val}')
        elif isinstance(val, bool):
            parts.append(f'{key}:{"true" if val else "false"}')
        elif val is None:
            continue  # bỏ qua null

    return "{" + ",".join(parts) + "}"

# ── Ghi lại JS file ────────────────────────────────────────────────────────────
def write_kanji_js(filepath: str, kanji_data: list, header: str, footer: str):
    lines = []
    for item in kanji_data:
        if "_comment" in item:
            lines.append(item["_comment"])
        else:
            lines.append(dict_to_js_line(item) + ",")

    # Xoá dấu phẩy thừa ở cuối
    if lines and lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]

    content = header + "const ALL_KANJI = [\n"
    content += "\n".join(lines)
    content += "\n];" + footer

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ── Load/Save progress ────────────────────────────────────────────────────────
def load_progress() -> dict:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"done": [], "results": []}

def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true", help="Không ghi file, chỉ log")
    parser.add_argument("--resume",   type=int, default=0, help="Bắt đầu từ index N")
    parser.add_argument("--no-api",   action="store_true", help="Chỉ lọc EN, không gọi API")
    parser.add_argument("--limit",    type=int, default=0, help="Chỉ xử lý N kanji đầu (debug)")
    parser.add_argument("--no-words-api", action="store_true",
                        help="Verify kanji API nhưng không verify words (nhanh hơn)")
    args = parser.parse_args()

    print("=" * 60)
    print("KOERU — Batch Fix kanji-data.js")
    print(f"Bắt đầu: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    print("=" * 60)

    # Đọc file gốc
    print(f"\n📂 Đọc {INPUT_FILE}...")
    kanji_data, header, footer = parse_kanji_js(INPUT_FILE)

    kanji_only = [x for x in kanji_data if "_comment" not in x]
    comments   = {i: x for i, x in enumerate(kanji_data) if "_comment" in x}
    print(f"   Tìm thấy {len(kanji_only)} kanji, {len(comments)} comment dòng")

    # Backup
    if not args.dry_run and not os.path.exists(BACKUP_FILE):
        shutil.copy(INPUT_FILE, BACKUP_FILE)
        print(f"   💾 Backup → {BACKUP_FILE}")

    # Log file
    log = open(LOG_FILE, "w", encoding="utf-8") if not args.dry_run else sys.stdout

    start_idx = args.resume
    limit = args.limit if args.limit > 0 else len(kanji_only)
    total = min(limit, len(kanji_only))

    changes_total   = 0
    removed_words   = 0
    fixed_readings  = 0

    print(f"\n🔧 Xử lý {total - start_idx} kanji (từ index {start_idx})...\n")

    # Xử lý từng kanji
    for i, entry in enumerate(kanji_only):
        if i < start_idx:
            continue
        if i >= limit:
            break

        kanji_char = entry.get("kanji", "?")
        level = entry.get("level", "")

        # Progress display mỗi 10 kanji
        if (i - start_idx) % 10 == 0:
            print(f"\n[{i+1}/{total}] {level} — đang xử lý...", flush=True)

        sys.stdout.write(f"  {kanji_char} ")
        sys.stdout.flush()

        old_words_count = len(entry.get("words", []))

        # Patch: nếu --no-words-api thì monkeypatch fix_words để skip Jisho
        if args.no_words_api:
            from verify_kanji import fix_words as orig_fix
            import verify_kanji as vk_module
            orig = vk_module.fix_words
            def patched_fix(words, call_api=True):
                return orig(words, call_api=False)
            vk_module.fix_words = patched_fix

        result = verify_single(
            entry,
            call_api=not args.no_api,
            verbose=True
        )

        if args.no_words_api:
            vk_module.fix_words = orig

        warnings = result.pop("_warnings", [])
        new_words_count = len(result.get("words", []))

        if warnings:
            changes_total += 1
            removed_words  += (old_words_count - new_words_count)
            for w in warnings:
                log.write(f"[{kanji_char}] {w}\n")

        kanji_only[i] = result

        # Lưu progress mỗi 50 kanji
        if (i + 1) % 50 == 0 and not args.dry_run:
            # Ghi tạm vào file progress
            save_progress({"last_index": i + 1})
            # Rebuild full list với comments
            full_list = []
            ki = 0
            for j in range(len(kanji_data)):
                if j in comments:
                    full_list.append(kanji_data[j])
                else:
                    if ki < len(kanji_only):
                        full_list.append(kanji_only[ki])
                    ki += 1
            write_kanji_js(OUTPUT_FILE + ".tmp", full_list, header, footer)
            print(f"\n  💾 Checkpoint tại index {i+1}", flush=True)

    # Rebuild full list với comments
    full_list = []
    ki = 0
    for j in range(len(kanji_data)):
        if j in comments:
            full_list.append(kanji_data[j])
        else:
            if ki < len(kanji_only):
                full_list.append(kanji_only[ki])
            ki += 1

    # Ghi kết quả
    if not args.dry_run:
        write_kanji_js(OUTPUT_FILE, full_list, header, footer)
        # Dọn file tạm
        if os.path.exists(OUTPUT_FILE + ".tmp"):
            os.remove(OUTPUT_FILE + ".tmp")
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        print(f"\n\n💾 Đã ghi → {OUTPUT_FILE}")
    else:
        print(f"\n\n[DRY RUN] Không ghi file.")

    # Tổng kết
    print("\n" + "=" * 60)
    print("TỔNG KẾT")
    print(f"  Tổng kanji xử lý : {total - start_idx}")
    print(f"  Kanji được sửa   : {changes_total}")
    print(f"  Words bị xoá (EN): {removed_words}")
    print(f"  Log              : {LOG_FILE}")
    print(f"  Backup           : {BACKUP_FILE}")
    print("=" * 60)

    if log != sys.stdout:
        log.close()

if __name__ == "__main__":
    main()
