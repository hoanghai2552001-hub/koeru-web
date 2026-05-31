"""
enrich_words_from_excel.py
Nạp toàn bộ từ vựng từ Excel N5/N4/N3 vào words[] của kanji-data.js

Mapping: Hán tự trong từ → tìm kanji tương ứng trong DB → thêm từ vào words[]
"""
import re, json, sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent.parent
JS   = BASE / "js"
INPUT = BASE / "input" / "excel"

# ── Vietnamese translation dict for N5/N4 (English → Vietnamese) ────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from vi_n3_translations import VI_N3 as VI_DICT
except ImportError:
    VI_DICT = {}

# Extra N5/N4 specific translations
VI_EXTRA = {
    "to meet, to see": "gặp; gặp mặt",
    "blue": "xanh lam; xanh",
    "red": "đỏ",
    "bright (in reference to personality or weather); cheerful": "sáng sủa; vui vẻ",
    "fall (season)": "mùa thu",
    "to open, to become open": "mở ra",
    "to open (v.t.)": "mở (ngoại động từ)",
    "to raise, to lift": "nâng lên; giơ lên",
    "morning": "buổi sáng",
    "to play (a game, sports)": "chơi (trò chơi, thể thao)",
    "over there": "đằng kia; đó",
    "hot (weather)": "nóng (thời tiết)",
    "leg, foot": "chân",
    "to wash": "rửa; giặt",
    "to give (to someone of lower status)": "cho (người bề dưới)",
    "meaning, significance": "ý nghĩa",
    "above, over, on top of": "trên; phía trên",
    "doctor, physician": "bác sĩ; thầy thuốc",
    "station": "nhà ga; trạm",
    "to go": "đi",
    "pool, pond": "hồ; ao",
    "busy, occupied": "bận; bận rộn",
    "one": "một",
    "dog": "con chó",
    "now": "bây giờ; hiện tại",
    "above, up, senior": "trên; phía trên; cấp trên",
    "song, melody": "bài hát; giai điệu",
    "movie, film": "phim; bộ phim",
    "Ah!, Oh!": "Ồ!; Ôi!",
    "to think, to feel": "nghĩ; cảm thấy",
    "mother": "mẹ; mẹ",
    "younger brother": "em trai",
    "younger sister": "em gái",
    "older brother": "anh trai",
    "older sister": "chị gái",
    "father": "bố; cha",
    "house, home": "nhà; ngôi nhà",
    "outside, foreign": "bên ngoài; nước ngoài",
    "picture, drawing, painting": "tranh; bức tranh",
    "school": "trường học",
    "to buy": "mua",
    "to write": "viết",
    "to hear, to listen": "nghe",
    "to read": "đọc",
    "to speak, to talk": "nói; nói chuyện",
    "to eat": "ăn",
    "to drink": "uống",
    "to come": "đến; tới",
    "to return, to go home": "về; trở về",
    "to get up, to rise": "dậy; thức dậy",
    "to sleep": "ngủ",
    "to do, to make": "làm; làm ra",
    "to see, to look, to watch": "xem; nhìn",
    "to wait": "chờ; đợi",
    "to use": "dùng; sử dụng",
    "to know": "biết",
    "to understand": "hiểu",
    "to start, to begin": "bắt đầu",
    "to finish, to end": "kết thúc; hoàn thành",
    "to turn on": "bật lên",
    "to turn off": "tắt đi",
    "to put, to place": "đặt; để",
    "big, large": "to; lớn",
    "small, little": "nhỏ; bé",
    "tall, high": "cao",
    "short, low": "thấp; ngắn",
    "long": "dài",
    "new": "mới",
    "old": "cũ; già",
    "good, nice": "tốt; đẹp",
    "bad": "xấu; tệ",
    "cheap, inexpensive": "rẻ",
    "expensive": "đắt",
    "near, close": "gần",
    "far": "xa",
    "fast, quick": "nhanh",
    "slow": "chậm",
    "hot (to the touch)": "nóng (khi chạm vào)",
    "cold (to the touch)": "lạnh (khi chạm vào)",
    "white": "trắng",
    "black": "đen",
    "yellow": "vàng",
    "train": "tàu điện; xe lửa",
    "car, vehicle": "xe hơi; ô tô",
    "bus": "xe buýt",
    "airplane": "máy bay",
    "ticket": "vé",
    "road, street": "đường; đường phố",
    "bridge": "cầu",
    "town, city": "thành phố; thị trấn",
    "country, nation": "đất nước; quốc gia",
    "Japan": "Nhật Bản",
    "person, people": "người",
    "man": "đàn ông",
    "woman": "phụ nữ",
    "child, children": "trẻ em; đứa trẻ",
    "friend": "bạn bè",
    "teacher": "giáo viên",
    "student": "học sinh; sinh viên",
    "company": "công ty",
    "office": "văn phòng",
    "shop, store": "cửa hàng",
    "bank": "ngân hàng",
    "hospital": "bệnh viện",
    "park": "công viên",
    "mountain": "núi",
    "sea, ocean": "biển",
    "river": "sông",
    "flower": "hoa",
    "tree": "cây",
    "cat": "con mèo",
    "animal": "động vật",
    "food": "thức ăn; đồ ăn",
    "water": "nước",
    "rice": "cơm; gạo",
    "bread": "bánh mì",
    "meat": "thịt",
    "fish": "cá",
    "vegetable": "rau",
    "fruit": "hoa quả",
    "money": "tiền",
    "time": "thời gian",
    "year": "năm",
    "month": "tháng",
    "day": "ngày",
    "week": "tuần",
    "hour": "giờ; tiếng",
    "minute": "phút",
    "today": "hôm nay",
    "tomorrow": "ngày mai",
    "yesterday": "hôm qua",
    "now, at this time": "bây giờ; lúc này",
    "always": "luôn luôn; lúc nào cũng",
    "often": "thường xuyên; hay",
    "sometimes": "đôi khi; thỉnh thoảng",
    "never": "không bao giờ",
    "already": "rồi; đã",
    "not yet": "chưa",
    "also, too": "cũng; cũng vậy",
    "only, just": "chỉ; chỉ thôi",
    "very": "rất; lắm",
    "a little": "một chút; ít",
    "many, a lot": "nhiều",
    "all, everything": "tất cả; hết",
    "about, approximately": "khoảng; xấp xỉ",
    "perhaps, maybe": "có lẽ; chắc là",
    "please (requesting)": "xin hãy; làm ơn",
    "thank you": "cảm ơn",
    "sorry, excuse me": "xin lỗi",
    "yes": "vâng; phải",
    "no": "không",
    "here": "ở đây; đây",
    "there": "ở đó; đó",
    "which": "cái nào; nào",
    "what": "cái gì; gì",
    "who": "ai",
    "when": "khi nào; lúc nào",
    "where": "ở đâu; đâu",
    "how": "như thế nào",
    "why": "tại sao; vì sao",
    "how many, how much": "bao nhiêu",
    "next (year, month, etc)": "tiếp theo; kế",
    "last (year, month, etc)": "trước; vừa rồi",
    "this (year, month, etc)": "này",
    "morning (time before noon)": "buổi sáng",
    "afternoon (noon to 6 pm)": "buổi chiều",
    "evening (6 pm to midnight)": "buổi tối",
    "night": "đêm; ban đêm",
    "noon": "buổi trưa",
    "spring": "mùa xuân",
    "summer": "mùa hè",
    "winter": "mùa đông",
    "weather": "thời tiết",
    "rain": "mưa",
    "snow": "tuyết",
    "wind": "gió",
    "warm (weather)": "ấm áp",
    "cool (weather)": "mát mẻ",
    "cloudy": "có mây; u ám",
    "sunny, clear": "trời nắng; quang đãng",
    "high school": "trường trung học phổ thông",
    "university": "đại học",
    "library": "thư viện",
    "book": "sách",
    "notebook": "vở; cuốn sổ",
    "pen": "bút bi",
    "pencil": "bút chì",
    "bag": "túi; cặp",
    "clothes": "quần áo",
    "shoe, shoes": "giày",
    "hat": "mũ; nón",
    "glasses": "kính mắt",
    "watch, clock": "đồng hồ",
    "telephone, phone": "điện thoại",
    "television, TV": "TV; tivi",
    "computer": "máy tính",
    "door": "cửa",
    "window": "cửa sổ",
    "chair": "ghế",
    "table, desk": "bàn",
    "bed": "giường",
    "bath, bathtub": "bồn tắm; tắm",
    "toilet": "nhà vệ sinh; toilet",
    "kitchen": "nhà bếp; bếp",
    "room": "phòng",
    "floor (level)": "tầng; lầu",
    "stairs": "cầu thang",
    "elevator": "thang máy",
    "entrance, front door": "cửa vào; lối vào",
    "garden, yard": "vườn; sân",
    "town, block": "khu phố; thị trấn",
    "hospital, clinic": "bệnh viện; phòng khám",
    "to study, to learn": "học; học tập",
    "to teach": "dạy",
    "to enter": "vào; bước vào",
    "to exit, to go out": "ra; đi ra",
    "to sit": "ngồi",
    "to stand": "đứng",
    "to walk": "đi bộ",
    "to run": "chạy",
    "to take, to pick up": "lấy; nhặt",
    "to make a phone call": "gọi điện",
    "to cut": "cắt",
    "to ask": "hỏi",
    "to answer": "trả lời",
    "to remember": "nhớ",
    "to forget": "quên",
    "to meet": "gặp",
    "together, with": "cùng; cùng nhau",
    "alone": "một mình",
    "slowly": "chậm chạp; từ từ",
    "quickly, fast": "nhanh; mau",
    "a lot, much": "nhiều; rất nhiều",
    "a little, few": "ít; một ít",
    "different": "khác; khác nhau",
    "same": "giống; như nhau",
    "important": "quan trọng",
    "interesting": "thú vị; hay",
    "difficult": "khó",
    "easy": "dễ",
    "convenient": "tiện lợi; thuận tiện",
    "inconvenient": "bất tiện",
    "clean": "sạch sẽ",
    "dirty": "bẩn; dơ",
    "quiet": "yên tĩnh; im lặng",
    "noisy": "ồn ào",
    "safe": "an toàn",
    "dangerous": "nguy hiểm",
    "healthy": "khỏe mạnh",
    "sick, ill": "bệnh; ốm",
    "happy": "vui; hạnh phúc",
    "sad": "buồn",
    "angry": "tức giận",
    "surprised": "ngạc nhiên",
    "afraid, scared": "sợ hãi",
    "fun, enjoyable": "vui vẻ; thú vị",
    "boring": "chán; nhàm chán",
    "tired": "mệt; mệt mỏi",
    "hungry": "đói",
    "thirsty": "khát",
    "to be able to, can": "có thể; được",
    "must, have to": "phải",
    "want to": "muốn",
    "to like": "thích",
    "to dislike, to not like": "không thích; ghét",
    "to love": "yêu",
    "to hate": "ghét",
    "to need": "cần",
    "to have, to exist": "có",
    "to not have, to not exist": "không có",
    "to become": "trở thành; trở nên",
    "to be": "là",
    "to live, to be alive": "sống",
    "to die": "chết",
    "to be born": "sinh ra",
    "to grow up": "lớn lên",
    "to change": "thay đổi",
    "straight, directly": "thẳng; trực tiếp",
    "right (direction)": "phải; bên phải",
    "left (direction)": "trái; bên trái",
    "in front of, before": "trước; phía trước",
    "behind, after": "sau; phía sau",
    "next to, beside": "bên cạnh",
    "between, middle": "ở giữa; giữa",
    "inside, within": "bên trong; trong",
    "outside": "bên ngoài; ngoài",
    "up, above, upper": "trên; phía trên",
    "down, below, lower": "dưới; phía dưới",
    "number": "số; con số",
    "color": "màu sắc; màu",
    "shape": "hình dạng",
    "size": "kích thước",
    "weight": "trọng lượng; cân nặng",
    "height": "chiều cao",
    "age": "tuổi",
    "face": "mặt; khuôn mặt",
    "eye": "mắt",
    "nose": "mũi",
    "mouth": "miệng",
    "hand, arm": "tay; cánh tay",
    "finger": "ngón tay",
    "hair": "tóc",
    "heart": "tim; trái tim",
    "head": "đầu",
    "stomach": "bụng; dạ dày",
    "neck": "cổ",
    "back": "lưng",
    "chest, breast": "ngực",
    "the same; together": "giống nhau; cùng nhau",
    "~ district, ~ ward, ~ borough": "~ quận; ~ khu",
    "straight, quickly": "thẳng; nhanh",
    "in a moment, soon": "lát nữa; sắp",
    "by any chance, possibly": "lỡ như; biết đâu",
    "sufficiently, satisfactorily": "đầy đủ; thỏa đáng",
    "to step on, to tread on": "bước lên; đạp lên",
    "please (giving/receiving)": "xin; làm ơn",
    "with pleasure, willingly": "vui lòng; sẵn sàng",
    "a moment, a while": "một lúc; chốc lát",
    "to hold, to carry": "cầm; mang",
    "already, anymore": "rồi; nữa",
    "to receive": "nhận",
    "various, different kinds of": "các loại; đa dạng",
    "suddenly, all of a sudden": "đột nhiên; bỗng dưng",
    "to pass, to go by": "qua; vượt qua",
    "to continue, to keep on": "tiếp tục",
    "to take off (clothes)": "cởi (quần áo)",
    "to wear (clothes)": "mặc (quần áo)",
    "to put on (glasses, accessories)": "đeo (kính, phụ kiện)",
    "to be worried, to be concerned": "lo lắng; băn khoăn",
    "to repair, to fix": "sửa chữa",
    "to save money": "tiết kiệm tiền",
    "recently, lately": "gần đây; dạo này",
    "to move (house)": "chuyển nhà",
    "to complain": "phàn nàn",
    "to smile": "mỉm cười",
    "to cry, to weep": "khóc",
    "to laugh": "cười",
    "to dream": "mơ",
    "to pray": "cầu nguyện",
    "to guess": "đoán",
    "to escape, to run away": "trốn; bỏ trốn",
    "to save, to rescue": "cứu",
    "to protect": "bảo vệ",
    "to attack": "tấn công",
    "to defeat": "đánh bại",
    "to win": "thắng",
    "to lose": "thua",
    "to tie, to draw": "hòa; ràng buộc",
    "to compare": "so sánh",
    "to choose, to select": "chọn; lựa chọn",
    "to decide": "quyết định",
    "to plan": "lên kế hoạch",
    "to practice": "luyện tập",
    "to prepare": "chuẩn bị",
    "to check, to confirm": "kiểm tra; xác nhận",
    "to contact": "liên lạc",
    "to introduce": "giới thiệu",
    "to explain": "giải thích",
    "to report": "báo cáo",
    "to discuss": "thảo luận",
    "to agree": "đồng ý",
    "to disagree": "không đồng ý",
    "to promise": "hứa",
    "to apologize": "xin lỗi",
    "to thank": "cảm ơn",
    "to refuse": "từ chối",
    "to accept": "chấp nhận; đồng ý",
    "to lend": "cho mượn",
    "to borrow": "mượn",
    "to give": "cho; tặng",
    "to receive (from superior)": "nhận (từ người trên)",
    "to pay": "trả tiền; thanh toán",
    "to earn": "kiếm tiền",
    "to spend": "chi tiêu",
    "to save": "tiết kiệm",
    "to invest": "đầu tư",
    "to sell": "bán",
    "to rent": "thuê",
    "to build": "xây dựng",
    "to destroy": "phá hủy",
    "to clean": "dọn dẹp; lau chùi",
    "to cook": "nấu ăn",
    "to bake": "nướng",
    "to boil": "luộc; đun sôi",
    "to fry": "chiên; rán",
    "to cut (food)": "cắt (thức ăn)",
    "to mix": "trộn",
    "to pour": "rót; đổ",
    "to carry (heavy things)": "khiêng; vác",
    "to lift": "nâng; nhấc",
    "to pull": "kéo",
    "to push": "đẩy",
    "to throw": "ném",
    "to catch": "bắt",
    "to hit": "đánh; đập",
    "to kick": "đá",
    "to jump": "nhảy",
    "to fall": "ngã; rơi",
    "to climb": "leo",
    "to swim": "bơi",
    "to fly": "bay",
}

