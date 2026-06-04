"""
Build accurate kanji-data.js from:
  - KanjiAPI (kanjiapi.dev)  → on/kun readings, stroke count, JLPT level
  - Current kanji-data.js    → existing Vietnamese meanings (base)
  - Curated EN→VI map        → improve/standardize Vietnamese meanings

Output: js/kanji-data.js (overwrite)

Run: python build_kanji_data.py
"""
import re, json, time, requests, os, sys

BASE      = os.path.dirname(os.path.abspath(__file__))
INPUT_JS  = os.path.join(BASE, "js", "kanji-data.js")
OUTPUT_JS = os.path.join(BASE, "js", "kanji-data.js")
CACHE_F   = os.path.join(BASE, "kanji_api_cache.json")

# ──────────────────────────────────────────
#  Bản dịch EN → VI cho meaning từ KanjiAPI
#  Ưu tiên ngữ cảnh tiếng Việt tự nhiên
# ──────────────────────────────────────────
EN_VI = {
    # Số đếm
    "one":"một","two":"hai","three":"ba","four":"bốn","five":"năm",
    "six":"sáu","seven":"bảy","eight":"tám","nine":"chín","ten":"mười",
    "hundred":"trăm","thousand":"nghìn","ten thousand":"vạn",
    # Thiên nhiên
    "fire":"lửa","water":"nước","wood":"cây, gỗ","metal":"kim loại",
    "earth":"đất","mountain":"núi","river":"sông","sea":"biển",
    "sky":"bầu trời","sun":"mặt trời","moon":"mặt trăng","star":"sao",
    "rain":"mưa","snow":"tuyết","wind":"gió","cloud":"mây","thunder":"sấm sét",
    "tree":"cây","flower":"hoa","grass":"cỏ","leaf":"lá",
    # Người & gia đình
    "person":"người","man":"đàn ông","woman":"phụ nữ","child":"trẻ em",
    "father":"cha, bố","mother":"mẹ","older brother":"anh trai",
    "older sister":"chị gái","younger sibling":"em","friend":"bạn bè",
    "king":"vua","master":"thầy, chủ nhân","teacher":"giáo viên",
    # Cơ thể
    "eye":"mắt","ear":"tai","mouth":"miệng","hand":"tay","foot":"chân",
    "heart":"trái tim, tâm","body":"cơ thể","head":"đầu","face":"mặt",
    # Màu sắc
    "white":"trắng","black":"đen","red":"đỏ","blue":"xanh lam",
    "green":"xanh lá","yellow":"vàng",
    # Thời gian
    "day":"ngày","month":"tháng","year":"năm","time":"thời gian",
    "morning":"buổi sáng","evening":"buổi tối","night":"đêm",
    "before":"trước","after":"sau","now":"bây giờ",
    "spring":"mùa xuân","summer":"mùa hè","autumn":"mùa thu","winter":"mùa đông",
    # Hướng & vị trí
    "above":"trên","below":"dưới, phía dưới","left":"trái","right":"phải",
    "inside":"bên trong","outside":"bên ngoài","center":"trung tâm, giữa",
    "north":"phía bắc","south":"phía nam","east":"phía đông","west":"phía tây",
    "entrance":"lối vào","exit":"lối ra",
    # Hành động thông dụng
    "eat":"ăn","drink":"uống","see":"nhìn, thấy","hear":"nghe",
    "speak":"nói","write":"viết","read":"đọc","buy":"mua","sell":"bán",
    "go":"đi","come":"đến","return":"về, trở lại","stop":"dừng lại",
    "stand":"đứng","sit":"ngồi","sleep":"ngủ","wake":"thức dậy",
    "enter":"vào","exit":"ra","open":"mở","close":"đóng",
    "give":"cho, tặng","receive":"nhận","use":"dùng, sử dụng",
    "know":"biết","think":"suy nghĩ, nghĩ","study":"học",
    "work":"làm việc","play":"chơi","walk":"đi bộ","run":"chạy",
    "meet":"gặp gỡ","wait":"chờ","teach":"dạy","learn":"học",
    # Tính chất thông dụng
    "big":"to, lớn","small":"nhỏ, bé","long":"dài","short":"ngắn",
    "tall":"cao","high":"cao","low":"thấp","wide":"rộng","narrow":"hẹp",
    "old":"cũ, già","new":"mới","young":"trẻ",
    "good":"tốt, giỏi","bad":"xấu, tồi","correct":"đúng","wrong":"sai",
    "fast":"nhanh","slow":"chậm","early":"sớm","late":"muộn, trễ",
    "hot":"nóng","cold":"lạnh","warm":"ấm","cool":"mát",
    "bright":"sáng","dark":"tối","heavy":"nặng","light":"nhẹ",
    "hard":"cứng, khó","soft":"mềm, dễ","easy":"dễ","difficult":"khó",
    "strong":"mạnh","weak":"yếu","rich":"giàu","poor":"nghèo",
    "cheap":"rẻ","expensive":"đắt","beautiful":"đẹp","ugly":"xấu",
    "safe":"an toàn","peaceful":"bình yên","quiet":"yên tĩnh",
    "happy":"vui vẻ, hạnh phúc","sad":"buồn","angry":"tức giận",
    # Địa điểm
    "country":"đất nước","city":"thành phố","town":"thị trấn","village":"làng",
    "school":"trường học","hospital":"bệnh viện","station":"ga tàu",
    "temple":"đền, chùa","shrine":"miếu","house":"nhà","room":"phòng",
    "road":"đường","bridge":"cầu","park":"công viên",
    # Đồ vật
    "book":"sách","money":"tiền","car":"xe hơi","train":"tàu hỏa",
    "clothes":"quần áo","food":"thức ăn, đồ ăn","rice":"cơm, gạo",
    "sword":"kiếm","bow":"cung tên","letter":"thư, chữ",
    # Khái niệm trừu tượng
    "power":"sức mạnh, quyền lực","spirit":"tinh thần, linh hồn",
    "heaven":"trời, thiên đàng","earth":"đất, trái đất",
    "life":"cuộc sống, sinh mệnh","death":"cái chết",
    "love":"tình yêu, yêu thương","war":"chiến tranh","peace":"hòa bình",
    "truth":"sự thật","lie":"nói dối","justice":"công lý",
    "beginning":"bắt đầu, khởi đầu","end":"kết thúc",
    "number":"số","name":"tên","word":"từ, lời nói",
    "language":"ngôn ngữ","meaning":"ý nghĩa",
    # JLPT hay gặp
    "stand up":"đứng dậy","get up":"thức dậy",
    "to eat":"ăn","to drink":"uống","to go":"đi","to come":"đến",
    "to see":"xem, nhìn","to hear":"nghe","to read":"đọc","to write":"viết",
    "to buy":"mua","to sell":"bán","to use":"sử dụng",
    "meeting":"cuộc họp, hội nghị","company":"công ty",
    "electricity":"điện","gas":"khí ga","telephone":"điện thoại",
    "message":"tin nhắn","answer":"câu trả lời","question":"câu hỏi",
    "test":"bài kiểm tra","score":"điểm số",
    "price":"giá cả","cost":"chi phí","tax":"thuế",
    "travel":"du lịch","trip":"chuyến đi",
    "music":"âm nhạc","picture":"bức tranh, hình ảnh","painting":"tranh vẽ",
    "sport":"thể thao","game":"trò chơi",
    "news":"tin tức","newspaper":"báo","magazine":"tạp chí",
    "letter":"thư","mail":"thư, bưu kiện",
    "hospital":"bệnh viện","doctor":"bác sĩ","medicine":"thuốc",
    "police":"cảnh sát","law":"luật pháp","court":"tòa án",
    "government":"chính phủ","politics":"chính trị",
    "society":"xã hội","culture":"văn hóa","history":"lịch sử",
    "science":"khoa học","technology":"công nghệ","industry":"công nghiệp",
    "economy":"kinh tế","trade":"thương mại, buôn bán",
    "agriculture":"nông nghiệp","nature":"tự nhiên, thiên nhiên",
    "environment":"môi trường","pollution":"ô nhiễm",
    "temperature":"nhiệt độ","weather":"thời tiết",
}

