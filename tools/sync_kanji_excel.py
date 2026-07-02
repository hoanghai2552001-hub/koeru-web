#!/usr/bin/env python3
"""
sync_kanji_excel.py — Đồng bộ 1 chiều: Excel → JS data files
Source: input/excel/kanji_KOERU_full.xlsx
Targets:
  js/kanji-data.js          (window.KANJI_DATA flat array)
  js/kanji-data-n5.js       (window.KANJI_N5)
  js/kanji-data-n4.js       (window.KANJI_N4)
  js/kanji-data-n3.js       (window.KANJI_N3)
  js/kanji-data-n2.js       (window.KANJI_N2)
  js/kanji-data-n1.js       (window.KANJI_N1)
  kanji-map-data.js         (window.KANJI_DATA object {kanji,vocab})

Luật:
- KHÔNG SỬA Excel
- Giữ nguyên freq_rank, grade, mnemonic, mn_vi từ JS hiện tại
- Giữ nguyên toàn bộ vocab array trong kanji-map-data.js

Usage:
  python tools/sync_kanji_excel.py [--project-root PATH]
"""

import json, re, sys, ast
from pathlib import Path
from datetime import date

# ── 1. SETUP ────────────────────────────────────────────────────────────────

def find_project_root():
    """Tìm thư mục gốc project KOERU từ vị trí script."""
    here = Path(__file__).resolve().parent
    # tools/ nằm trong project root
    root = here.parent
    if (root / "js" / "kanji-data.js").exists():
        return root
    # Fallback: thư mục hiện tại
    cwd = Path.cwd()
    if (cwd / "js" / "kanji-data.js").exists():
        return cwd
    return root

args = sys.argv[1:]
if "--project-root" in args:
    ROOT = Path(args[args.index("--project-root") + 1])
else:
    ROOT = find_project_root()

EXCEL = ROOT / "input" / "excel" / "kanji_KOERU_full.xlsx"
KANJI_DATA_JS   = ROOT / "js" / "kanji-data.js"
KANJI_MAP_JS    = ROOT / "kanji-map-data.js"
LEVEL_FILES = {
    "N5": ROOT / "js" / "kanji-data-n5.js",
    "N4": ROOT / "js" / "kanji-data-n4.js",
    "N3": ROOT / "js" / "kanji-data-n3.js",
    "N2": ROOT / "js" / "kanji-data-n2.js",
    "N1": ROOT / "js" / "kanji-data-n1.js",
}

print(f"[sync] Project root: {ROOT}")
print(f"[sync] Excel: {EXCEL}")

try:
    import pandas as pd
except ImportError:
    print("[error] Cần cài pandas: pip install pandas openpyxl")
    sys.exit(1)

# ── 2. ĐỌC EXCEL ────────────────────────────────────────────────────────────

def parse_parts(parts_str):
    """Parse parts column — supports multiple formats:
    - '女, 宀, 一'        (plain comma-separated, new standard)
    - '"女", "宀", "一"' (quoted, legacy format)
    - '["女","宀"]'      (JSON-like)
    """
    if not isinstance(parts_str, str) or not parts_str.strip():
        return []
    s = parts_str.strip()
    # Try ast.literal_eval first (handles quoted/JSON-like formats)
    try:
        result = list(ast.literal_eval(f"[{s}]"))
        if result:
            return result
    except Exception:
        pass
    # Fallback: quoted regex '"女"'
    quoted = re.findall(r'"([^"]+)"', s)
    if quoted:
        return quoted
    # Fallback 2: plain comma-separated (new standard: 女, 宀, 一)
    return [p.strip() for p in s.split(",") if p.strip()]

def parse_radical_char(radical_str):
    """'⼧|うかんむり|roof, house|mái nhà' → '⼧'"""
    if not isinstance(radical_str, str):
        return ""
    return radical_str.split("|")[0].strip()

xl = pd.ExcelFile(EXCEL)
print(f"[sync] Sheets: {xl.sheet_names}")

# Đọc tất cả kanji sheets
kanji_rows = []
for level in ["N5", "N4", "N3", "N2", "N1"]:
    if level not in xl.sheet_names:
        print(f"[warn] Sheet {level} không tìm thấy, bỏ qua")
        continue
    df = xl.parse(level, dtype=str)
    df = df.fillna("")
    for _, row in df.iterrows():
        k = str(row.get("kanji", "")).strip()
        if not k:
            continue
        # Lấy level từ cột level nếu có, fallback sheet name
        lvl = str(row.get("level", level)).strip() or level
        kanji_rows.append({
            "kanji": k,
            "hanviet": str(row.get("hanviet", "")).strip(),
            "on":   str(row.get("on", "")).strip(),
            "kun":  str(row.get("kun", "")).strip(),
            "meaning": str(row.get("meaning", "")).strip(),
            "stroke": int(row["stroke"]) if row.get("stroke", "").strip().isdigit() else 0,
            "radical": str(row.get("radical", "")).strip(),
            "parts": parse_parts(str(row.get("parts", ""))),
            "level": lvl,
        })

