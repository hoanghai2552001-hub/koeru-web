"""
verify_kanji.py — Xác minh và sửa dữ liệu kanji qua kanjiapi.dev + Jisho

Dùng trong skill extract-japanese sau bước trích xuất:
    python verify_kanji.py --input extracted.json --output verified.json

Hoặc import trực tiếp:
    from verify_kanji import verify_kanji_list

Nguồn dữ liệu:
  - kanjiapi.dev  → On/Kun readings chính xác, JLPT level, stroke count
  - jisho.org API → xác nhận + sửa reading từ ghép, lọc nghĩa tiếng Anh
"""

import json
import time
import re
import urllib.request
import urllib.parse
import sys
import argparse
from typing import Optional

KANJI_API = "https://kanjiapi.dev/v1/kanji/{}"
JISHO_API  = "https://jisho.org/api/v1/search/words?keyword={}"
HEADERS    = {"User-Agent": "KoeruApp/1.0"}

JLPT_NUM_TO_LABEL = {1: "N1", 2: "N2", 3: "N3", 4: "N4", 5: "N5"}

# ── Phát hiện nghĩa tiếng Anh (không có dấu tiếng Việt) ──────────────────────
VIET_DIACRITICS = re.compile(
    r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
    r'ÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]',
    re.IGNORECASE
)

def is_vietnamese(text: str) -> bool:
    return bool(VIET_DIACRITICS.search(text)) if text else False

def is_japanese(text: str) -> bool:
    """Kiểm tra chuỗi có chứa ký tự Nhật không."""
    return bool(re.search(r'[぀-ヿ一-鿿]', text)) if text else False

def is_english_meaning(text: str) -> bool:
    """Trả True nếu nghĩa có vẻ là tiếng Anh (không phải VN cũng không phải JP)."""
    if not text:
        return False
    if is_vietnamese(text) or is_japanese(text):
        return False
    # Nếu chủ yếu là chữ Latin không dấu → tiếng Anh
    latin = re.sub(r'[^a-zA-Z\s\-]', '', text).strip()
    return len(latin) > 3

# ── Cache để tránh gọi API trùng ─────────────────────────────────────────────
_kanji_cache = {}
_word_cache  = {}

# ── Gọi kanjiapi.dev ──────────────────────────────────────────────────────────
def fetch_kanji_info(kanji: str) -> Optional[dict]:
    if kanji in _kanji_cache:
        return _kanji_cache[kanji]
    url = KANJI_API.format(urllib.parse.quote(kanji))
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
            _kanji_cache[kanji] = data
            return data
    except Exception as e:
        print(f"  [kanjiapi] Lỗi khi tra {kanji}: {e}", file=sys.stderr)
        _kanji_cache[kanji] = None
        return None

# ── Gọi Jisho để lấy reading chính xác của từ ghép ───────────────────────────
def fetch_word_reading(word: str) -> Optional[dict]:
    if word in _word_cache:
        return _word_cache[word]
    url = JISHO_API.format(urllib.parse.quote(word))
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            results = json.loads(r.read().decode()).get("data", [])
        # Ưu tiên kết quả khớp chính xác
        for item in results:
            for jp in item.get("japanese", []):
                if jp.get("word") == word:
                    result = {
                        "reading": jp.get("reading", ""),
                        "is_common": item.get("is_common", False),
                        "jlpt": item.get("jlpt", []),
                        "meanings_en": [
                            d for s in item.get("senses", [])
                            for d in s.get("english_definitions", [])
                        ][:3],
                    }
                    _word_cache[word] = result
                    return result
        # Không khớp chính xác → lấy kết quả đầu
        if results:
            jp = results[0].get("japanese", [{}])[0]
            result = {
                "reading": jp.get("reading", ""),
                "is_common": results[0].get("is_common", False),
                "jlpt": results[0].get("jlpt", []),
                "meanings_en": [
                    d for s in results[0].get("senses", [])
                    for d in s.get("english_definitions", [])
                ][:3],
            }
            _word_cache[word] = result
            return result
    except Exception as e:
        print(f"  [jisho] Lỗi khi tra '{word}': {e}", file=sys.stderr)
    _word_cache[word] = None
    return None

# ── Format readings ───────────────────────────────────────────────────────────
def format_on(readings: list) -> str:
    return "、".join(readings)

def format_kun(readings: list) -> str:
    return "、".join(readings)

# ── Tạo meaning_jp từ words array ─────────────────────────────────────────────
def build_meaning_jp(words: list) -> str:
    """Lấy 2-3 từ ghép đầu để làm meaning_jp."""
    items = [w.get("w", "") for w in words if w.get("w")][:3]
    return "、".join(items)

# ── Verify và sửa words array ────────────────────────────────────────────────
def fix_words(words: list, call_api: bool = True) -> tuple[list, list]:
    """
    Sửa words array:
    - Loại bỏ entry có nghĩa tiếng Anh
    - Sửa reading sai qua Jisho
    Returns: (fixed_words, warnings)
    """
    fixed = []
    warnings = []

    for w in words:
        word_str = w.get("w", "")
        meaning  = w.get("m", "")
        reading  = w.get("r", "")

        # Lọc nghĩa tiếng Anh
        if is_english_meaning(meaning):
            warnings.append(f"Bỏ '{word_str}' (nghĩa EN: '{meaning}')")
            continue

        new_w = dict(w)

        # Sửa reading qua Jisho
        if call_api and word_str:
            winfo = fetch_word_reading(word_str)
            time.sleep(0.15)

            if winfo and winfo.get("reading"):
                jisho_reading = winfo["reading"]
                if reading and reading != jisho_reading:
                    warnings.append(f"  Sửa reading '{word_str}': '{reading}' → '{jisho_reading}'")
                    new_w["r"] = jisho_reading
                elif not reading:
                    new_w["r"] = jisho_reading

                if winfo.get("is_common"):
                    new_w["common"] = True

        fixed.append(new_w)

    return fixed, warnings