VIET_CHARS = set('àáảãạăắặằẳẵâấầẩẫậđèéẻẽẹêếềệểễìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵÀÁẢÃẠĂẮẶẰẲẴÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỆỂỄÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ')

def is_vi(s):
    return bool(s) and any(c in VIET_CHARS for c in str(s))

def translate_en(en):
    if not en or str(en)=='nan': return ''
    s = str(en).strip()
    if is_vi(s): return s
    return (VI_EXTRA.get(s) or VI_DICT.get(s) or
            VI_EXTRA.get(s.replace('; ',', ')) or VI_DICT.get(s.replace('; ',', ')) or
            VI_EXTRA.get(s.split(';')[0].strip()) or VI_DICT.get(s.split(';')[0].strip()) or
            VI_EXTRA.get(s.split(',')[0].strip()) or VI_DICT.get(s.split(',')[0].strip()) or
            s)  # keep original if no translation

# ── Load kanji DB ─────────────────────────────────────────────────────────
print("Loading kanji database...")
src_map = {}  # kanji_char → which level file it's in
kanji_db = {}  # kanji_char → {entry dict with words list}

for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
    path = JS / f'kanji-data-{lv}.js'
    content = path.read_text(encoding='utf-8')
    # Parse entries
    for m in re.finditer(r'\{kanji:"([^"]+)"[^}]+\}(?:\,?\s*\{(?:[^{}]|\{[^{}]*\})*\})*', content):
        pass  # need better parser

