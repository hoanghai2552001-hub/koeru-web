"""Patch: fix wrong translations + restore deleted words for N5/N4."""
import re, json

path = 'js/kanji-data.js'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. Fix wrong inline translations
content = content.replace(
    '{"w":"黒海","r":"こっかい","m":"màu đen"}',
    '{"w":"黒海","r":"こっかい","m":"Biển Đen"}'
)
content = content.replace(
    '{"w":"黒衣","r":"こくい","m":"màu đen"}',
    '{"w":"黒衣","r":"こくい","m":"quần áo đen"}'
)
print('Fixed: 黒海→Biển Đen, 黒衣→quần áo đen')

# 2. Restore deleted words
RESTORE = {
    '走': [('走塁', 'そうるい', 'chạy vượt gốc (bóng chày)'), ('競走馬', 'きょうそうば', 'ngựa đua')],
    '近': [('近衛', 'このえ', 'Cận vệ Hoàng gia'), ('近東', 'きんとう', 'Cận Đông')],
    '始': [('原始人', 'げんしじん', 'người nguyên thủy')],
    '門': [('専門医', 'せんもんい', 'bác sĩ chuyên khoa')],
    '待': [('招待', 'しょうたい', 'lời mời, chiêu đãi')],
    '送': [('民間放送', 'みんかんほうそう', 'phát thanh thương mại'),
           ('配送', 'はいそう', 'giao hàng'),
           ('直送', 'ちょくそう', 'giao thẳng')],
    '海': [('北極海', 'ほっきょくかい', 'Bắc Băng Dương')],
    '軽': [('軽金属', 'けいきんぞく', 'kim loại nhẹ')],
    '暑': [('猛暑', 'もうしょ', 'nắng nóng gay gắt'), ('炎暑', 'えんしょ', 'oi bức, nóng bức')],
    '遠': [('遠心力', 'えんしんりょく', 'lực ly tâm'), ('遠心', 'えんしん', 'ly tâm')],
    '漢': [('羅漢', 'らかん', 'La Hán (A-la-hán)')],
    '試': [('入学試験', 'にゅうがくしけん', 'kỳ thi tuyển sinh'),
           ('入試', 'にゅうし', 'thi đầu vào'),
           ('完全試合', 'かんぜんじあい', 'trận đấu hoàn hảo')],
    '頭': [('番頭', 'ばんとう', 'trưởng quầy, quản lý cửa hàng')],
}

def dict_to_js(obj):
    fields = ['kanji','hanviet','on','kun','meaning','meaning_jp','level','strokes','words']
    parts = []
    for key in fields:
        if key not in obj: continue
        val = obj[key]
        if isinstance(val, str):
            esc = val.replace('\\', '\\\\').replace('"', '\\"')
            parts.append(f'{key}:"{esc}"')
        elif isinstance(val, list):
            parts.append(f'{key}:{json.dumps(val, ensure_ascii=False, separators=(",",":"))}')
        elif isinstance(val, (int, float)):
            parts.append(f'{key}:{val}')
    return '{' + ','.join(parts) + '}'

# Parse and patch
restored = 0
lines = content.splitlines()
new_lines = []
for line in lines:
    s = line.strip().rstrip(',')
    if s.startswith('{kanji:'):
        try:
            j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', s)
            obj = json.loads(j)
            k = obj.get('kanji', '')
            if k in RESTORE:
                existing = {w['w'] for w in obj.get('words', [])}
                added = []
                for w, r, m in RESTORE[k]:
                    if w not in existing:
                        obj.setdefault('words', []).append({'w': w, 'r': r, 'm': m})
                        added.append(w)
                        restored += 1
                if added:
                    trailing = ',' if line.strip().endswith(',') else ''
                    line = dict_to_js(obj) + trailing
                    print(f'  [{k}] +{added}')
        except:
            pass
    new_lines.append(line)

content = '\n'.join(new_lines)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone: restored {restored} words')