# ── Verify 1 kanji entry ──────────────────────────────────────────────────────
def verify_single(entry: dict, call_api: bool = True, verbose: bool = True) -> dict:
    kanji_char = entry.get("kanji", "")
    if not kanji_char:
        return entry

    result = dict(entry)
    warnings = []

    if verbose:
        print(f"  {kanji_char}", end=" ", flush=True)

    # --- kanjiapi.dev: On/Kun/Level/Strokes ---
    if call_api:
        info = fetch_kanji_info(kanji_char)
        time.sleep(0.25)

        if info:
            api_on  = format_on(info.get("on_readings", []))
            api_kun = format_kun(info.get("kun_readings", []))
            api_jlpt_num = info.get("jlpt")
            api_jlpt = JLPT_NUM_TO_LABEL.get(api_jlpt_num, "") if api_jlpt_num else ""
            api_strokes = info.get("stroke_count")

            # On reading
            old_on = result.get("on", "")
            if api_on and api_on != old_on:
                if old_on:
                    warnings.append(f"On: '{old_on}'→'{api_on}'")
                result["on"] = api_on

            # Kun reading
            old_kun = result.get("kun", "")
            if api_kun and api_kun != old_kun:
                if old_kun:
                    warnings.append(f"Kun: '{old_kun}'→'{api_kun}'")
                result["kun"] = api_kun

            # JLPT level
            if api_jlpt and not result.get("level"):
                result["level"] = api_jlpt

            # Stroke count
            if api_strokes:
                result["strokes"] = api_strokes

            if verbose:
                print(f"[on={api_on or'—'} kun={api_kun or'—'} N{api_jlpt_num or'?'}]", end=" ")
        else:
            if verbose:
                print("[API miss]", end=" ")

    # --- Sửa words ---
    words = result.get("words", [])
    fixed_words, word_warnings = fix_words(words, call_api=call_api)
    warnings.extend(word_warnings)

    # Nếu sau khi lọc tiếng Anh còn ít hơn 1 từ, giữ nguyên toàn bộ (tránh mất data)
    if len(fixed_words) < 1 and len(words) > 0:
        fixed_words = words  # rollback
        warnings.append("Rollback words (quá nhiều bị lọc)")

    result["words"] = fixed_words

    # --- meaning_jp: tạo lại từ words nếu chưa có hoặc trống ---
    if not result.get("meaning_jp") and fixed_words:
        result["meaning_jp"] = build_meaning_jp(fixed_words)
    elif fixed_words:
        # Giữ meaning_jp cũ nếu đã có (thường là do người dùng tự nhập)
        pass

    if warnings:
        result["_warnings"] = warnings
        if verbose:
            print(f"⚠ {len(warnings)}fix")
    else:
        if verbose:
            print("✓")

    return result

# ── Verify toàn bộ list ───────────────────────────────────────────────────────
def verify_kanji_list(kanji_list: list, call_api: bool = True, verbose: bool = True) -> dict:
    """
    Nhận list kanji objects, trả về:
    {
      "verified": [...],
      "summary": {"total", "corrected", "unchanged"}
    }
    """
    if verbose:
        print(f"\n🔍 Xác minh {len(kanji_list)} kanji qua kanjiapi.dev + Jisho...\n")

    verified = []
    corrected = 0

    for i, entry in enumerate(kanji_list):
        if verbose and i % 50 == 0 and i > 0:
            print(f"\n  [{i}/{len(kanji_list)}] đã xong...\n")
        result = verify_single(entry, call_api=call_api, verbose=verbose)
        if result.get("_warnings"):
            corrected += 1
        # Xoá key tạm trước khi lưu
        result.pop("_warnings", None)
        verified.append(result)

    summary = {
        "total": len(kanji_list),
        "corrected": corrected,
        "unchanged": len(kanji_list) - corrected,
    }

    if verbose:
        print(f"\n✅ Xong! {corrected}/{len(kanji_list)} kanji được điều chỉnh.\n")

    return {"verified": verified, "summary": summary}

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Verify kanji data via kanjiapi.dev + Jisho")
    parser.add_argument("--input",   "-i", required=True)
    parser.add_argument("--output",  "-o", required=True)
    parser.add_argument("--key",     "-k", default="kanji",
                        help="Key trong JSON chứa mảng kanji (default: 'kanji')")
    parser.add_argument("--no-api",  action="store_true",
                        help="Chỉ lọc tiếng Anh, không gọi API")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    kanji_list = data.get(args.key, data) if isinstance(data, dict) else data
    result = verify_kanji_list(kanji_list, call_api=not args.no_api)

    if isinstance(data, dict):
        data[args.key] = result["verified"]
        output_data = data
    else:
        output_data = result["verified"]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"💾 Đã lưu → {args.output}")
    s = result["summary"]
    print(f"   Tổng: {s['total']} | Sửa: {s['corrected']} | Không đổi: {s['unchanged']}")

if __name__ == "__main__":
    main()
