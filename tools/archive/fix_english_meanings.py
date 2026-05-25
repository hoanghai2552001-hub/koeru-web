"""
fix_english_meanings.py — Dịch nghĩa tiếng Anh còn sót trong words[].m sang tiếng Việt

Chiến lược:
  1. Đọc qa_report.json lấy danh sách từ bị lỗi
  2. Với mỗi từ có nghĩa EN: gọi Jisho để lấy nghĩa JP → dịch qua bảng EN→VI
  3. Nếu không dịch được → xoá entry đó khỏi words (rollback nếu còn < 1)
  4. Ghi lại kanji-data.js

Chạy: python fix_english_meanings.py
"""

import re, json, os, sys, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Bảng EN→VI cho các nghĩa phổ biến ────────────────────────────────────────
EN_VI = {
    # Thường gặp nhất
    "last year": "năm ngoái",
    "this year": "năm nay",
    "next year": "năm sau",
    "last month": "tháng trước",
    "next month": "tháng sau",
    "last week": "tuần trước",
    "next week": "tuần sau",
    "fountain pen": "bút máy",
    "measuring ruler": "thước kẻ",
    "ruler": "thước kẻ",
    "compass": "compa",
    "double feature": "chiếu hai phim liên tiếp",
    "double exposure": "phơi sáng kép",
    "power of imagination": "sức tưởng tượng",
    "imagination": "trí tưởng tượng",
    "agriculture and industry": "nông nghiệp và công nghiệp",
    "towns and villages": "thị trấn và làng xã",
    "low profile": "thái độ khiêm tốn, giữ thái độ thấp",
    "association formed to carry out an objective": "liên minh thực hiện mục tiêu",
    "20 percent": "20 phần trăm",
    "ecuador": "Ecuador",
    "absolute majority": "đa số tuyệt đối",
    "diversification": "đa dạng hóa",
    "arc": "cung tròn",
    "1000 yen": "1000 yên",
    "all means": "mọi phương tiện",
    "paying a great deal of attention": "chú ý nhiều, quan tâm",
    "paying great attention": "chú ý nhiều",
    "jupiter": "sao Mộc",
    "planet": "hành tinh",
    "spindletree": "cây vệ mao",
    "hornbeam": "cây thùa",
    "bookshelf": "kệ sách",
    "construction": "xây dựng, kiến thiết",
    "cross for crucifixion": "cây thánh giá",
    "cross": "chữ thập, thánh giá",
    "finely chopped": "thái nhỏ, băm nhỏ",
    "microscope": "kính hiển vi",
    "microscopic": "nhỏ li ti, vi mô",
    "universal": "phổ quát, toàn cầu",
    "heresy": "tà thuyết, dị giáo",
    "approval": "sự chấp thuận",
    "national policy": "chính sách quốc gia",
    "right or wrong": "đúng hay sai",
    "opening of hostilities": "mở đầu chiến sự",
    "northern extremity": "đầu phía bắc",
    "exemplary": "mẫu mực, điển hình",
    "normal school": "trường sư phạm",
    "extensive": "rộng rãi, phạm vi rộng",
    "resuscitation": "hồi sức, cứu hộ",
    "living": "sinh sống, cuộc sống",
    "lively": "sôi nổi, năng động",
    "being helped": "được giúp đỡ",
    "towns and villages": "thị trấn và làng xã",
    "association": "hiệp hội",
    "agriculture": "nông nghiệp",
    "industry": "công nghiệp",
    # Số
    "20 percent": "20%",
    "30 percent": "30%",
    "50 percent": "50%",
}

HEADERS = {"User-Agent": "KoeruApp/1.0"}
_word_cache = {}

def fetch_jisho(word):
    if word in _word_cache: return _word_cache[word]
    url = "https://jisho.org/api/v1/search/words?keyword=" + urllib.parse.quote(word)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode()).get("data", [])
        for item in data:
            for jp in item.get("japanese", []):
                if jp.get("word") == word:
                    senses = item.get("senses", [])
                    en_defs = [d for s in senses for d in s.get("english_definitions", [])]
                    _word_cache[word] = en_defs
                    return en_defs
        if data:
            senses = data[0].get("senses", [])
            en_defs = [d for s in senses for d in s.get("english_definitions", [])]
            _word_cache[word] = en_defs
            return en_defs
    except: pass
    _word_cache[word] = []
    return []

def translate_en_to_vi(en_text):
    """Dịch chuỗi tiếng Anh sang tiếng Việt qua bảng EN_VI."""
    t = en_text.strip().lower()
    # Khớp chính xác
    if t in EN_VI: return EN_VI[t]
    # Khớp partial (loại bỏ nội dung trong ngoặc)
    t_clean = re.sub(r'\(.*?\)', '', t).strip()
    if t_clean in EN_VI: return EN_VI[t_clean]
    # Thử từng key theo độ dài giảm dần
    for k, v in sorted(EN_VI.items(), key=lambda x: -len(x[0])):
        if k in t_clean: return v
    return None