# Use simpler approach: extract just kanji→words mapping
# Read combined file line by line
content_combined = (JS / 'kanji-data.js').read_text(encoding='utf-8')
# Parse each entry
entry_pattern = re.compile(
    r'\{kanji:"(?P<kanji>[^"]+)"[^}]*?level:"(?P<level>[^"]+)"[^}]*?words:\[(?P<words>[^\]]*)\]',
    re.DOTALL
)

kanji_words = {}  # kanji → set of word strings already in words[]
kanji_level = {}  # kanji → level

for m in entry_pattern.finditer(content_combined):
    k = m.group('kanji')
    lv = m.group('level')
    words_raw = m.group('words')
    # Extract existing word strings
    existing = set(re.findall(r'"w":"([^"]+)"', words_raw))
    kanji_words[k] = existing
    kanji_level[k] = lv

print(f"  Loaded {len(kanji_words)} kanji entries")

# ── Load Excel vocab ──────────────────────────────────────────────────────
def parse_kanji_field(val):
    """'作 法' → ['作', '法'], '冷' → ['冷']"""
    if not val or str(val)=='nan': return []
    return [c.strip() for c in re.split(r'[\s,;]+', str(val).strip()) if c.strip() and len(c.strip())==1]

all_vocab = []  # list of {word, reading, meaning_vi, kanji_chars}

