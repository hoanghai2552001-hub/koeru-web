"""
fix_n5n4.py — Sửa sạch N5/N4: dịch nghĩa EN, điền thiếu qua API
"""
import re, json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
JS_PATH = os.path.join(BASE, 'js', 'kanji-data.js')
HEADERS = {"User-Agent": "KoeruApp/1.0"}

# Bảng dịch trực tiếp cho N5/N4
DIRECT = {
    "1000 yen": "1000 yên",
    "(paying) a great deal of attention (to)": "chú ý rất nhiều",
    "(paying) a great deal of attention": "chú ý rất nhiều",
    "paying a great deal of attention": "chú ý rất nhiều",
    "-nth time": "lần thứ N",
    "corner of one's eye": "đuôi mắt",
    "all means": "mọi phương tiện",
    "kaleidoscope": "kính vạn hoa",
    "ecuador": "Ecuador",
    "Ecuador": "Ecuador",
    "(artificial) dialysis": "thẩm phân nhân tạo",
    "dialysis": "thẩm phân",
    "classmate": "bạn cùng lớp",
    "community chest": "quỹ từ thiện cộng đồng",
    "fishing village": "làng chài",
    "mountain village": "làng miền núi",
    "apprentice": "học việc, thực tập sinh",
    "cousin (male)": "anh/em họ (nam)",
    "cousin": "anh/em họ",
    "batting power": "sức đánh bóng",
    "batting": "đánh bóng",
    # Thêm từ danh sách N5/N4
    "1 yen coin": "đồng xu 1 yên",
    "10 yen coin": "đồng xu 10 yên",
    "100 yen coin": "đồng xu 100 yên",
    "1000 yen bill": "tờ 1000 yên",
    "round trip": "khứ hồi",
    "one-way": "một chiều",
    "opening": "khai mạc, mở đầu",
    "living national treasure": "báu vật quốc gia sống",
    "national treasure": "báu vật quốc gia",
    "light industry": "công nghiệp nhẹ",
    "heavy industry": "công nghiệp nặng",
    "prefectural": "thuộc tỉnh",
    "native of a prefecture": "người bản địa của tỉnh",
    "association of people from the same prefecture": "hội đồng hương tỉnh",
    "(under) prefectural management": "thuộc quản lý tỉnh",
    "prefectural management": "quản lý tỉnh",
    "prefectural assembly": "hội đồng tỉnh",
    "member of a prefectural assembly": "thành viên hội đồng tỉnh",
    "coming and going": "qua lại, đến và đi",
    "to consign to oblivion": "đưa vào quên lãng",
    "entry in a race": "xuất phát trong cuộc đua",
    "beginning of the month": "đầu tháng",
    "ceremonial first pitch": "ném bóng khai mạc nghi lễ",
    "new year's pine decoration": "trang trí thông năm mới",
    "New Year's pine decoration": "trang trí thông năm mới",
    "pine decoration": "trang trí thông",
    "to keep (a person) waiting": "bắt (ai đó) chờ",
    "kinki": "vùng Kinki (Osaka, Kyoto, Nara)",
    "kinki (region around osaka, kyoto, nara)": "vùng Kinki (Osaka, Kyoto, Nara)",
    "(russian) maritime provinces": "vùng duyên hải Nga",
    "black (colour, color)": "màu đen",
    "black": "màu đen",
    "heat (of the weather)": "nóng bức (thời tiết)",
    "coming from far away": "đến từ xa",
    "chinese herbal medicine": "thuốc đông y Trung Quốc",
    "chinese person (esp. han chinese)": "người Trung Quốc (đặc biệt là người Hán)",
    "(on the) street": "trên đường phố",
    "street": "đường phố",
    "beginning (of a century, etc.)": "đầu (thế kỷ, v.v.)",
    "beginning": "khởi đầu",
    "arrangement of stones in a garden": "sắp xếp đá trong vườn",
    "appointments and dismissal": "bổ nhiệm và miễn nhiệm",
    "low blood pressure": "huyết áp thấp",
    "low frequency": "tần số thấp",
    "biological younger brother": "em trai ruột",
    "biological": "ruột thịt, sinh học",
    "light machine gun": "súng máy hạng nhẹ",
    "chim non,  chim con": "chim non, chim con",
    "dairy industry": "ngành công nghiệp sữa",
    "ministry of construction": "Bộ Xây dựng",
    "Ministry of Construction": "Bộ Xây dựng",
    "minister of agriculture": "Bộ trưởng Nông nghiệp",
    "Minister of Agriculture": "Bộ trưởng Nông nghiệp",
    "(science of) agriculture": "khoa học nông nghiệp",
    "commerce and industry": "thương mại và công nghiệp",
    "agriculture and horticulture": "nông nghiệp và làm vườn",
    "(encouragement of) industry": "khuyến khích công nghiệp",
    "construction cost": "chi phí xây dựng",
    "rufous hawk-cuckoo": "chim cu diều hung",
    "(railway) crossing gate": "thanh chắn đường sắt",
    "deep-fried food (esp. chicken)": "đồ chiên (đặc biệt là gà chiên)",
    "deep-fried food": "đồ chiên giòn",
    "lively motion": "chuyển động sôi nổi",
    "exemplary": "mẫu mực, điển hình",
    "brimming with": "tràn đầy",
    "(husband and wife) earning a living together": "vợ chồng cùng đi làm",
    "universal suffrage": "phổ thông đầu phiếu",
    "approval": "sự chấp thuận",
    "heresy": "tà thuyết, dị giáo",
    "extensive": "rộng rãi, phạm vi rộng",
}

