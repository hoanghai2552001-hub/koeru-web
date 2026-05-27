"""
gen_kanji_map_data.py
Tái tạo kanji-map-data.js từ kanji-data.js (1765 kanji đầy đủ).
Giữ nguyên phần vocab từ kanji-map-data.js cũ.
"""
import re, json, os

BASE = r'C:\Users\hoang\Desktop\BUILD WEB KOERU'
SRC  = os.path.join(BASE, 'js', 'kanji-data.js')
OLD  = os.path.join(BASE, 'kanji-map-data.js')
OUT  = os.path.join(BASE, 'kanji-map-data.js')

# ── helpers ───────────────────────────────────────────────────────────────
def get_str(line, field):
    m = re.search(r'(?<!\w)' + re.escape(field) + r':"((?:[^"\\]|\\.)*)"', line)
    return m.group(1).replace('\\"', '"') if m else ''

def get_num(line, field):
    m = re.search(r'(?<!\w)' + re.escape(field) + r':(\d+)', line)
    return int(m.group(1)) if m else 0

def get_array_str(line, field):
    m = re.search(r'(?<!\w)' + re.escape(field) + r':\[([^\]]*)\]', line)
    if not m: return []
    raw = m.group(1)
    return [x.strip().strip('"') for x in re.findall(r'"([^"]*)"', raw)]

# ── parse kanji-data.js ───────────────────────────────────────────────────
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

kanji_entries = []
radicals_dict = {}

for line in lines:
    if 'kanji:"' not in line:
        continue

    kanji    = get_str(line, 'kanji')
    hanviet  = get_str(line, 'hanviet')
    on_str   = get_str(line, 'on')
    kun_str  = get_str(line, 'kun')
    meaning  = get_str(line, 'meaning')
    level    = get_str(line, 'level')
    stroke   = get_num(line, 'stroke')
    freq_rank= get_num(line, 'freq_rank')
    grade    = get_num(line, 'grade')
    radical_str = get_str(line, 'radical')
    mnemonic = get_str(line, 'mnemonic')
    mn_vi    = get_str(line, 'mn_vi')
    parts    = get_array_str(line, 'parts')

    # radical pipe: char|name_ja|meaning_en|meaning_vi
    rad_char = ''
    if radical_str:
        segs = radical_str.split('|')
        rad_char      = segs[0] if len(segs) > 0 else ''
        rad_name_ja   = segs[1] if len(segs) > 1 else ''
        rad_meaning_en= segs[2] if len(segs) > 2 else ''
        rad_meaning_vi= segs[3] if len(segs) > 3 else ''
        if rad_char and rad_char not in radicals_dict:
            radicals_dict[rad_char] = {
                'name_ja': rad_name_ja,
                'meaning': rad_meaning_vi or rad_meaning_en,
                'meaning_en': rad_meaning_en,
            }

    # onyomi / kunyomi: split by 、 or comma
    def split_reading(s):
        if not s: return []
        return [x.strip() for x in re.split(r'[、,]', s) if x.strip()]

    entry = {
        'id':         kanji,
        'han_viet':   hanviet,
        'onyomi':     split_reading(on_str),
        'kunyomi':    split_reading(kun_str),
        'meaning':    meaning,
        'stroke':     stroke,
        'jlpt':       level,
        'status':     'reviewed',
        'radical':    rad_char,
        'components': parts,
        'freq_rank':  freq_rank if freq_rank else None,
        'grade':      grade if grade else None,
        'mnemonic':   mn_vi or mnemonic,   # ưu tiên tiếng Việt
        'mn_vi':      mn_vi,
    }
    if level in ('N5','N4','N3','N2'):   # N1 chưa triển khai
        kanji_entries.append(entry)

print(f'Parsed {len(kanji_entries)} kanji (N5–N2), {len(radicals_dict)} unique radicals')

