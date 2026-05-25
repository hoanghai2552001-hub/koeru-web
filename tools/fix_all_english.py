"""
fix_all_english.py — Sửa tất cả nghĩa tiếng Anh trong kanji-data.js
Chiến lược:
  1. Dict lookup (950+ entries) → dịch trực tiếp
  2. Pattern regex → dịch theo pattern
  3. Không dịch được → xoá word entry (giữ ít nhất 1 word/kanji)
Chạy: python tools/fix_all_english.py (từ root project)
"""
import re, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
JS_PATH = os.path.join(ROOT, 'js', 'kanji-data.js')

# ══════════════════════════════════════════════════════════════════
# BẢNG DỊCH EN → VI (từ qa_report + curated)
# ══════════════════════════════════════════════════════════════════
EN_VI = {
    # ── Thời gian ──
    "last year": "năm ngoái", "this year": "năm nay", "next year": "năm tới",
    "last month": "tháng trước", "next month": "tháng sau",
    "last week": "tuần trước", "next week": "tuần sau",
    "next morning": "sáng hôm sau", "the next day": "ngày hôm sau",
    "on the same day": "cùng ngày", "same day": "cùng ngày",
    "every year": "mỗi năm", "every month": "mỗi tháng",
    "every week": "mỗi tuần", "every day": "mỗi ngày",
    "from now on": "từ nay về sau", "from now": "từ bây giờ",
    "recently": "gần đây", "lately": "dạo gần đây",
    "immediately": "ngay lập tức", "at once": "ngay lập tức",
    "temporarily": "tạm thời", "for the time being": "tạm thời",

    # ── Giáo dục ──
    "elementary school": "trường tiểu học",
    "middle school": "trường trung học cơ sở",
    "high school": "trường trung học phổ thông",
    "normal school": "trường sư phạm",
    "school excursion": "dã ngoại học đường",
    "textbook": "sách giáo khoa",
    "graduation ceremony": "lễ tốt nghiệp",
    "entrance ceremony": "lễ nhập học",
    "school opening": "khai giảng",
    "scholarship": "học bổng",
    "study abroad": "du học",
    "cram school": "trường luyện thi",

    # ── Công việc / tổ chức ──
    "absence (from work)": "nghỉ việc, vắng mặt",
    "absence from work": "nghỉ việc", "absent from work": "nghỉ việc",
    "overtime work": "làm thêm giờ", "overtime": "làm thêm giờ",
    "part-time work": "làm bán thời gian", "part-time job": "việc bán thời gian",
    "full-time employee": "nhân viên chính thức",
    "temporary employee": "nhân viên tạm thời",
    "resignation": "từ chức", "retirement": "về hưu, nghỉ hưu",
    "promotion": "thăng chức", "demotion": "giáng chức",
    "transfer": "chuyển công tác", "assignment": "nhiệm vụ",
    "salary": "lương", "wage": "tiền công",
    "bonus": "tiền thưởng", "allowance": "phụ cấp",
    "labor union": "công đoàn", "trade union": "công đoàn",
    "working condition": "điều kiện làm việc",
    "employment": "việc làm", "unemployment": "thất nghiệp",
    "dismissal": "sa thải", "layoff": "cho thôi việc",
    "recruitment": "tuyển dụng",
    "business trip": "công tác", "on a business trip": "đi công tác",

    # ── Hành chính / luật pháp ──
    "administration of justice": "tư pháp",
    "administrative litigation": "kiện hành chính",
    "administrative measures": "biện pháp hành chính",
    "local government": "chính quyền địa phương",
    "municipal government": "chính quyền thành phố",
    "prefectural government": "chính quyền tỉnh",
    "national government": "chính phủ trung ương",
    "tax bureau": "cục thuế",
    "census": "điều tra dân số",
    "national census": "tổng điều tra dân số",
    "district court": "tòa án quận",
    "supreme court": "tòa án tối cao",
    "public prosecutor": "công tố viên",
    "lawyer": "luật sư",
    "verdict": "phán quyết",
    "sentence": "bản án", "conviction": "kết tội",
    "acquittal": "tha bổng, vô tội",
    "arrest": "bắt giữ", "detention": "tạm giam",
    "indictment": "cáo trạng",
    "lawsuit": "vụ kiện", "litigation": "tố tụng",
    "settlement": "dàn xếp, hòa giải",
    "constitutional law": "hiến pháp",
    "civil law": "luật dân sự",
    "criminal law": "luật hình sự",
    "violation": "vi phạm",

    # ── Kinh tế / tài chính ──
    "stock market": "thị trường chứng khoán",
    "stock exchange": "sàn giao dịch chứng khoán",
    "securities": "chứng khoán",
    "investment": "đầu tư",
    "interest rate": "lãi suất",
    "inflation": "lạm phát", "deflation": "giảm phát",
    "recession": "suy thoái kinh tế",
    "economic growth": "tăng trưởng kinh tế",
    "gdp": "GDP",
    "trade balance": "cán cân thương mại",
    "export": "xuất khẩu", "import": "nhập khẩu",
    "tariff": "thuế quan",
    "bankruptcy": "phá sản",
    "debt": "nợ", "loan": "khoản vay",
    "mortgage": "thế chấp",
    "budget": "ngân sách",
    "revenue": "doanh thu",
    "profit": "lợi nhuận", "loss": "thua lỗ",
    "dividend": "cổ tức",
    "currency": "tiền tệ",
    "exchange rate": "tỷ giá hối đoái",

    # ── Y tế / sức khỏe ──
    "hospital": "bệnh viện",
    "clinic": "phòng khám",
    "surgery": "phẫu thuật",
    "operation": "ca phẫu thuật",
    "diagnosis": "chẩn đoán",
    "prescription": "đơn thuốc",
    "medicine": "thuốc", "drug": "thuốc",
    "vaccination": "tiêm chủng",
    "epidemic": "dịch bệnh",
    "symptom": "triệu chứng",
    "treatment": "điều trị",
    "recovery": "hồi phục",
    "disease": "bệnh",
    "infection": "nhiễm trùng",
    "fracture": "gãy xương",
    "bleeding": "chảy máu",
    "first aid": "sơ cứu",
    "emergency": "khẩn cấp",
    "ambulance": "xe cứu thương",
    "rehabilitation": "phục hồi chức năng",
    "resuscitation": "hồi sức",
    "low blood pressure": "huyết áp thấp",
    "high blood pressure": "huyết áp cao",
    "blood type": "nhóm máu",
    "low frequency": "tần số thấp",

    # ── Thiên nhiên / môi trường ──
    "earthquake": "động đất",
    "tsunami": "sóng thần",
    "flood": "lũ lụt",
    "drought": "hạn hán",
    "typhoon": "bão lớn",
    "volcanic eruption": "núi lửa phun",
    "landslide": "sạt lở đất",
    "eruption of smoke": "khói bốc lên",
    "rainfall": "lượng mưa",
    "amount of rainfall": "lượng mưa",
    "snowfall": "tuyết rơi",
    "temperature": "nhiệt độ",
    "humidity": "độ ẩm",
    "weather forecast": "dự báo thời tiết",
    "season of winter": "mùa đông",
    "season of summer": "mùa hè",
    "winter season": "mùa đông",
    "spring season": "mùa xuân",
    "summer season": "mùa hè",
    "autumn season": "mùa thu",

    # ── Giao thông / di chuyển ──
    "traffic jam": "tắc đường",
    "traffic accident": "tai nạn giao thông",
    "traffic signal": "đèn giao thông",
    "pedestrian crossing": "vạch sang đường",
    "railway crossing gate": "rào chắn đường sắt",
    "railroad crossing": "đường ngang",
    "departure": "khởi hành", "arrival": "đến nơi",
    "transfer (train)": "chuyển tàu",
    "commute": "đi làm hàng ngày",
    "driving license": "bằng lái xe",
    "speed limit": "giới hạn tốc độ",
    "parking lot": "bãi đỗ xe",
    "expressway": "đường cao tốc",
    "highway": "đường quốc lộ",
    "navigation": "dẫn đường",
    "overhead luggage rack": "giá để hành lý trên cao",

    # ── Gia đình / xã hội ──
    "marriage": "hôn nhân",
    "divorce": "ly hôn",
    "adoption of a person": "nhận con nuôi",
    "adoption": "nhận con nuôi",
    "inheritance": "thừa kế",
    "will (legal document)": "di chúc",
    "funeral": "tang lễ",
    "ceremony": "lễ nghi",
    "only child": "con một",
    "younger brother": "em trai",
    "older brother": "anh trai",
    "younger sister": "em gái",
    "older sister": "chị gái",
    "husband and wife": "vợ chồng",
    "newlyweds": "vợ chồng mới cưới",

    # ── Khoa học / công nghệ ──
    "experiment": "thí nghiệm",
    "research": "nghiên cứu",
    "hypothesis": "giả thuyết",
    "theory": "lý thuyết",
    "invention": "phát minh",
    "patent": "bằng sáng chế",
    "microscope": "kính hiển vi",
    "telescope": "kính thiên văn",
    "periodic table": "bảng tuần hoàn",
    "chemical reaction": "phản ứng hóa học",
    "aqueous solution": "dung dịch nước",
    "translucent aqueous solution": "dung dịch trong suốt",
    "electric current": "dòng điện",
    "electromagnetic wave": "sóng điện từ",
    "nuclear power": "năng lượng hạt nhân",
    "solar energy": "năng lượng mặt trời",
    "artificial intelligence": "trí tuệ nhân tạo",
    "internet": "Internet",
    "software": "phần mềm",
    "hardware": "phần cứng",

    # ── Văn hóa / nghệ thuật ──
    "writing song lyrics": "viết lời bài hát",
    "song lyrics": "lời bài hát",
    "painting": "hội họa",
    "canvas": "vải canvas",
    "oil painting canvas": "vải vẽ tranh sơn dầu",
    "writing brush": "bút lông",
    "calligraphy": "thư pháp",
    "theater": "nhà hát",
    "theatrical fighting scene": "cảnh đánh nhau trong kịch",
    "film": "phim điện ảnh", "movie": "phim",
    "double feature": "chiếu hai phim liên tiếp",
    "double exposure": "phơi sáng đôi",
    "documentary": "phim tài liệu",
    "photography": "nhiếp ảnh",
    "photographic printing paper": "giấy in ảnh",
    "literature": "văn học",
    "poetry": "thơ ca",
    "novel": "tiểu thuyết",
    "music": "âm nhạc",
    "instrument": "nhạc cụ",
    "music of wind through pine trees": "tiếng gió qua rừng thông",

    # ── Tôn giáo / triết học ──
    "buddhism": "Phật giáo",
    "shinto": "Thần đạo",
    "temple": "chùa",
    "shrine": "đền thờ",
    "main building of a shinto shrine": "chính điện đền Shinto",
    "prayer": "lời cầu nguyện",
    "ritual": "nghi lễ",
    "heresy": "tà thuyết",
    "doctrine": "giáo lý",
    "philosophy": "triết học",
    "logic": "logic",
    "ethics": "đạo đức học",

    # ── Quân sự / chiến tranh ──
    "war": "chiến tranh",
    "battle": "trận chiến",
    "army": "quân đội",
    "navy": "hải quân",
    "air force": "không quân",
    "soldier": "chiến sĩ",
    "military officer": "sĩ quan",
    "weapon": "vũ khí",
    "ammunition": "đạn dược",
    "strategy": "chiến lược",
    "tactics": "chiến thuật",
    "alliance": "liên minh",
    "ceasefire": "ngừng bắn",
    "opening of hostilities": "mở đầu chiến sự",
    "in hot pursuit": "truy đuổi gấp",
    "being in hot pursuit": "đang truy đuổi",
    "on the defensive": "thủ thế",

    # ── Nông nghiệp / thực phẩm ──
    "agriculture": "nông nghiệp",
    "farming": "canh tác",
    "harvest": "thu hoạch",
    "crop": "cây trồng",
    "fertilizer": "phân bón",
    "extra fertilizer": "bón thêm phân",
    "adding extra fertilizer": "bón thêm phân",
    "rice field": "ruộng lúa",
    "fishery": "ngư nghiệp",
    "fisheries agency": "cục ngư nghiệp",
    "dried sardines": "cá mòi khô",
    "small crunchy dried sardines": "cá cơm khô",
    "something cooked with rice": "đồ ấu cùng cơm",
    "finely chopped": "thái nhỏ",

    # ── Thể thao ──
    "sumo wrestling": "đấu sumo",
    "wrestling": "đấu vật",
    "martial arts": "võ thuật",
    "competition": "cuộc thi đấu",
    "tournament": "giải đấu",
    "championship": "giải vô địch",
    "match": "trận đấu",
    "game of go": "ván cờ Go",
    "playing a game of go": "chơi cờ Go",
    "playing a game": "chơi ván cờ",

    # ── Đồ vật / dụng cụ ──
    "fountain pen": "bút máy",
    "measuring ruler": "thước đo",
    "ruler": "thước kẻ",
    "compass": "compa",
    "bookshelf": "kệ sách",
    "luggage rack": "giá để hành lý",
    "wire entanglements": "hàng rào dây thép gai",
    "barbed wire": "dây thép gai",
    "construction": "xây dựng",
    "addition to a building": "công trình bổ sung",

    # ── Thiên văn / địa lý ──
    "jupiter": "sao Mộc",
    "jupiter planet": "hành tinh Mộc tinh",
    "planet": "hành tinh",
    "solar system": "hệ mặt trời",
    "northern extremity": "cực bắc",
    "built on sand": "xây trên cát",
    "russian maritime provinces": "vùng duyên hải Nga",
    "maritime provinces": "vùng duyên hải",

    # ── Cây cỏ / sinh vật ──
    "japanese spindletree": "cây vệ mao Nhật",
    "spindletree": "cây vệ mao",
    "euonymus japonicus": "cây vệ mao Nhật",
    "hornbeam": "cây thùa",
    "birch": "cây bạch dương",
    "age of a tree": "tuổi cây",
    "fishery resource": "nguồn thủy sản",
    "air bubble": "bọt khí",
    "bubble in a liquid": "bọt khí trong chất lỏng",

    # ── Hành động / trạng thái ──
    "paying a great deal of attention": "chú ý đặc biệt",
    "paying great attention": "chú ý nhiều",
    "paying attention": "chú ý",
    "-nth time": "lần thứ n",
    "corner of one's eye": "khóe mắt",
    "coming and going": "qua lại",
    "go and return": "đi về",
    "in one's possession": "trong tay, sở hữu",
    "keeping a low profile": "giữ thái độ khiêm tốn",
    "low profile": "thái độ khiêm tốn",
    "not altogether": "không hẳn là",
    "on the street": "trên đường phố",
    "according to someone": "theo ai đó",
    "act of barbarity": "hành động man rợ",
    "accepting with pleasure": "vui vẻ chấp nhận",
    "accompanying on a trip": "đi kèm chuyến du lịch",
    "after one's death": "sau khi chết",
    "consign to oblivion": "đưa vào quên lãng",
    "to consign to oblivion": "đưa vào quên lãng",
    "carrying out": "thực hiện",
    "being on the defensive": "ở thế thủ",
    "death by hanging": "tử hình bằng treo cổ",
    "suffering an emotional disturbance": "rối loạn cảm xúc",
    "talking in a half-joking manner": "nói nửa đùa nửa thật",
    "while working in or at or for": "trong lúc làm việc tại",
    "husband and wife earning a living together": "vợ chồng cùng làm kiếm sống",

    # ── Chức danh / tổ chức ──
    "government": "chính phủ",
    "association formed to carry out an objective": "hiệp hội thực hiện mục tiêu",
    "association": "hiệp hội",
    "agency for cultural affairs": "cục văn hóa",
    "japanese fisheries agency": "cục thủy sản Nhật",
    "japanese national land agency": "cục địa chính Nhật",
    "japanese postal savings bureau": "cục tiết kiệm bưu chính",
    "japanese tax bureau": "cục thuế Nhật",
    "japanese imperial army": "quân đội Hoàng gia Nhật",
    "former ministry of health and welfare": "bộ y tế và phúc lợi cũ",
    "governmental supervisor of teachers": "chuyên viên tư vấn giáo dục",
    "company announcement": "thông báo công ty",
    "social welfare": "phúc lợi xã hội",
    "air traffic controller": "kiểm soát không lưu",

    # ── Pháp lý / hành chính đặc biệt ──
    "abstention from voting": "bỏ phiếu trắng",
    "abstention": "bỏ phiếu trắng",
    "adoption or rejection": "chấp thuận hay từ chối",
    "advancing to the first grade": "thăng hạng vào vòng đầu",
    "acupuncture and moxibustion": "châm cứu và ngải cứu",
    "abolition of licensed prostitution": "bãi bỏ mại dâm có giấy phép",
    "administration of medicine": "cho uống thuốc",
    "administrative": "hành chính",
    "having life-and-death power over": "có quyền sinh sát",
    "life-and-death power": "quyền sinh sát",
    "its own accord": "tự nguyện",
    "a bad debt": "nợ khó đòi",
    "a fine thing to say": "lời hay",
    "a long time since the last time": "lâu rồi không gặp",
    "a long time": "rất lâu",
    "a metal reinforcement": "thanh kim loại gia cố",
    "a palace sanctuary": "điện thờ hoàng gia",
    "a route or passage": "tuyến đường, hành trình",
    "a seal affixed to a document": "con dấu trên văn bản",
    "a third country": "nước thứ ba",
    "a third force": "lực lượng thứ ba",
    "absolute majority": "đa số tuyệt đối",
    "diversification": "đa dạng hóa",
    "arc": "cung tròn",
    "1000 yen": "1000 yên",
    "1,000 yen bill": "tờ 1000 yên",
    "all means": "mọi phương tiện",
    "20 percent": "20%",
    "30 percent": "30%",
    "40 percent": "40%",
    "50 percent": "50%",
    "universal": "phổ quát",
    "cross for crucifixion": "cây thánh giá",
    "cross": "chữ thập",
    "crucifixion": "bị đóng đinh thập giá",
    "kaleidoscope": "kính vạn hoa",
    "double feature movie": "chiếu hai phim liên tiếp",
    "approval": "sự chấp thuận",
    "national policy": "chính sách quốc gia",
    "right or wrong": "đúng hay sai",
    "exemplary": "mẫu mực",
    "extensive": "rộng rãi",
    "living": "cuộc sống",
    "lively": "sôi nổi",
    "being helped": "được giúp đỡ",
    "towns and villages": "thị trấn và làng xã",
    "ecuador": "Ecuador",
    "1962 trade agreement between japan and china": "hiệp định thương mại Nhật-Trung 1962",
    "degree of freshness": "độ tươi",
    "freshness": "độ tươi",
    "encouragement of industry": "khuyến khích công nghiệp",
    "science of agriculture": "khoa học nông nghiệp",
    "single-industry industrial union": "liên đoàn công nghiệp đơn ngành",
    "edo-period town magistrate": "quan đô trưởng thời Edo",
    "construction of an argument": "lập luận",
    "right-wing propaganda truck": "xe tuyên truyền cánh hữu",
    "under metropolitan government management": "do thành phố quản lý",
    "under prefectural management": "do tỉnh quản lý",
    "movie distribution rights": "quyền phân phối phim",
    "degree of freshness": "mức độ tươi",
    "abstract or impracticable theory": "lý thuyết không thực tiễn",
    "at a very slow speed": "ở tốc độ rất chậm",
    "season of winter": "mùa đông",
    "affection esp parental": "tình cảm yêu thương",
    "affection": "tình cảm",
    "parental affection": "tình yêu của cha mẹ",
    "after the end of something": "sau khi kết thúc",
    "feelings of love": "cảm xúc yêu đương",
    "having life-and-death power": "có quyền sinh tử",
    "fish climbing up waterfall": "cá vượt thác",
    "governmental supervisor": "giám sát viên chính phủ",
    "britain's lord privy seal": "Quốc tỷ thư ký Anh",
}

