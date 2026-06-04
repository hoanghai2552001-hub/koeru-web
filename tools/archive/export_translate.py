import json, os, re

JS_FILE = r'C:\Users\hoang\Desktop\BUILD WEB KOERU\js\kanji-data.js'
OUT_DIR = r'C:\Users\hoang\Desktop\BUILD WEB KOERU\tools\translate'
os.makedirs(OUT_DIR, exist_ok=True)

with open(JS_FILE, encoding='utf-8') as f:
    content = f.read()

results = {'N5': [], 'N4': [], 'N3': [], 'N2': [], 'N1': []}

for line in content.split('\n'):
    if 'kanji:' not in line:
        continue

    km = re.search(r'kanji:"(.)"', line)
    if not km:
        continue
    kanji = km.group(1)

    lm = re.search(r'level:"(N[12345])"', line)
    if not lm:
        continue
    level = lm.group(1)

    # radical_en: 3rd segment of radical:"char|name_ja|meaning_en"
    radical_en = ''
    ri = line.find('radical:"')
    if ri >= 0:
        start = ri + len('radical:"')
        end = line.find('"', start)
        if end > start:
            segs = line[start:end].split('|')
            if len(segs) >= 3:
                radical_en = segs[2].strip()

    # mnemonic: parse char by char to handle escaped quotes
    mnemonic = ''
    mi = line.find('mnemonic:"')
    if mi >= 0:
        start = mi + len('mnemonic:"')
        i = start
        chars = []
        backslash = chr(92)
        while i < len(line):
            c = line[i]
            if c == backslash and i + 1 < len(line):
                chars.append(line[i + 1])
                i += 2
            elif c == '"':
                break
            else:
                chars.append(c)
                i += 1
        mnemonic = ''.join(chars)

    if not radical_en and not mnemonic:
        continue

    entry = {'k': kanji}
    if radical_en:
        entry['rad_en'] = radical_en
    if mnemonic:
        entry['mn_en'] = mnemonic

    if level in results:
        results[level].append(entry)

prompt_header = """Dịch các trường sau sang tiếng Việt tự nhiên:
- "rad_vi": nghĩa tiếng Việt của bộ thủ (rad_en) — ngắn gọn 1-3 từ
- "mn_vi": dịch mnemonic sang tiếng Việt, GIỮ NGUYÊN ký tự Kanji trong câu (女, 宀, 木...)

Trả về JSON array đúng format bên dưới, KHÔNG giải thích thêm.
Ví dụ output mẫu:
[
  {
    "k": "安",
    "rad_en": "roof, house",
    "rad_vi": "mái nhà",
    "mn_en": "When the woman 女 remains at home 宀.",
    "mn_vi": "Người phụ nữ 女 ở yên trong ngôi nhà 宀."
  }
]

===INPUT===
"""

total = 0
for level, entries in results.items():
    if not entries:
        continue
    with open(os.path.join(OUT_DIR, f'{level}_translate.json'), 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, f'{level}_prompt.txt'), 'w', encoding='utf-8') as f:
        f.write(prompt_header)
        json.dump(entries, f, ensure_ascii=False, indent=2)
    total += len(entries)
    print(f'{level}: {len(entries):>4} entries  →  {level}_prompt.txt')

print(f'\nTong: {total} entries')
print(f'Output: {OUT_DIR}')

# Sample check
s = results['N5'][0] if results['N5'] else {}
print('\nSample N5[0]:', json.dumps(s, ensure_ascii=False))