def is_english(s):
    if not s: return False
    # Có dấu VN hoặc ký tự JP → không phải EN
    if re.search(r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]', s): return False
    if re.search(r'[぀-ヿ一-鿿]', s): return False
    # Chỉ Latin
    if not re.match(r'^[a-zA-Z\s\-\(\)\/\.,\'\"0-9]+$', s.strip()): return False
    if len(s.strip()) <= 4: return False
    s2 = s.strip().lower()
    if s2 in {'hoa','mua','hai','ba','mot','tay','mat','tai','chan','bung','lung','vai','an','di','ve'}: return False
    EN_MARKERS = {
        'the','a','an','of','in','on','at','to','for','with','by','from','and','or',
        'not','is','are','was','were','be','been','have','has','that','this','which',
        'one','two','three','four','five','six','seven','eight','nine','ten',
        'person','people','thing','place','time','way','day','year','make','take',
        'get','go','come','see','know','think','look','good','bad','big','small',
        'large','new','old','high','low','national','general','special','main',
        'local','original','school','university','company','government','family',
        'opening','closing','finely','chopped','microscopic','extensive','exemplary',
        'universal','heresy','hornbeam','bookshelf','construction','crucifixion',
        'sumo','fountain','pen','measuring','ruler','jupiter','planet','spindletree',
        'approval','policy','hostilities','northern','extremity','absolute','majority',
        'diversification','imagination','agriculture','industry','profile','towns',
        'villages','percent','feature','double','exposure','association','resuscitation',
        'living','lively','helped','paying','attention','formed','carry','objective',
        'last','next','this','month','week','profile',
    }
    words_list = re.split(r'[\s\(\)\-\/,\.]+', s2)
    words_list = [w for w in words_list if w]
    if any(w in EN_MARKERS for w in words_list): return True
    if len(words_list) >= 3: return True
    return False

# ── Parse JS ──────────────────────────────────────────────────────────────────
def parse_kanji_js(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries, structure = [], []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith('// ====='):
            structure.append({'_comment': line})
            entries.append(None)
        elif s.startswith('{kanji:'):
            s2 = s.rstrip(',')
            try:
                j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', s2)
                obj = json.loads(j)
                structure.append(obj)
                entries.append(obj)
            except:
                structure.append({'_raw': s})
                entries.append(None)
    header_end = content.index('const ALL_KANJI = [')
    footer_start = content.rindex('];') + 2
    return (structure,
            content[:header_end],
            content[footer_start:])

def dict_to_js_line(obj):
    fields = ['kanji','hanviet','on','kun','meaning','meaning_jp','level','strokes','words']
    parts = []
    for key in fields:
        if key not in obj: continue
        val = obj[key]
        if isinstance(val, str):
            escaped = val.replace('\\','\\\\').replace('"','\\"')
            parts.append(f'{key}:"{escaped}"')
        elif isinstance(val, list):
            arr_str = json.dumps(val, ensure_ascii=False, separators=(',',':'))
            parts.append(f'{key}:{arr_str}')
        elif isinstance(val, (int,float)):
            parts.append(f'{key}:{val}')
        elif val is None:
            continue
    return '{' + ','.join(parts) + '}'

def write_js(path, structure, header, footer):
    lines = []
    for item in structure:
        if '_comment' in item:
            lines.append(item['_comment'])
        elif '_raw' in item:
            lines.append(item['_raw'] + ',')
        else:
            lines.append(dict_to_js_line(item) + ',')
    if lines and lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + 'const ALL_KANJI = [\n' + '\n'.join(lines) + '\n];' + footer)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    js_path = os.path.join(BASE, 'js', 'kanji-data.js')
    print('📂 Đọc kanji-data.js...')
    structure, header, footer = parse_kanji_js(js_path)

    fixed_count = 0
    removed_count = 0
    untranslated = []

    kanji_objs = [x for x in structure if x and '_comment' not in x and '_raw' not in x]
    print(f'   {len(kanji_objs)} kanji\n')

    for obj in kanji_objs:
        k = obj.get('kanji','?')
        words = obj.get('words', [])
        new_words = []
        changed = False

        for w in words:
            wm = w.get('m','')
            if is_english(wm):
                # Thử dịch qua bảng
                vi = translate_en_to_vi(wm)
                if vi:
                    new_w = dict(w)
                    new_w['m'] = vi
                    new_words.append(new_w)
                    print(f'  [{k}] "{w["w"]}": "{wm}" → "{vi}"')
                    fixed_count += 1
                    changed = True
                else:
                    # Thử lấy nghĩa từ Jisho
                    en_defs = fetch_jisho(w.get('w',''))
                    time.sleep(0.15)
                    # Nếu Jisho trả về rồi thử dịch lại
                    translated = None
                    for d in en_defs[:3]:
                        translated = translate_en_to_vi(d)
                        if translated: break
                    if translated:
                        new_w = dict(w)
                        new_w['m'] = translated
                        new_words.append(new_w)
                        print(f'  [{k}] "{w["w"]}": "{wm}" → "{translated}" (via Jisho)')
                        fixed_count += 1
                        changed = True
                    else:
                        # Không dịch được → xoá entry
                        removed_count += 1
                        changed = True
                        untranslated.append(f'{k}: {w.get("w","")} = "{wm}"')
            else:
                new_words.append(w)

        if changed:
            # Rollback nếu sau khi sửa/xoá còn lại ít hơn 1
            if len(new_words) < 1 and len(words) > 0:
                pass  # giữ nguyên obj
            else:
                obj['words'] = new_words

    # Ghi file
    write_js(js_path, structure, header, footer)
    print(f'\n✅ Đã sửa {fixed_count} nghĩa, xoá {removed_count} entry không dịch được')
    print(f'💾 Đã ghi → {js_path}')

    if untranslated:
        log = os.path.join(BASE, 'untranslated.log')
        with open(log, 'w', encoding='utf-8') as f:
            f.write('\n'.join(untranslated))
        print(f'📋 {len(untranslated)} từ chưa dịch được → {log}')

if __name__ == '__main__':
    main()