# ══════════════════════════════════════════════════════════════════
# PATTERN-BASED TRANSLATION
# ══════════════════════════════════════════════════════════════════
PATTERNS = [
    (r'^(\d+)th anniversary$', lambda m: f"kỷ niệm lần thứ {m.group(1)}"),
    (r'^(\d+)th year$', lambda m: f"năm thứ {m.group(1)}"),
    (r'^(\d+) years? old$', lambda m: f"{m.group(1)} tuổi"),
    (r'^(\d+) (yen|en)$', lambda m: f"{m.group(1)} yên"),
    (r'^(\d+),000 yen', lambda m: f"{m.group(1).replace(',','')}000 yên"),
    (r'^first (.+)$', lambda m: f"lần đầu {m.group(1).lower()}" if len(m.group(1)) < 30 else None),
    (r'^old (.+)$', lambda m: f"{m.group(1)} cũ"),
    (r'^new (.+)$', lambda m: f"{m.group(1)} mới"),
    (r'^(.+) system$', lambda m: f"hệ thống {m.group(1)}"),
    (r'^(.+) method$', lambda m: f"phương pháp {m.group(1)}"),
    (r'^(.+) policy$', lambda m: f"chính sách {m.group(1)}"),
    (r'^(.+) problem$', lambda m: f"vấn đề {m.group(1)}"),
    (r'^(.+) issue$', lambda m: f"vấn đề {m.group(1)}"),
    (r'^the (.+)$', lambda m: m.group(1)),
]

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def has_viet(s):
    return bool(re.search(r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
                           r'ÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]', s))

