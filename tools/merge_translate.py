import json, os, re

JS_FILE = r'C:\Users\hoang\Desktop\BUILD WEB KOERU\js\kanji-data.js'

# Load translated files (key: kanji char -> {rad_vi, mn_vi})
trans_map = {}

files = [
    r'C:\Users\hoang\Desktop\BUILD WEB KOERU\N4_translated.json',
    r'C:\Users\hoang\Desktop\BUILD WEB KOERU\N3_translated.json',
    r'C:\Users\hoang\Desktop\BUILD WEB KOERU\N2_translated.json',
    r'C:\Users\hoang\Desktop\BUILD WEB KOERU\N1_translated.json',
]

for fpath in files:
    if not os.path.exists(fpath):
        continue
    data = json.load(open(fpath, encoding='utf-8'))
    for e in data:
        k = e.get('k', '')
        if k:
            trans_map[k] = {
                'rad_vi': e.get('rad_vi', ''),
                'mn_vi':  e.get('mn_vi',  ''),
            }

print(f'Loaded translations for {len(trans_map)} kanji')

with open(JS_FILE, encoding='utf-8') as f:
    content = f.read()

def update_line(line):
    km = re.search(r'kanji:"(.)"', line)
    if not km:
        return line
    kanji = km.group(1)
    if kanji not in trans_map:
        return line

    t = trans_map[kanji]
    rad_vi = t.get('rad_vi', '').strip()
    mn_vi  = t.get('mn_vi',  '').strip()

    fields = []

    # Update radical: "char|name_ja|en" → "char|name_ja|en|vi"
    if rad_vi:
        ri = line.find('radical:"')
        if ri >= 0:
            start = ri + len('radical:"')
            end = line.find('"', start)
            if end > start:
                current = line[start:end]
                segs = current.split('|')
                # Chỉ thêm nếu chưa có segment thứ 4
                if len(segs) == 3:
                    new_val = current + '|' + rad_vi.replace('"', '\\"')
                    line = line[:start] + new_val + line[end:]

    # Add mn_vi nếu chưa có
    if mn_vi and 'mn_vi:' not in line:
        mn_vi_clean = mn_vi.replace('"', '\\"').replace('\n', ' ')
        inject = f',mn_vi:"{mn_vi_clean}"'
        stripped = line.rstrip()
        if stripped.endswith('},'):
            line = stripped[:-2] + inject + '},'
        elif stripped.endswith('}'):
            line = stripped[:-1] + inject + '}'

    return line

lines = content.split('\n')
new_lines = [update_line(l) for l in lines]
changed = sum(1 for a, b in zip(lines, new_lines) if a != b)

new_content = '\n'.join(new_lines)
with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'Updated {changed} entries in kanji-data.js')

# Sample check
for char in ['力', '化', '腕', '恩']:
    sample = [l for l in new_lines if f'kanji:"{char}"' in l]
    if sample:
        line = sample[0]
        rv = re.search(r'radical:"([^"]*)"', line)
        mv = re.search(r'mn_vi:"', line)
        rad_val = rv.group(1) if rv else ''
        print(f'  {char}: radical={rad_val[:40]}... | mn_vi={"✅" if mv else "❌"}')