# N5
print("Loading N5 Excel...")
df5 = pd.read_excel(INPUT / 'KOERU_JLPT_N5_Vocab_Kanji_OnKun_HanViet.xlsx', sheet_name='Vocab_N5')
for _, row in df5.iterrows():
    w = str(row.get('Từ vựng / Expression','')).strip()
    r = str(row.get('Cách đọc / Reading','')).strip()
    en = str(row.get('Nghĩa nguồn EN','')).strip()
    kanji_str = row.get('Hán tự trong từ', '')
    if not w or w=='nan': continue
    vi = translate_en(en)
    kanjis = parse_kanji_field(kanji_str)
    all_vocab.append({'w':w,'r':r,'m':vi,'kanjis':kanjis,'level':'N5'})

# N4
print("Loading N4 Excel...")
df4 = pd.read_excel(INPUT / 'KOERU_JLPT_N4_Vocab_Kanji_OnKun_HanViet.xlsx', sheet_name='Vocab_N4')
for _, row in df4.iterrows():
    w = str(row.get('Từ vựng','')).strip()
    r = str(row.get('Cách đọc','')).strip()
    en = str(row.get('Nghĩa EN nguồn','')).strip()
    kanji_str = row.get('Hán tự trong từ', '')
    if not w or w=='nan': continue
    vi = translate_en(en)
    kanjis = parse_kanji_field(kanji_str)
    all_vocab.append({'w':w,'r':r,'m':vi,'kanjis':kanjis,'level':'N4'})