def is_jp(s):
    return bool(re.search(r'[぀-ヿ一-鿿]', s))

def is_english(s):
    if not s: return False
    if has_viet(s) or is_jp(s): return False
    s_clean = s.strip()
    if not re.match(r'^[a-zA-Z\s\-\(\)\/\.,\'\"0-9\%\+]+$', s_clean): return False
    if len(s_clean) <= 3: return False
    known_short_vi = {
        'hoa','mua','hai','ba','mot','tay','mat','tai','chan','bung',
        'lung','vai','an','di','ve','lon','nho','cao','dai','ten',
        'tri','duc','tu','vo','so','ky','khi','thu','to','la',
    }
    s_lower = s_clean.lower()
    if s_lower in known_short_vi: return False
    en_words = set(re.split(r'[\s\(\)\-\/,\.\'\"\%]+', s_lower))
    en_words.discard('')
    EN_MARKERS = {
        'the','a','an','of','in','on','at','to','for','with','by',
        'from','and','or','not','is','are','was','were','be','been',
        'have','has','that','this','which','who','one','two','three',
        'four','five','six','seven','eight','nine','ten','person',
        'people','thing','place','time','way','day','year','make',
        'take','get','go','come','see','know','think','look','good',
        'bad','big','small','large','new','old','high','low',
        'national','general','special','main','local','school',
        'university','company','government','family','opening',
        'closing','finely','chopped','microscopic','extensive',
        'exemplary','universal','heresy','hornbeam','bookshelf',
        'construction','crucifixion','sumo','fountain','pen',
        'measuring','ruler','jupiter','planet','spindletree',
        'approval','policy','hostilities','northern','extremity',
        'absolute','majority','diversification','imagination',
        'agriculture','industry','profile','towns','villages',
        'percent','feature','double','exposure','association',
        'resuscitation','living','lively','helped','paying',
        'attention','formed','carry','objective','last','next',
        'month','week','profile','former','under','metropolitan',
        'prefectural','governmental','supervisor','abstract',
        'impracticable','theory','abolition','prostitution',
        'licensed','affection','parental','season','winter',
        'summer','autumn','spring','birth','death','war','battle',
        'army','navy','force','soldier','military','weapon',
        'strategy','alliance','ceasefire','hospital','clinic',
        'surgery','diagnosis','prescription','medicine','drug',
        'vaccination','epidemic','symptom','treatment','recovery',
        'disease','infection','fracture','bleeding','emergency',
        'ambulance','rehabilitation','earthquake','tsunami','flood',
        'drought','typhoon','volcanic','landslide','rainfall',
        'snowfall','temperature','humidity','forecast','traffic',
        'accident','signal','pedestrian','crossing','railway',
        'departure','arrival','transfer','commute','driving',
        'license','expressway','highway','marriage','divorce',
        'adoption','inheritance','funeral','ceremony','child',
        'brother','sister','husband','wife','newlyweds','market',
        'exchange','securities','investment','interest','rate',
        'inflation','deflation','recession','economic','growth',
        'trade','balance','export','import','tariff','bankruptcy',
        'debt','loan','mortgage','budget','revenue','profit',
        'loss','dividend','currency','stock',
    }
    if any(w in EN_MARKERS for w in en_words): return True
    if len(en_words) >= 3: return True
    return False