print(f"[sync] Đọc được {len(kanji_rows)} kanji từ Excel")

# Đọc Words sheet
words_by_kanji = {}  # kanji_char → [{w, r, m}]
words_seen = set()   # (kanji, word) đã thêm — để dedup khi merge Vocabs

if "Words" in xl.sheet_names:
    wdf = xl.parse("Words", dtype=str).fillna("")
    for _, row in wdf.iterrows():
        k = str(row.get("kanji", "")).strip()
        w = str(row.get("word", "")).strip()
        r = str(row.get("reading", "")).strip()
        m = str(row.get("meaning", "")).strip()
        if k and w:
            words_by_kanji.setdefault(k, []).append({"w": w, "r": r, "m": m})
            words_seen.add((k, w))
    print(f"[sync] Words sheet: {sum(len(v) for v in words_by_kanji.values())} từ vựng")
else:
    print("[warn] Không tìm thấy sheet Words")

# Đọc Vocabs sheet — bổ sung từ gắn với kanji cụ thể (không trùng Words)
STANDALONE_TAGS = {"語彙", "仮名", "外来語", "語", ""}
vocabs_added = 0
if "Vocabs" in xl.sheet_names:
    vdf = xl.parse("Vocabs", dtype=str).fillna("")
    for _, row in vdf.iterrows():
        k = str(row.get("kanji relate", "")).strip()
        w = str(row.get("word", "")).strip()
        r = str(row.get("reading", "")).strip()
        m = str(row.get("meaning", "")).strip()
        # Chỉ thêm nếu: có kanji cụ thể, có word, chưa có trong Words sheet
        if k and k not in STANDALONE_TAGS and w and (k, w) not in words_seen:
            words_by_kanji.setdefault(k, []).append({"w": w, "r": r, "m": m})
            words_seen.add((k, w))
            vocabs_added += 1
    print(f"[sync] Vocabs sheet: bổ sung {vocabs_added} từ mới (đã dedup với Words)")
else:
    print("[info] Không có sheet Vocabs — bỏ qua")

# ── 3. TẢI PRESERVED FIELDS TỪ JS HIỆN TẠI ─────────────────────────────────

def extract_js_array(text):
    """Trích xuất array JSON từ JS file dạng window.X = [...] hoặc window.X = {...}"""
    # Tìm phần sau dấu = đầu tiên
    m = re.search(r'window\.\w+\s*=\s*', text)
    if not m:
        return None
    json_str = text[m.end():].rstrip('; \n\r\t')
    return json_str


def decode_js_str(s: str) -> str:
    """Decode JS string escape sequences về Python string thuần.
    Dùng khi đọc preserved fields từ file JS để tránh double-escaping khi sync nhiều lần.
    """
    prev = None
    while prev != s:
        prev = s
        s = s.replace("\\\\", "\x00BKSL\x00")
        s = s.replace('\\"', '"')
        s = s.replace("\\'", "'")
        s = s.replace("\x00BKSL\x00", "\\")
    return s


# Load preserved fields từ kanji-data.js
preserved = {}  # kanji_char → {freq_rank, grade}
if KANJI_DATA_JS.exists():
    try:
        txt = KANJI_DATA_JS.read_text(encoding="utf-8")
        # Parse bằng regex thay vì JSON (vì format JS không phải JSON chuẩn)
        for m in re.finditer(r'\{kanji:"([^"]+)"[^}]*?\}', txt, re.DOTALL):
            block = m.group(0)
            k = m.group(1)
            freq_m = re.search(r'freq_rank:(\d+)', block)
            grade_m = re.search(r'grade:(\d+)', block)
            preserved[k] = {
                "freq_rank": int(freq_m.group(1)) if freq_m else None,
                "grade": int(grade_m.group(1)) if grade_m else None,
            }
        print(f"[sync] Loaded preserved fields từ kanji-data.js: {len(preserved)} entries")
    except Exception as e:
        print(f"[warn] Không thể đọc kanji-data.js: {e}")

