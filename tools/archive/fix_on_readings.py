"""
KOERU — Fix on-readings: convert hiragana → katakana
99 kanji có on reading sai dạng hiragana, cần convert sang katakana
"""
import re
from pathlib import Path

JS_DIR = Path(__file__).parent.parent / "js"

def to_katakana(s):
    return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ん' else c for c in s)

def is_hiragana_heavy(s):
    return any('ぁ' <= c <= 'ん' for c in s)

total = 0

for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
    path = JS_DIR / f"kanji-data-{lv}.js"
    content = path.read_text(encoding='utf-8')
    count = 0

    def fix_on(m):
        global count, total
        on_val = m.group(1)
        if is_hiragana_heavy(on_val):
            fixed = to_katakana(on_val)
            count += 1
            total += 1
            return m.group(0).replace(on_val, fixed)
        return m.group(0)

    new_content = re.sub(r'on\s*:\s*"([^"]+)"', fix_on, content)
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        print(f"  {lv.upper()}: {count} on-readings fixed")
    else:
        print(f"  {lv.upper()}: ✅ sạch")

print(f"\nTổng: {total} on-readings chuyển sang katakana")

# Rebuild kanji-data.js
print("Rebuilding kanji-data.js...")
parts = []
for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
    c = (JS_DIR / f"kanji-data-{lv}.js").read_text(encoding='utf-8')
    start = c.index('[')
    end = c.rindex(']') + 1
    inner = c[start+1:end-1].strip().rstrip(',')
    if inner:
        parts.append(inner)

combined = 'window.KANJI_DATA = [\n' + ',\n'.join(parts) + '\n];\n'
(JS_DIR / 'kanji-data.js').write_text(combined, encoding='utf-8')
print("Done!")