def lookup(en_text):
    """Tìm trong dict, strip ngoặc đơn nếu cần."""
    t = en_text.strip()
    t_lower = t.lower()
    if t_lower in EN_VI: return EN_VI[t_lower]
    # Bỏ nội dung trong ngoặc (đầu)
    t2 = re.sub(r'^\([^)]*\)\s*', '', t_lower).strip()
    if t2 in EN_VI: return EN_VI[t2]
    # Bỏ ngoặc ở cuối
    t3 = re.sub(r'\s*\([^)]*\)\s*$', '', t_lower).strip()
    if t3 in EN_VI: return EN_VI[t3]
    # Tìm key nào là substring dài nhất trong t_lower
    best = None
    best_len = 0
    for k, v in EN_VI.items():
        if k in t_lower and len(k) > best_len:
            best = v; best_len = len(k)
    if best: return best
    # Pattern matching
    for pattern, fn in PATTERNS:
        m = re.match(pattern, t_lower)
        if m:
            result = fn(m)
            if result: return result
    return None

# ══════════════════════════════════════════════════════════════════
# PARSE & WRITE kanji-data.js
# ══════════════════════════════════════════════════════════════════
def parse_js(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    # Tách header và footer
    ka_start = raw.index('const ALL_KANJI = [')
    ka_end   = raw.rindex('];') + 2
    header   = raw[:ka_start]
    footer   = raw[ka_end:]
    body     = raw[ka_start + len('const ALL_KANJI = ['):ka_end - 2]

    lines    = []
    entries  = []
    for line in body.splitlines():
        s = line.strip()
        if not s: continue
        lines.append(line)
        if s.startswith('{kanji:') or s.startswith('// ====='):
            entries.append(s)
        else:
            entries.append(s)
    return raw, header, footer, body

def fix_js(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    ka_start = content.index('const ALL_KANJI = [')
    ka_end   = content.rindex('];') + 2
    header   = content[:ka_start]
    footer   = content[ka_end:]

    # Xử lý từng dòng entry
    lines_in  = content[ka_start + len('const ALL_KANJI = ['):ka_end - 2].splitlines()
    lines_out = []

    fixed_count   = 0
    removed_count = 0
    skipped_count = 0

    for raw_line in lines_in:
        s = raw_line.strip()
        if not s or s.startswith('//'):
            lines_out.append(raw_line)
            continue

        # Cố gắng parse entry JSON
        s_noc = s.rstrip(',')
        try:
            j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:(?!\s*[/]))', r'"\1"', s_noc)
            obj = json.loads(j)
        except Exception:
            lines_out.append(raw_line)
            skipped_count += 1
            continue

        words   = obj.get('words', [])
        changed = False
        new_words = []

        for w in words:
            m_text = w.get('m', '')
            if is_english(m_text):
                vi = lookup(m_text)
                if vi:
                    new_w = dict(w)
                    new_w['m'] = vi
                    new_words.append(new_w)
                    print(f"  [{obj.get('kanji','?')}] \"{w.get('w','')}\" → \"{vi}\"")
                    fixed_count += 1
                    changed = True
                else:
                    # Xoá word này
                    removed_count += 1
                    changed = True
            else:
                new_words.append(w)

        if changed:
            # Giữ ít nhất 1 word nếu ban đầu có word
            if len(new_words) == 0 and len(words) > 0:
                new_words = [words[0]]  # fallback: giữ word đầu tiên
            obj['words'] = new_words

        # Rebuild dòng
        line_new = rebuild_line(obj)
        has_comma = s.endswith(',')
        lines_out.append(line_new + (',' if has_comma else ''))

    # Ráp lại
    new_content = header + 'const ALL_KANJI = [\n' + '\n'.join(lines_out) + '\n];' + footer
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return fixed_count, removed_count, skipped_count

def rebuild_line(obj):
    """Rebuild một object thành JS line."""
    FIELDS = ['kanji','hanviet','on','kun','meaning','meaning_jp','level','strokes','words']
    parts = []
    for key in FIELDS:
        if key not in obj: continue
        val = obj[key]
        if val is None: continue
        if isinstance(val, str):
            esc = val.replace('\\', '\\\\').replace('"', '\\"')
            parts.append(f'{key}:"{esc}"')
        elif isinstance(val, list):
            arr = json.dumps(val, ensure_ascii=False, separators=(',', ':'))
            parts.append(f'{key}:{arr}')
        elif isinstance(val, (int, float)):
            parts.append(f'{key}:{val}')
    return '{' + ','.join(parts) + '}'

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print(f'📂 Đọc: {JS_PATH}')
    fixed, removed, skipped = fix_js(JS_PATH)
    print(f'\n✅ Kết quả:')
    print(f'   Đã dịch : {fixed} nghĩa')
    print(f'   Đã xoá  : {removed} entry không dịch được')
    print(f'   Bỏ qua  : {skipped} dòng parse lỗi')
    print(f'💾 Ghi xong → {JS_PATH}')