# Load preserved fields từ kanji-map-data.js (thêm mnemonic)
preserved_map = {}  # kanji_char → {freq_rank, grade, mnemonic, mn_vi}
preserved_vocab = []  # vocab array giữ nguyên
if KANJI_MAP_JS.exists():
    try:
        txt = KANJI_MAP_JS.read_text(encoding="utf-8")
        # Trích kanji array entries
        for m in re.finditer(r'\{\s*id:"([^"]+)"[^}]*?\}', txt, re.DOTALL):
            block = m.group(0)
            k = m.group(1)
            freq_m  = re.search(r'freq_rank:(\d+)', block)
            grade_m = re.search(r'grade:(\d+)', block)
            mnemo_m = re.search(r'mnemonic:"((?:[^"\\]|\\.)*)"', block)
            mn_vi_m = re.search(r'mn_vi:"((?:[^"\\]|\\.)*)"', block)
            preserved_map[k] = {
                "freq_rank": int(freq_m.group(1)) if freq_m else None,
                "grade": int(grade_m.group(1)) if grade_m else None,
                "mnemonic": decode_js_str(mnemo_m.group(1)) if mnemo_m else "",
                "mn_vi": decode_js_str(mn_vi_m.group(1)) if mn_vi_m else "",
            }
        # Trích vocab array (giữ nguyên toàn bộ)
        vocab_m = re.search(r'vocab:\s*(\[.*?\])\s*\}', txt, re.DOTALL)
        if vocab_m:
            preserved_vocab_raw = vocab_m.group(1)
            # Chỉ lấy "vocab: [...]" — KHÔNG lấy dấu } cuối (group(0) có thêm })
            preserved_vocab_text = f"vocab: {vocab_m.group(1)}"
        else:
            preserved_vocab_text = "vocab: []"
        print(f"[sync] Loaded preserved map fields: {len(preserved_map)} entries")
    except Exception as e:
        print(f"[warn] Không thể đọc kanji-map-data.js: {e}")
        preserved_vocab_text = "vocab: []"

# ── 4. BUILD MERGED DATA ─────────────────────────────────────────────────────

def js_str(s):
    """Escape Python string → JS double-quoted string literal (1 level only)."""
    s = str(s) if s is not None else ""
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return s

def js_arr(lst):
    """List → JS array literal."""
    if not lst:
        return "[]"
    return "[" + ",".join(f'"{js_str(x)}"' for x in lst) + "]"

def build_kanji_entry(row):
    """Build 1 entry cho kanji-data.js format."""
    k = row["kanji"]
    words = words_by_kanji.get(k, [])
    pres = preserved.get(k, {})
    freq_rank = pres.get("freq_rank")
    grade = pres.get("grade")

    words_js = "[" + ",".join(
        '{' + f'"w":"{js_str(w["w"])}","r":"{js_str(w["r"])}","m":"{js_str(w["m"])}"' + '}'
        for w in words
    ) + "]"

    parts = row["parts"] or []

    fields = []
    fields.append(f'kanji:"{js_str(k)}"')
    fields.append(f'hanviet:"{js_str(row["hanviet"])}"')
    fields.append(f'on:"{js_str(row["on"])}"')
    fields.append(f'kun:"{js_str(row["kun"])}"')
    fields.append(f'meaning:"{js_str(row["meaning"])}"')
    fields.append(f'level:"{row["level"]}"')
    fields.append(f'words:{words_js}')
    fields.append(f'stroke:{row["stroke"]}')
    if freq_rank is not None:
        fields.append(f'freq_rank:{freq_rank}')
    if grade is not None:
        fields.append(f'grade:{grade}')
    fields.append(f'radical:"{js_str(row["radical"])}"')
    fields.append(f'parts:{js_arr(parts)}')

    return "{" + ",".join(fields) + "}"

def build_map_entry(row):
    """Build 1 entry cho kanji-map-data.js format."""
    k = row["kanji"]
    pres = preserved_map.get(k, {})
    freq_rank = pres.get("freq_rank")
    grade = pres.get("grade")
    mnemonic = pres.get("mnemonic", "")
    mn_vi = pres.get("mn_vi", "")

    # onyomi/kunyomi: split by 、
    onyomi = [x.strip() for x in row["on"].split("、") if x.strip()] if row["on"] else []
    kunyomi = [x.strip() for x in row["kun"].split("、") if x.strip() and x.strip() != "—"] if row["kun"] else []

    radical_char = parse_radical_char(row["radical"])
    components = row["parts"] or []

    fields = []
    fields.append(f'id:"{js_str(k)}"')
    fields.append(f'han_viet:"{js_str(row["hanviet"])}"')
    fields.append(f'onyomi:{js_arr(onyomi)}')
    fields.append(f'kunyomi:{js_arr(kunyomi)}')
    fields.append(f'meaning:"{js_str(row["meaning"])}"')
    fields.append(f'stroke:{row["stroke"]}')
    fields.append(f'jlpt:"{row["level"]}"')
    fields.append(f'status:"reviewed"')
    fields.append(f'radical:"{js_str(radical_char)}"')
    fields.append(f'components:{js_arr(components)}')
    if freq_rank is not None:
        fields.append(f'freq_rank:{freq_rank}')
    if grade is not None:
        fields.append(f'grade:{grade}')
    if mnemonic:
        fields.append(f'mnemonic:"{js_str(mnemonic)}"')
    if mn_vi:
        fields.append(f'mn_vi:"{js_str(mn_vi)}"')

    return "    { " + ", ".join(fields) + " }"