# N3
print("Loading N3 Excel (8 parts)...")
for i in range(1,9):
    df3 = pd.read_excel(INPUT / f'KOERU_JLPT_N3_Vocab_Kanji_OnKun_HanViet_QA_v2_Part0{i}.xlsx', sheet_name='Vocab_N3')
    for _, row in df3.iterrows():
        w = str(row.get('Từ vựng','')).strip()
        r = str(row.get('Cách đọc','')).strip()
        vi = str(row.get('Nghĩa tiếng Việt','')).strip()
        kanji_str = row.get('Hán tự trong từ', '')
        if not w or w=='nan': continue
        if not is_vi(vi):
            vi = translate_en(vi)
        kanjis = parse_kanji_field(kanji_str)
        all_vocab.append({'w':w,'r':r,'m':vi,'kanjis':kanjis,'level':'N3'})

print(f"  Total vocab loaded: {len(all_vocab)}")

# ── Build new words to add per kanji ────────────────────────────────────
print("\nMapping vocab to kanji...")
new_words = {k: [] for k in kanji_words}  # kanji → list of new {w,r,m} to add

added = 0
no_match = 0
for entry in all_vocab:
    if not entry['kanjis']: continue
    if not entry['m'] or not is_vi(entry['m']): continue  # skip if no Vietnamese meaning
    for k in entry['kanjis']:
        if k not in kanji_words: continue
        if entry['w'] in kanji_words[k]: continue  # already exists
        # Don't add duplicates within the new_words list
        if any(x['w']==entry['w'] for x in new_words[k]): continue
        new_words[k].append({'w':entry['w'],'r':entry['r'],'m':entry['m']})
        kanji_words[k].add(entry['w'])  # mark as added
        added += 1

