import re
import csv

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

entry_re = re.compile(
    r'\{kanji:"([^"]*)",hanviet:"([^"]*)",on:"([^"]*)",kun:"([^"]*)",meaning:"([^"]*)",meaning_jp:"([^"]*)",level:"([^"]*)",words:\[(.*?)\]\}'
)
word_re = re.compile(r'\{"w": "([^"]*)", "r": "([^"]*)", "m": "([^"]*)"\}')

rows = []
for line in lines:
    line = line.strip()
    if not line.startswith('{kanji:'):
        continue
    m = entry_re.search(line)
    if not m:
        continue
    kanji, hanviet, on, kun, meaning, meaning_jp, level, words_raw = m.groups()
    words = word_re.findall(words_raw)

    row = {
        'kanji': kanji,
        'hanviet': hanviet,
        'on': on,
        'kun': kun,
        'meaning': meaning,
        'meaning_jp': meaning_jp,
        'level': level,
    }
    # Flatten up to 4 words
    for i in range(4):
        if i < len(words):
            row[f'w{i+1}'] = words[i][0]
            row[f'r{i+1}'] = words[i][1]
            row[f'm{i+1}'] = words[i][2]
        else:
            row[f'w{i+1}'] = ''
            row[f'r{i+1}'] = ''
            row[f'm{i+1}'] = ''
    rows.append(row)

headers = ['kanji','hanviet','on','kun','meaning','meaning_jp','level',
           'w1','r1','m1','w2','r2','m2','w3','r3','m3','w4','r4','m4']

with open('kanji_export.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f'✅ Exported {len(rows)} entries → kanji_export.csv')