def translate_meanings(english_meanings):
    """Dịch list nghĩa EN → VI, ưu tiên ngắn gọn, sát nghĩa"""
    result = []
    for m in english_meanings[:5]:  # Lấy tối đa 5 nghĩa
        m_lower = m.lower().strip()
        # Tìm trong bản dịch
        vi = EN_VI.get(m_lower)
        if not vi:
            # Thử tìm partial match
            for en, vi_val in EN_VI.items():
                if en in m_lower or m_lower in en:
                    vi = vi_val
                    break
        if vi and vi not in result:
            result.append(vi)
    return result

def format_kun(kun_readings):
    """Format kun readings — loại bỏ dấu chấm okurigana cho gọn"""
    clean = []
    for r in kun_readings[:3]:
        # Giữ dạng đầy đủ nhưng bỏ dấu chấm: やす.い → やすい
        display = r.replace('.', '')
        if display not in clean:
            clean.append(display)
    return '、'.join(clean) if clean else '—'

def format_on(on_readings):
    """Format on readings"""
    return '、'.join(on_readings[:3]) if on_readings else '—'

# ──────────────────────────────────────────
#  Load cache (tránh gọi API lại)
# ──────────────────────────────────────────
cache = {}
if os.path.exists(CACHE_F):
    with open(CACHE_F, encoding='utf-8') as f:
        cache = json.load(f)
    print(f"Cache loaded: {len(cache)} entries")

# ──────────────────────────────────────────
#  Parse kanji-data.js → extract entries
# ──────────────────────────────────────────
with open(INPUT_JS, encoding='utf-8') as f:
    js_content = f.read()

pattern = r'\{kanji:"(.)",hanviet:"([^"]*)",on:"([^"]*)",kun:"([^"]*)",meaning:"([^"]*)",meaning_jp:"([^"]*)",level:"([^"]*)"\}'
entries = re.findall(pattern, js_content)
print(f"Parsed {len(entries)} entries from JS")