print(f"  New words to add: {added}")

# ── Patch per-level JS files ─────────────────────────────────────────────
print("\nPatching JS files...")
total_patched = 0

for lv in ['n5','n4','n3','n2','n1']:
    path = JS / f'kanji-data-{lv}.js'
    content = path.read_text(encoding='utf-8')
    patched = 0
    for k, words_to_add in new_words.items():
        if not words_to_add: continue
        # Find this kanji entry and append to its words[]
        # Pattern: words:[...existing...]
        pattern = r'(kanji:"' + re.escape(k) + r'".*?words:\[)(.*?)(\])'
        def replacer(m, k=k, wta=words_to_add):
            existing = m.group(2).strip()
            new_entries = ','.join(
                f'{{"w":"{w["w"]}","r":"{w["r"]}","m":"{w["m"]}"}}'
                for w in wta
            )
            if existing:
                return m.group(1) + existing + ',' + new_entries + m.group(3)
            else:
                return m.group(1) + new_entries + m.group(3)
        new_content, count = re.subn(pattern, replacer, content, flags=re.DOTALL, count=1)
        if count:
            content = new_content
            patched += 1
    path.write_text(content, encoding='utf-8')
    total_patched += patched
    print(f"  {lv.upper()}: {patched} kanji updated")

# Rebuild combined
print("\nRebuilding kanji-data.js...")
parts = []
for lv in ['n5','n4','n3','n2','n1']:
    c = (JS/f'kanji-data-{lv}.js').read_text(encoding='utf-8')
    s = c.index('['); e = c.rindex(']')+1
    inner = c[s+1:e-1].strip().rstrip(',')
    if inner: parts.append(inner)
(JS/'kanji-data.js').write_text('window.KANJI_DATA = [\n'+',\n'.join(parts)+'\n];\n', encoding='utf-8')

# ── Final stats ──────────────────────────────────────────────────────────
content_final = (JS/'kanji-data.js').read_text(encoding='utf-8')
for lv in ['N5','N4','N3']:
    n_kanji = content_final.count(f'level:"{lv}"')
    n_words = len(re.findall(r'"w":"[^"]+"', content_final[:content_final.find(f'level:"{["N4","N3","N2"][["N5","N4","N3"].index(lv)+1] if lv!="N3" else "N2"}"')]))
    pass

print("\n✅ Done!")
print(f"   Total kanji updated: {total_patched}")
print(f"   Total new word entries: {added}")