# ── 5. VIẾT OUTPUT FILES ─────────────────────────────────────────────────────

today = date.today().strftime("%Y%m%d")
total = len(kanji_rows)

# 5a. kanji-data.js (all levels combined)
all_entries = [build_kanji_entry(r) for r in kanji_rows]
content = (
    f"window.KANJI_DATA = [\n"
    + ",\n".join(all_entries)
    + "\n];\nwindow.ALL_KANJI = window.KANJI_DATA;\n"
)
KANJI_DATA_JS.write_text(content, encoding="utf-8")
print(f"[sync] ✓ {KANJI_DATA_JS.name} — {total} entries")

# 5b. kanji-data-n{X}.js
VAR_NAMES = {"N5": "KANJI_N5", "N4": "KANJI_N4", "N3": "KANJI_N3", "N2": "KANJI_N2", "N1": "KANJI_N1"}
for level, outfile in LEVEL_FILES.items():
    rows = [r for r in kanji_rows if r["level"] == level]
    entries = [build_kanji_entry(r) for r in rows]
    var = VAR_NAMES[level]
    content = (
        f"// KOERU Kanji Data — {level}\n"
        f"window.{var} = [\n"
        + ",\n".join(entries)
        + "\n];\n"
    )
    outfile.write_text(content, encoding="utf-8")
    print(f"[sync] ✓ {outfile.name} — {len(rows)} entries")

# 5c. kanji-map-data.js
map_entries = [build_map_entry(r) for r in kanji_rows]
map_content = (
    f"// kanji-map-data.js — auto-generated from Excel\n"
    f"// Total: {total} kanji (N5-N1)\n"
    f"// Generated: {today}\n"
    f"// Source: input/excel/kanji_KOERU_full.xlsx\n\n"
    f"window.KANJI_DATA = {{\n"
    f"  kanji: [\n"
    + ",\n".join(map_entries)
    + "\n  ],\n\n  "
    + preserved_vocab_text
    + "\n};\n"
)
KANJI_MAP_JS.write_text(map_content, encoding="utf-8")
print(f"[sync] ✓ kanji-map-data.js — {total} entries + vocab preserved")

print(f"\n[sync] ✅ Hoàn thành! {total} kanji, {sum(len(v) for v in words_by_kanji.values())} từ vựng")
print(f"[sync] Files đã cập nhật:")
print(f"  - js/kanji-data.js")
for level in ["N5","N4","N3","N2","N1"]:
    print(f"  - js/kanji-data-{level.lower()}.js")
print(f"  - kanji-map-data.js")
print(f"\n[sync] ⚠️  Nhớ bump cache version trong HTML files nếu cần:")
print(f"  kanji-data.js?v={today}")

# ── 6. AUTO QA ───────────────────────────────────────────────────────────────
import subprocess as _sp
_home = Path.home()
_qa_script = _home / ".claude" / "skills" / "koeru-data-check" / "scripts" / "check_kanji_data.py"
if _qa_script.exists():
    print(f"\n[sync] 🔍 Chạy QA tự động...")
    _r = _sp.run([sys.executable, str(_qa_script), str(ROOT)], capture_output=True, text=True)
    # Chỉ hiện dòng tóm tắt (không spam full report)
    _summary_lines = [l for l in _r.stdout.splitlines()
                      if any(x in l for x in ["✅ SẠCH", "❌", "⚠️", "🎉", "TỔNG", "lỗi"])]
    _critical = [l for l in _summary_lines if "❌" in l or "⚠️" in l]
    _clean    = [l for l in _summary_lines if "✅" in l or "🎉" in l]
    if _critical:
        print(f"[qa]  ⚠️  Phát hiện vấn đề:")
        for l in _critical[:10]:
            print(f"[qa]    {l.strip()}")
        print(f"[qa]  → Chạy đầy đủ: python \"{_qa_script}\"")
    else:
        print(f"[qa]  ✅ Tất cả files sạch — không có lỗi data")