# Also get compound word data (after ALL_KANJI array)
compound_section = js_content[js_content.find('COMPOUND'):]

# ──────────────────────────────────────────
#  Fetch KanjiAPI for each kanji
# ──────────────────────────────────────────
JLPT_MAP = {4:'N5', 3:'N4', 2:'N3', 1:'N2', 0:'N1', None:'N1'}

def fetch_kanji(k):
    if k in cache:
        return cache[k]
    try:
        r = requests.get(f'https://kanjiapi.dev/v1/kanji/{k}', timeout=10)
        if r.status_code == 200:
            data = r.json()
            cache[k] = data
            return data
    except Exception as e:
        print(f"  ERR {k}: {e}")
    return None

# ──────────────────────────────────────────
#  Build new entries
# ──────────────────────────────────────────
new_entries = []
total = len(entries)

for i, (kanji, hanviet, old_on, old_kun, old_meaning, old_meaning_jp, level) in enumerate(entries):
    sys.stdout.write(f"\r  [{i+1}/{total}] {kanji} ...    ")
    sys.stdout.flush()

    api = fetch_kanji(kanji)
    time.sleep(0.05)  # rate limit

    if api:
        # On/kun từ API (chuẩn nhất)
        on  = format_on(api.get('on_readings', []))
        kun = format_kun(api.get('kun_readings', []))

        # Nghĩa: ưu tiên bản dịch VI từ API meanings, fallback sang existing
        en_meanings = api.get('meanings', [])
        vi_from_api = translate_meanings(en_meanings)
        if vi_from_api:
            # Giữ nghĩa tiếng Việt cũ nếu tốt hơn (dài hơn = cụ thể hơn)
            old_parts = [m.strip() for m in old_meaning.split(',')]
            # Merge: ưu tiên existing VI nếu khác và cụ thể
            merged = old_parts if len(old_parts) >= len(vi_from_api) else vi_from_api
            meaning = ', '.join(merged[:4])
        else:
            meaning = old_meaning

        # meaning_jp: dùng on_readings + heisig hint
        heisig = api.get('heisig_en', '')
        meaning_jp = old_meaning_jp  # giữ nguyên, đã tốt

        # Level từ API nếu khác
        api_jlpt = JLPT_MAP.get(api.get('jlpt'), level)
        # Giữ level hiện tại (đã được curate thủ công)
    else:
        on, kun, meaning, meaning_jp, api_jlpt = old_on, old_kun, old_meaning, old_meaning_jp, level

    new_entries.append({
        'kanji': kanji,
        'hanviet': hanviet,
        'on': on,
        'kun': kun,
        'meaning': meaning,
        'meaning_jp': meaning_jp,
        'level': level  # Giữ level gốc
    })

print(f"\nDone fetching. Saving cache...")
with open(CACHE_F, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────
#  Group by level
# ──────────────────────────────────────────
by_level = {'N5':[], 'N4':[], 'N3':[], 'N2':[], 'N1':[]}
for e in new_entries:
    lvl = e['level']
    if lvl in by_level:
        by_level[lvl].append(e)

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def entry_to_js(e):
    return (f'{{kanji:"{e["kanji"]}",'
            f'hanviet:"{esc(e["hanviet"])}",'
            f'on:"{esc(e["on"])}",'
            f'kun:"{esc(e["kun"])}",'
            f'meaning:"{esc(e["meaning"])}",'
            f'meaning_jp:"{esc(e["meaning_jp"])}",'
            f'level:"{e["level"]}"}}'
            )

# ──────────────────────────────────────────
#  Extract compound section (keep as-is)
# ──────────────────────────────────────────
# Find compound data start
comp_match = re.search(r'(// ─+ Compound word data.*)', js_content, re.DOTALL)
compound_js = comp_match.group(1) if comp_match else ''

# ──────────────────────────────────────────
#  Write kanji-data.js
# ──────────────────────────────────────────
lines = ['// ══════════════════════════════════════════',
         '// KANJI DATA — Auto-generated by build_kanji_data.py',
         f'// Source: KanjiAPI (kanjiapi.dev) + curated Vietnamese translations',
         f'// Total: {len(new_entries)} kanji (N5-N1)',
         '// ══════════════════════════════════════════',
         'const ALL_KANJI = [']

for lvl in ['N5','N4','N3','N2','N1']:
    group = by_level[lvl]
    if group:
        lines.append(f'// ===== {lvl} ({len(group)} kanji) =====')
        for e in group:
            lines.append(entry_to_js(e) + ',')

lines.append('];')
lines.append('')
if compound_js:
    lines.append(compound_js.rstrip())

output = '\n'.join(lines)
with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\n✅ Written to {OUTPUT_JS}")
print(f"   N5:{len(by_level['N5'])}  N4:{len(by_level['N4'])}  N3:{len(by_level['N3'])}  N2:{len(by_level['N2'])}  N1:{len(by_level['N1'])}")
