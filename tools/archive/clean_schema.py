"""
clean_schema.py — Xóa field rác KHỎI schema (xử lý ĐÚNG escaped quotes)
Khác build_unified_db cũ: dùng char-by-char scanner thay vì regex naive
để không làm hỏng data khi value chứa \"
"""
import re, json
from pathlib import Path

JS = Path(__file__).parent.parent / "js"
REMOVE = {'meaning_jp', 'meaning_en', 'mnemonic', 'mn_vi'}
KEEP_ORDER = ['kanji', 'hanviet', 'on', 'kun', 'meaning', 'level',
              'words', 'stroke', 'freq_rank', 'grade', 'radical', 'parts']


def parse_entry(s):
    """
    Parse một entry JS literal {key:value,...} → dict (giữ thứ tự).
    Xử lý đúng: chuỗi có \" escape, array [...], số, key không quote.
    Trả về list[(key, raw_value_string)] để giữ nguyên format value.
    """
    assert s[0] == '{'
    i = 1
    n = len(s)
    fields = []
    while i < n:
        # Skip whitespace/comma
        while i < n and s[i] in ' ,\n\t':
            i += 1
        if i >= n or s[i] == '}':
            break
        # Read key (until ':')
        key_start = i
        while i < n and s[i] != ':':
            i += 1
        key = s[key_start:i].strip().strip('"')
        i += 1  # skip ':'
        # Skip whitespace
        while i < n and s[i] in ' \n\t':
            i += 1
        # Read value
        val_start = i
        if s[i] == '"':
            # String — handle escaped quotes
            i += 1
            while i < n:
                if s[i] == '\\':
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
        elif s[i] == '[':
            # Array — track depth, handle strings inside
            depth = 0
            while i < n:
                c = s[i]
                if c == '"':
                    i += 1
                    while i < n:
                        if s[i] == '\\':
                            i += 2; continue
                        if s[i] == '"':
                            break
                        i += 1
                elif c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
        elif s[i] == '{':
            depth = 0
            while i < n:
                c = s[i]
                if c == '"':
                    i += 1
                    while i < n:
                        if s[i] == '\\':
                            i += 2; continue
                        if s[i] == '"':
                            break
                        i += 1
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
        else:
            # Number / bool / null — until , or }
            while i < n and s[i] not in ',}':
                i += 1
        val = s[val_start:i].strip()
        fields.append((key, val))
    return fields


def rebuild_entry(fields):
    """Dựng lại entry từ list[(key,val)], chỉ giữ field cần, theo thứ tự chuẩn."""
    kept = {k: v for k, v in fields if k not in REMOVE}
    # Sắp xếp theo KEEP_ORDER, field lạ để cuối
    ordered = []
    for k in KEEP_ORDER:
        if k in kept:
            ordered.append(f'{k}:{kept[k]}')
    for k, v in kept.items():
        if k not in KEEP_ORDER:
            ordered.append(f'{k}:{v}')
    return '{' + ','.join(ordered) + '}'


def process_file(path):
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()
    out_lines = []
    fixed = 0
    for line in lines:
        stripped = line.strip()
        trailing_comma = stripped.endswith(',')
        core = stripped.rstrip(',')
        if core.startswith('{kanji:'):
            try:
                fields = parse_entry(core)
                rebuilt = rebuild_entry(fields)
                # Validate rebuilt parses as JSON
                j = re.sub(r'(?<![\\"\w])([a-zA-Z_]\w*)(?=\s*:)', r'"\1"', rebuilt)
                json.loads(j)  # raises if invalid
                out_lines.append(rebuilt + (',' if trailing_comma else ''))
                fixed += 1
            except Exception as e:
                # Keep original if parse fails (safety)
                out_lines.append(line)
                m = re.search(r'kanji:"([^"]+)"', core)
                print(f"  ⚠️ {path.name}: giữ nguyên {m.group(1) if m else '?'} — {str(e)[:50]}")
        else:
            out_lines.append(line)
    path.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    return fixed


def main():
    total = 0
    for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
        path = JS / f"kanji-data-{lv}.js"
        n = process_file(path)
        total += n
        print(f"  {lv.upper()}: {n} entries cleaned")
    print(f"\nTổng: {total} entries")

    # Rebuild combined
    parts = []
    for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
        c = (JS / f"kanji-data-{lv}.js").read_text(encoding='utf-8')
        start = c.index('[')
        end = c.rindex(']') + 1
        inner = c[start+1:end-1].strip().rstrip(',')
        if inner:
            parts.append(inner)
    combined = 'window.KANJI_DATA = [\n' + ',\n'.join(parts) + '\n];\n'
    (JS / 'kanji-data.js').write_text(combined, encoding='utf-8')
    print("kanji-data.js rebuilt")


if __name__ == '__main__':
    main()