VIET = re.compile(r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', re.I)

def is_en(s):
    if not s or VIET.search(s): return False
    if re.search(r'[ぁ-んァ-ヶ一-鿿]', s): return False
    if not re.match(r'^[a-zA-Z\s\-\(\)\/\.,\'\"0-9%]+$', s.strip()): return False
    if len(s.strip()) <= 4: return False
    return True

def translate(s):
    t = s.strip()
    if t.lower() in DIRECT: return DIRECT[t.lower()]
    if t in DIRECT: return DIRECT[t]
    t_clean = re.sub(r'\(.*?\)', '', t).strip()
    if t_clean.lower() in DIRECT: return DIRECT[t_clean.lower()]
    for k, v in sorted(DIRECT.items(), key=lambda x: -len(x[0])):
        if k.lower() in t.lower(): return v
    return None

def fetch_jisho(word):
    url = "https://jisho.org/api/v1/search/words?keyword=" + urllib.parse.quote(word)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode()).get("data", [])
        if data:
            senses = data[0].get("senses", [])
            return [d for s in senses for d in s.get("english_definitions", [])][:3]
    except: pass
    return []

def parse_js(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries, structure = [], []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith('// ====='):
            structure.append({'_comment': line}); entries.append(None)
        elif s.startswith('{kanji:'):
            s2 = s.rstrip(',')
            try:
                j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', s2)
                obj = json.loads(j)
                structure.append(obj); entries.append(obj)
            except:
                structure.append({'_raw': s}); entries.append(None)
    h = content.index('const ALL_KANJI = [')
    f2 = content.rindex('];') + 2
    return structure, content[:h], content[f2:]

def dict_to_js(obj):
    fields = ['kanji','hanviet','on','kun','meaning','meaning_jp','level','strokes','words']
    parts = []
    for key in fields:
        if key not in obj: continue
        val = obj[key]
        if isinstance(val, str):
            parts.append(f'{key}:"{val.replace(chr(92),chr(92)*2).replace(chr(34),chr(92)+chr(34))}"')
        elif isinstance(val, list):
            parts.append(f'{key}:{json.dumps(val, ensure_ascii=False, separators=(",",":"))}')
        elif isinstance(val, (int,float)):
            parts.append(f'{key}:{val}')
    return '{' + ','.join(parts) + '}'

def write_js(path, structure, header, footer):
    lines = []
    for item in structure:
        if '_comment' in item: lines.append(item['_comment'])
        elif '_raw' in item: lines.append(item['_raw'] + ',')
        else: lines.append(dict_to_js(item) + ',')
    if lines and lines[-1].endswith(','): lines[-1] = lines[-1][:-1]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + 'const ALL_KANJI = [\n' + '\n'.join(lines) + '\n];' + footer)

def main():
    print('📂 Đọc kanji-data.js...')
    structure, header, footer = parse_js(JS_PATH)
    objs = [x for x in structure if x and '_comment' not in x and '_raw' not in x]

    n54 = [o for o in objs if o.get('level') in ('N5','N4')]
    print(f'   N5/N4: {len(n54)} kanji\n')

    fixed = removed = 0
    still_en = []

    for obj in n54:
        k = obj.get('kanji','?')
        words = obj.get('words', [])
        new_words = []
        changed = False

        for w in words:
            m = w.get('m','')
            if is_en(m):
                vi = translate(m)
                if not vi:
                    # Thử Jisho
                    defs = fetch_jisho(w.get('w',''))
                    time.sleep(0.1)
                    for d in defs[:3]:
                        vi = translate(d)
                        if vi: break
                if vi:
                    nw = dict(w); nw['m'] = vi
                    new_words.append(nw)
                    print(f'  ✅ [{k}] "{w["w"]}": "{m}" → "{vi}"')
                    fixed += 1; changed = True
                else:
                    still_en.append(f'{k}: {w.get("w","")} = "{m}"')
                    removed += 1; changed = True
                    print(f'  ❌ [{k}] "{w["w"]}": "{m}" — XÓA')
            else:
                new_words.append(w)

        if changed:
            if len(new_words) >= 1 or len(words) == 0:
                obj['words'] = new_words

    write_js(JS_PATH, structure, header, footer)
    print(f'\n✅ Đã sửa {fixed} nghĩa, xóa {removed} entry không dịch được')
    if still_en:
        with open(os.path.join(BASE, 'still_english_n54.log'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(still_en))
        print(f'📋 {len(still_en)} từ còn tiếng Anh → still_english_n54.log')

if __name__ == '__main__':
    main()
