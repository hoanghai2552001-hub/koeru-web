"""
Parse Excel 512 Kanji → từ ghép tiếng Việt
Merge vào kanji-data.js (ưu tiên Excel, fallback KanjiAPI đã inject)

Format Excel (sheet FORM KANJI):
Row N:   [idx, kanji, '訓', kun_reading, compound1, compound2, compound3, 'kanji\nHANVIET: nghĩa']
Row N+1: [reading1, reading2, reading3]
Row N+2: [nghĩa_VN1, nghĩa_VN2, nghĩa_VN3]
Row N+3: ['音', on_reading, compound1, compound2, compound3]
Row N+4: [reading1, reading2, reading3]
Row N+5: [nghĩa_VN1, nghĩa_VN2, nghĩa_VN3]

Chạy: python build_compounds_excel.py
"""
import re, json, openpyxl, os, warnings
warnings.filterwarnings('ignore')

BASE     = os.path.dirname(os.path.abspath(__file__))
XLS      = os.path.join(BASE, "input", "excel", "HÁN TỰ 512KANJI LOOK & LEARN NGỌC SOẠN.xlsx")
DATA_JS  = os.path.join(BASE, "js", "kanji-data.js")

def to_hiragana(s):
    return "".join(chr(ord(c)-0x60) if 'ァ'<=c<='ヶ' else c for c in (s or ""))

def clean(s):
    if s is None: return ""
    return str(s).replace('\n',' ').strip()

def is_kanji_word(s):
    """Có ít nhất 1 CJK character"""
    return bool(s) and any('一'<=c<='鿿' or '㐀'<=c<='䶿' for c in s)

def parse_excel():
    """
    Trả về dict: {kanji: [{w, r, m}, ...]}
    Tối đa 3 từ ghép mỗi kanji, ưu tiên âm On (thường dùng hơn)
    """
    wb = openpyxl.load_workbook(XLS)
    ws = wb['FORM KANJI']

    # Đọc tất cả rows có dữ liệu vào list
    rows = []
    for row in ws.iter_rows(values_only=True):
        non_null = [v for v in row if v is not None]
        rows.append(row)

    result = {}
    i = 0
    total_rows = len(rows)

    while i < total_rows:
        row = rows[i]
        cells = [v for v in row if v is not None]

        # Phát hiện row kanji chính: cell[0] là số, cell[1] là kanji
        if (len(cells) >= 2 and
            isinstance(cells[0], (int, float)) and
            isinstance(cells[1], str) and
            len(cells[1]) == 1 and
            is_kanji_word(cells[1])):

            kanji = cells[1]
            words = []

            # Parse block 7 rows cho mỗi kanji (訓 block + 音 block)
            # Row i:   idx, kanji, '訓', kun_r, word1, word2, word3, ...
            # Row i+1: reading1, reading2, reading3
            # Row i+2: meaning1, meaning2, meaning3
            # Row i+3: '音', on_r, word1, word2, word3
            # Row i+4: reading1, reading2, reading3
            # Row i+5: meaning1, meaning2, meaning3

            # Ưu tiên âm On (row i+3..i+5) vì thường dùng hơn trong văn viết
            for block_start, is_on in [(i+3, True), (i, False)]:
                if block_start + 2 >= total_rows: continue
                r0 = [clean(v) for v in rows[block_start] if v is not None]
                r1 = [clean(v) for v in rows[block_start+1] if v is not None]
                r2 = [clean(v) for v in rows[block_start+2] if v is not None]

                if not r0: continue

                # r0: ['音'/'訓', on/kun_reading, kanji_itself?, word1, word2, ...]
                # r1: [kanji_reading, word1_reading, word2_reading, ...]
                # r2: [kanji_meaning, word1_meaning, word2_meaning, ...]
                # → Index 0 trong r1/r2 là của chính kanji, word thứ j dùng r1[j+1], r2[j+1]

                # Lọc compound words từ r0 (bỏ '音'/'訓', on/kun reading, single-char)
                compounds = []
                for v in r0[2:]:  # skip '音'/'訓' và reading
                    if v and is_kanji_word(v) and kanji in v and 2 <= len(v) <= 4:
                        compounds.append(v)

                for j, word in enumerate(compounds[:3]):
                    idx = j + 1  # offset: index 0 = kanji itself
                    reading = r1[idx] if idx < len(r1) else ""
                    meaning = r2[idx] if idx < len(r2) else ""
                    reading = to_hiragana(reading.split('\n')[0].strip())
                    meaning = meaning.split('\n')[0].split('/')[0].strip()
                    # Bỏ dấu ngoặc thừa
                    meaning = re.sub(r'^\s*[\(（].*?[\)）]\s*', '', meaning).strip()
                    if not reading or not meaning: continue
                    if not any(w['w'] == word for w in words):
                        words.append({"w": word, "r": reading, "m": meaning})
                    if len(words) >= 3: break

                if len(words) >= 3: break

            if words:
                result[kanji] = words[:3]

        i += 1

    return result

def inject_into_js(excel_map):
    """Merge excel_map vào kanji-data.js, ưu tiên Excel > API"""
    with open(DATA_JS, encoding='utf-8') as f:
        txt = f.read()

    replaced = 0

    def replacer(m):
        nonlocal replaced
        entry = m.group(0)
        km = re.search(r'kanji:"([^"]+)"', entry)
        if not km: return entry
        k = km.group(1)

        if k in excel_map:
            # Xóa words cũ nếu có
            entry = re.sub(r',words:\[[^\]]*\]', '', entry)
            entry = entry.rstrip('} \t\n') + f',words:{json.dumps(excel_map[k], ensure_ascii=False)}' + '}'
            replaced += 1

        return entry

    # Match each entry — stop at },{ or end of array (level-aware)
    new_txt = re.sub(r'\{kanji:"[^"]+?"(?:[^{}]|\{[^}]*\})*\}', replacer, txt)

    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(new_txt)

    return replaced

def main():
    print("=== Build Compounds from Excel ===")
    print("Parsing Excel...")
    excel_map = parse_excel()
    print(f"  Found {len(excel_map)} kanji with compounds from Excel")

    # Sample
    for k in list(excel_map.keys())[:5]:
        print(f"  {k}: {excel_map[k]}")

    print("Injecting into kanji-data.js (Excel overrides API)...")
    n = inject_into_js(excel_map)
    print(f"  Updated {n} entries with Excel data")

    # Count total words
    with open(DATA_JS, encoding='utf-8') as f:
        txt = f.read()
    total = txt.count('words:')
    print(f"  Total entries with words: {total}/1765")
    print("Done!")

if __name__ == "__main__":
    main()