# ── lấy phần vocab + relations từ kanji-map-data.js cũ ──────────────────
# Vocab và relations được giữ nguyên trong một file riêng để không bị mất
# khi chạy lại script. File vocab gốc: tools/kanji-map-vocab.js
VOCAB_FILE = os.path.join(BASE, 'tools', 'kanji-map-vocab.js')

if os.path.exists(VOCAB_FILE):
    with open(VOCAB_FILE, encoding='utf-8') as f:
        vocab_content = f.read()
    # trích vocab block — dùng bộ đếm ngoặc để xử lý nested arrays
    def extract_block(text, key):
        m = re.search(r'\b' + re.escape(key) + r'\s*:\s*\[', text)
        if not m: return key + ': []'
        start = m.end() - 1   # vị trí '[' mở
        depth = 0
        for i, c in enumerate(text[start:], start):
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return key + ': ' + text[start:i+1]
        return key + ': []'
    vocab_block    = extract_block(vocab_content, 'vocab')
    rel_block      = extract_block(vocab_content, 'kanji_relations')
else:
    print(f'WARNING: {VOCAB_FILE} không tồn tại — vocab sẽ rỗng')
    vocab_block = 'vocab: []'
    rel_block   = 'kanji_relations: []'

# ── viết JS entry ─────────────────────────────────────────────────────────
def js_str(s):
    if s is None: return 'null'
    return json.dumps(s, ensure_ascii=False)

def js_arr(arr):
    return '[' + ','.join(js_str(x) for x in arr) + ']'

def entry_to_js(e):
    parts = [
        f'id:{js_str(e["id"])}',
        f'han_viet:{js_str(e["han_viet"])}',
        f'onyomi:{js_arr(e["onyomi"])}',
        f'kunyomi:{js_arr(e["kunyomi"])}',
        f'meaning:{js_str(e["meaning"])}',
        f'stroke:{e["stroke"]}',
        f'jlpt:{js_str(e["jlpt"])}',
        f'status:"reviewed"',
        f'radical:{js_str(e["radical"])}',
        f'components:{js_arr(e["components"])}',
    ]
    if e['freq_rank']:
        parts.append(f'freq_rank:{e["freq_rank"]}')
    if e['grade']:
        parts.append(f'grade:{e["grade"]}')
    if e['mnemonic']:
        parts.append(f'mnemonic:{js_str(e["mnemonic"])}')
    if e['mn_vi']:
        parts.append(f'mn_vi:{js_str(e["mn_vi"])}')
    return '    { ' + ', '.join(parts) + ' }'

# ── radicals dict → JS ────────────────────────────────────────────────────
def radicals_to_js(d):
    lines = []
    for char, v in d.items():
        entry = (f'    {js_str(char)}: '
                 f'{{ name_ja:{js_str(v["name_ja"])}, '
                 f'meaning:{js_str(v["meaning"])}, '
                 f'meaning_en:{js_str(v["meaning_en"])} }}')
        lines.append(entry)
    return ',\n'.join(lines)

# ── assemble output ───────────────────────────────────────────────────────
kanji_block = ',\n'.join(entry_to_js(e) for e in kanji_entries)
radicals_block = radicals_to_js(radicals_dict)

output = f"""// kanji-map-data.js — auto-generated from kanji-data.js
// Total: {len(kanji_entries)} kanji (N5-N1)
// Run: python tools/gen_kanji_map_data.py

window.KANJI_DATA = {{
  kanji: [
{kanji_block}
  ],

  {vocab_block},

  {rel_block},

  radicals: {{
{radicals_block}
  }}
}};
"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Written {OUT}')
print(f'File size: {os.path.getsize(OUT) // 1024} KB')

# sample check
samples = ['安','力','腕','恩','夢']
for s in samples:
    e = next((x for x in kanji_entries if x['id'] == s), None)
    if e:
        print(f'  {s}: radical={e["radical"]}, mn_vi={"✅" if e["mn_vi"] else "❌"}, mnemonic={e["mnemonic"][:30] if e["mnemonic"] else "—"}')
