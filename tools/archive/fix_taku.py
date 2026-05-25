with open('../js/kanji-data.js', encoding='utf-8') as f:
    t = f.read()
old = '"r":"帰宅","m":"về nhà"'
new = '"r":"おたく","m":"về nhà"'
if old in t:
    t = t.replace(old, new)
    with open('../js/kanji-data.js', 'w', encoding='utf-8') as f:
        f.write(t)
    print('Fixed 宅 reading: 帰宅 → おたく')
else:
    print('Not found:', repr(old))
