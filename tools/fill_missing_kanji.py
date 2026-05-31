"""
KOERU — Fill missing JLPT kanji for N3 and N4
1. Tìm kanji thiếu (so với kanjidic2 chuẩn)
2. Tìm kanji bị gán nhầm level (N3 → bị để ở N2)
3. Generate entry đầy đủ và append vào kanji-data-nX.js
4. Cập nhật kanji-data.js tổng hợp

Usage:
  python tools/fill_missing_kanji.py
"""

import re, json, time, urllib.request
from pathlib import Path

ROOT   = Path(__file__).parent.parent
JS_DIR = ROOT / "js"

# ── Hán Việt mapping từ On'yomi ───────────────────────────────────────────────
# Ánh xạ âm On → Hán Việt (dựa theo bảng tương đồng Hán Việt - Nhật)
ON_TO_HV = {
    # A
    'ア':'A','アイ':'AI','アク':'ÁC','アン':'AN',
    # I
    'イ':'Y','イキ':'ÍCH','イチ':'NHẤT','イツ':'NHẤT','イン':'ÂM',
    # U
    'ウ':'VŨ','ウン':'VẬN',
    # E
    'エイ':'ANH','エン':'VIÊN',
    # O
    'オウ':'VƯƠNG','オク':'ỨC','オン':'ÂN',
    # KA
    'カ':'HÁ','カイ':'GIỚI','カク':'CÁCH','カン':'CAN','ガ':'NGÃ','ガイ':'NGOẠI','ガク':'NHẠC','ガン':'NHAM',
    # KI
    'キ':'KỲ','キク':'CÚC','キャク':'KHÁCH','キュウ':'CỨU','キョ':'CỰ','キョウ':'CỘNG','キン':'CẦN','ギ':'NGHĨA','ギャク':'NGHỊCH','ギョ':'NGƯ','ギン':'NGÂN',
    # KU
    'ク':'CU','クウ':'KHÔNG','グ':'NGŨ','グン':'QUÂN',
    # KE
    'ケイ':'KÍNH','ケツ':'QUYẾT','ケン':'KIÊN','ゲイ':'NGHỆ','ゲン':'NGUYÊN',
    # KO
    'コ':'CỐ','コウ':'CÔNG','コク':'CỐC','コツ':'CỐT','コン':'CĂN','ゴ':'NGỌ','ゴウ':'HÀO','ゴク':'CỰC','ゴン':'QUYỀN',
    # SA
    'サ':'TẢ','サイ':'TẾ','サク':'SÁCH','サツ':'SÁT','サン':'TAM','ザ':'TẠ','ザイ':'TÀI','ザン':'TÀN',
    # SI/SHI
    'シ':'CHỈ','シキ':'SẮC','シチ':'THẤT','シャ':'XÁ','シャク':'THÍCH','シュ':'THỦ','シュウ':'TẬP','シュン':'XUÂN','ショ':'SƠ','ショウ':'TIỂU','ショク':'THỰC','シン':'TÂM','ジ':'TỰ','ジキ':'TRỰC','ジツ':'THỰC','ジャク':'NHƯỢC','ジュ':'NHU','ジュウ':'THẬP','ジュン':'THUẦN','ジョ':'TRỢ','ジョウ':'THƯỢNG','ジン':'NHÂN',
    # SU
    'ス':'TỐ','スイ':'THỦY','スウ':'SỐ','ズ':'ĐỒ',
    # SE
    'セイ':'TINH','セキ':'TỊCH','セツ':'TIẾT','セン':'TIÊN','ゼイ':'THUẾ','ゼン':'THIỆN',
    # SO
    'ソ':'TỔ','ソウ':'TỔNG','ソク':'TỨC','ソツ':'SUẤT','ゾウ':'TƯỢNG','ゾク':'TỘC',
    # TA
    'タ':'ĐA','タイ':'ĐẠI','タク':'TRẠCH','タン':'ĐAN','ダ':'ĐÀ','ダイ':'ĐẠI','ダン':'ĐÀN',
    # TI/CHI
    'チ':'TRI','チク':'TRÚC','チャ':'TRÀ','チュウ':'TRUNG','チョ':'TRỮ','チョウ':'ĐIỂU','チン':'TRÂN',
    # TU/TSU
    'ツイ':'TRUY','テイ':'ĐỀ','テキ':'ĐỊCH','テツ':'THIẾT','テン':'THIÊN','デイ':'NÊ','デン':'ĐIỀN',
    # TO
    'ト':'ĐỒ','トウ':'ĐÁO','トク':'ĐỨC','トン':'ĐỐN','ド':'ĐỘ','ドウ':'ĐẠO','ドク':'ĐỘC',
    # NA
    'ナ':'NA','ナイ':'NỘI','ナン':'NAN',
    # NI
    'ニ':'NHỊ','ニク':'NHỤC','ニチ':'NHẬT','ニュウ':'NHẬP','ニン':'NHÂN',
    # NU/NE/NO
    'ネン':'NIÊN','ノウ':'NĂNG',
    # HA
    'ハ':'BÁT','ハイ':'BỐI','ハク':'BẠCH','ハツ':'PHÁT','ハン':'BÁN','バ':'MÃ','バイ':'BỘI','バク':'MẠC','バン':'VẠN',
    # HI
    'ヒ':'PHI','ヒキ':'BÚT','ヒツ':'TẤT','ヒャク':'BÁCH','ヒョウ':'BÌNH','ヒン':'PHẨM','ビ':'MỸ','ビョウ':'BỆNH','ビン':'BẦN',
    # HU/FU
    'フ':'PHÚ','フウ':'PHONG','フク':'PHÚC','フン':'PHẦN','ブ':'VŨ','ブン':'VĂN',
    # HE/HO
    'ヘイ':'BÌNH','ヘン':'BIẾN','ボ':'MỘ','ボウ':'MẪU','ボク':'MỤC','ボン':'BỔN','ホ':'BỔ','ホウ':'PHƯƠNG','ホン':'BỔN',
    # MA
    'マ':'MA','マイ':'MUỘI','マン':'VẠN','バ':'BA',
    # MI
    'ミ':'VỊ','ミャク':'MẠCH','ミン':'DÂN',
    # MU/ME/MO
    'ム':'VÔ','メイ':'MINH','モウ':'MỘNG','モク':'MỘC','モン':'VĂN',
    # YA/YU/YO
    'ヤ':'DÃ','ユ':'DO','ユウ':'HỮU','ヨ':'DƯ','ヨウ':'DƯƠNG','ヨク':'DỤC',
    # RA/RI/RU/RE/RO
    'ラ':'LA','ライ':'LAI','ラク':'LẠC','ラン':'LAN','リ':'LÝ','リキ':'LỰC','リク':'LỤC','リツ':'LUẬT','リャク':'LƯỢC','リュウ':'LƯU','リョ':'LỮ','リョウ':'LƯỢNG','リン':'LÂM','ル':'LỮ','レイ':'LỄ','レキ':'LỊCH','レツ':'LIỆT','レン':'LIÊN','ロ':'LỘ','ロウ':'LÃO','ロク':'LỤC','ロン':'LUẬN',
    # WA
    'ワ':'HÒA','ワン':'HOÀN',
}

MEANING_VI = {
    # Từ điển Anh→Việt cơ bản cho meanings từ kanjidic
    'evening':'buổi tối','sunset':'hoàng hôn','stand':'đứng','platform':'bục; khu',
    'desk':'bàn','writing':'viết','copy':'sao chép','town':'thị trấn','self':'tự',
    'oneself':'bản thân','death':'chết','die':'chết','capital':'thủ đô','picture':'hình',
    'painting':'tranh vẽ','room':'phòng','reason':'lý do','logic':'lý luận','by means of':'bằng',
    'house':'nhà','reside':'ở','study':'nghiên cứu','place':'nơi; địa điểm','morning':'buổi sáng',
    'shop':'cửa hàng','degree':'độ; mức','hold':'giữ','world':'thế giới','departure':'khởi hành',
    'fat':'béo; to lớn','number':'số','neck':'cổ','people':'dân','record':'ghi chép',
    'picture':'tranh; hình','number':'số','place':'nơi','reality':'thực tế','part':'phần',
    'guest':'khách','advance':'tiến lên','leaf':'lá','most':'nhất; tối','rank':'hạng',
    'convenience':'thuận tiện; tiện lợi','voice':'giọng; tiếng','straight':'thẳng',
    'subject':'môn học','science':'khoa học','head':'đầu','citizen':'công dân; dân',
    'write':'viết','drawing':'vẽ; bức tranh','number':'số đếm','actual':'thực tế',
    'section':'bộ phận','reality':'thực tế; sự thật','progress':'tiến bộ','word':'từ',
    'highest':'cao nhất; tối cao','position':'vị trí; thứ hạng',
    'letter':'thư; chữ cái','correspondence':'thư từ; trao đổi',
    'circle':'vòng tròn','circumference':'chu vi','round':'tròn',
    'return':'trở về; hoàn lại','direct':'thẳng; trực tiếp',
    'nature':'thiên nhiên; tự nhiên','origin':'nguồn gốc','original':'gốc',
    'country':'đất nước; quốc gia','district':'khu vực','area':'vùng',
    'time':'thời gian','period':'giai đoạn','age':'tuổi; thời đại',
    'mix':'trộn lẫn','combine':'kết hợp',
    'begin':'bắt đầu','start':'khởi đầu',
    'finish':'kết thúc; hoàn thành','complete':'hoàn chỉnh',
    'thing':'vật; thứ','matter':'vấn đề','fact':'sự thật',
    'big':'lớn','large':'to lớn','great':'vĩ đại',
    'small':'nhỏ','little':'ít; nhỏ',
    'old':'cũ; già','ancient':'cổ xưa',
    'new':'mới','fresh':'tươi mới',
    'high':'cao','expensive':'đắt tiền',
    'low':'thấp','cheap':'rẻ',
    'long':'dài','leader':'thủ lĩnh',
    'short':'ngắn','brief':'vắn tắt',
    'strong':'mạnh','powerful':'hùng mạnh',
    'weak':'yếu','frail':'mỏng manh',
    'good':'tốt; hay','fine':'đẹp',
    'bad':'xấu; tồi','evil':'ác',
    'beautiful':'đẹp','pretty':'xinh',
    'ugly':'xấu xí',
    'fast':'nhanh','quick':'mau',
    'slow':'chậm','sluggish':'uể oải',
    'hot':'nóng','warm':'ấm',
    'cold':'lạnh; lạnh lẽo',
    'many':'nhiều','much':'nhiều',
    'few':'ít','little':'ít',
    'all':'tất cả','every':'mọi',
    'half':'một nửa','middle':'giữa; trung',
    'heaven':'trời; thiên đường','sky':'bầu trời',
    'earth':'đất; trái đất','ground':'mặt đất',
    'water':'nước','river':'sông',
    'fire':'lửa','flame':'ngọn lửa',
    'tree':'cây','wood':'gỗ',
    'mountain':'núi','hill':'đồi',
    'field':'đồng ruộng; cánh đồng',
    'rice field':'ruộng lúa',
    'flower':'hoa','blossom':'nở hoa',
    'grass':'cỏ','plant':'cây cỏ',
    'animal':'động vật','beast':'thú',
    'bird':'chim','fowl':'gia cầm',
    'fish':'cá','seafood':'hải sản',
    'person':'người','human':'con người',
    'man':'đàn ông; nam','male':'nam tính',
    'woman':'phụ nữ; nữ','female':'nữ tính',
    'child':'trẻ em; con','kid':'đứa trẻ',
    'father':'cha; bố','dad':'ba',
    'mother':'mẹ','mom':'mẹ',
    'brother':'anh em','sibling':'anh chị em',
    'sister':'chị em gái',
    'friend':'bạn bè','companion':'bạn đồng hành',
    'teacher':'giáo viên','instructor':'người hướng dẫn',
    'student':'học sinh','pupil':'học trò',
    'king':'vua','ruler':'người cai trị',
    'country':'quốc gia','nation':'dân tộc',
    'language':'ngôn ngữ; tiếng','word':'từ ngữ',
    'read':'đọc','reading':'việc đọc',
    'write':'viết','writing':'chữ viết',
    'speak':'nói','say':'nói; bảo',
    'listen':'nghe','hear':'nghe thấy',
    'see':'nhìn; thấy','look':'nhìn; trông',
    'go':'đi','come':'đến',
    'eat':'ăn','food':'thức ăn',
    'drink':'uống','beverage':'đồ uống',
    'buy':'mua','purchase':'mua sắm',
    'sell':'bán','sale':'buôn bán',
    'enter':'vào; nhập','insert':'chèn vào',
    'exit':'ra; xuất','leave':'rời đi',
    'up':'lên; trên','above':'ở trên',
    'down':'xuống; dưới','below':'ở dưới',
    'left':'trái','right':'phải',
    'north':'phía bắc','south':'phía nam',
    'east':'phía đông','west':'phía tây',
    'front':'trước; mặt trước','back':'sau; phía sau',
    'inside':'bên trong','outside':'bên ngoài',
    'one':'một','two':'hai','three':'ba',
    'four':'bốn','five':'năm','six':'sáu',
    'seven':'bảy','eight':'tám','nine':'chín','ten':'mười',
    'hundred':'trăm','thousand':'nghìn','ten thousand':'vạn',
    'year':'năm','month':'tháng','day':'ngày',
    'hour':'giờ','minute':'phút','second':'giây',
    'spring':'mùa xuân','summer':'mùa hè','autumn':'mùa thu','winter':'mùa đông',
    'sun':'mặt trời','moon':'mặt trăng','star':'ngôi sao',
    'rain':'mưa','snow':'tuyết','wind':'gió',
    'road':'con đường; đường','street':'phố; đường phố',
    'school':'trường học','university':'đại học',
    'hospital':'bệnh viện','clinic':'phòng khám',
    'station':'ga tàu; trạm','train':'tàu hỏa',
    'car':'ô tô; xe hơi','vehicle':'phương tiện',
    'airplane':'máy bay','fly':'bay',
    'boat':'thuyền','ship':'tàu',
    'money':'tiền','gold':'vàng','silver':'bạc',
    'price':'giá cả','cost':'chi phí',
    'work':'làm việc; công việc','job':'nghề; việc làm',
    'company':'công ty','business':'kinh doanh',
    'heart':'trái tim; tâm','mind':'tâm trí',
    'body':'cơ thể','health':'sức khỏe',
    'life':'cuộc sống; sinh mệnh','live':'sống',
    'die':'chết; tử vong',
    'love':'tình yêu; yêu thương','like':'thích',
    'hate':'ghét','dislike':'không thích',
    'happy':'hạnh phúc; vui','joy':'niềm vui',
    'sad':'buồn','sorrow':'nỗi buồn',
    'pain':'đau','suffer':'chịu đựng',
    'think':'suy nghĩ','thought':'ý nghĩ',
    'know':'biết','knowledge':'kiến thức',
    'learn':'học; học hỏi','study':'học tập',
    'teach':'dạy','education':'giáo dục',
    'use':'dùng; sử dụng','utilize':'tận dụng',
    'make':'làm; tạo','create':'sáng tạo',
    'build':'xây dựng','construct':'kiến tạo',
    'break':'phá vỡ; gãy','destroy':'phá hủy',
    'open':'mở','close':'đóng',
    'start':'bắt đầu','begin':'khởi đầu',
    'end':'kết thúc; cuối','finish':'hoàn thành',
    'send':'gửi','receive':'nhận',
    'give':'cho; tặng','take':'lấy; nhận',
    'wait':'chờ; đợi','expect':'mong đợi',
    'meet':'gặp; gặp gỡ','gather':'tụ tập',
    'separate':'tách; chia','divide':'chia',
    'join':'tham gia; nối','connect':'kết nối',
    'cut':'cắt','separate':'phân chia',
    'hit':'đánh; đập','strike':'đánh',
    'pull':'kéo','push':'đẩy',
    'carry':'mang; vác','bring':'mang lại',
    'throw':'ném','catch':'bắt',
    'run':'chạy','walk':'đi bộ',
    'stand':'đứng','sit':'ngồi',
    'sleep':'ngủ','wake':'thức dậy',
    'cry':'khóc','laugh':'cười',
    'shout':'la hét; gọi to','call':'gọi',
    'answer':'trả lời','question':'câu hỏi',
    'count':'đếm','measure':'đo; đo lường',
    'heavy':'nặng','light':'nhẹ; ánh sáng',
    'thick':'dày','thin':'mỏng',
    'wide':'rộng','narrow':'hẹp',
    'near':'gần','far':'xa',
    'early':'sớm','late':'muộn; trễ',
    'easy':'dễ','difficult':'khó',
    'busy':'bận rộn','free':'tự do; rảnh',
    'alone':'một mình','together':'cùng nhau',
    'special':'đặc biệt','ordinary':'bình thường',
    'important':'quan trọng','necessary':'cần thiết',
    'possible':'có thể','impossible':'không thể',
    'true':'thật; đúng','false':'sai; giả',
    'correct':'đúng; chính xác','wrong':'sai',
    'clean':'sạch; trong sạch','dirty':'bẩn',
    'bright':'sáng; rạng rỡ','dark':'tối',
    'quiet':'yên tĩnh','noisy':'ồn ào',
    'soft':'mềm; nhẹ nhàng','hard':'cứng; khó',
    'public':'công cộng','private':'riêng tư',
    'ancient':'cổ đại; xưa','modern':'hiện đại',
    'foreign':'nước ngoài','domestic':'trong nước',
    'international':'quốc tế','global':'toàn cầu',
    'culture':'văn hóa','art':'nghệ thuật',
    'music':'âm nhạc','song':'bài hát',
    'game':'trò chơi','play':'chơi',
    'sport':'thể thao','exercise':'tập thể dục',
    'food':'thức ăn','meal':'bữa ăn',
    'rice':'cơm; gạo','bread':'bánh mì',
    'meat':'thịt','vegetable':'rau củ',
    'fruit':'trái cây','sweet':'ngọt; kẹo',
    'clothes':'quần áo; trang phục','wear':'mặc',
    'color':'màu sắc','red':'đỏ','blue':'xanh','green':'xanh lá',
    'white':'trắng','black':'đen','yellow':'vàng',
    'size':'kích thước; cỡ','shape':'hình dạng',
    'line':'đường kẻ; hàng','circle':'hình tròn',
    'point':'điểm; chấm','surface':'bề mặt',
    'door':'cửa','window':'cửa sổ',
    'wall':'tường; vách','floor':'sàn nhà; tầng',
    'garden':'khu vườn; sân','park':'công viên',
    'city':'thành phố','town':'thị trấn',
    'village':'làng; thôn','countryside':'nông thôn',
    'government':'chính phủ','law':'luật pháp',
    'society':'xã hội','community':'cộng đồng',
    'history':'lịch sử','tradition':'truyền thống',
    'religion':'tôn giáo','belief':'niềm tin',
    'science':'khoa học','technology':'công nghệ',
    'nature':'thiên nhiên','environment':'môi trường',
}


def meanings_to_vi(meanings_en: list) -> str:
    """Convert English meanings to Vietnamese."""
    results = []
    for m in meanings_en[:3]:
        ml = m.lower().strip()
        # Direct lookup
        if ml in MEANING_VI:
            results.append(MEANING_VI[ml])
            continue
        # Partial match
        found = False
        for k, v in MEANING_VI.items():
            if k in ml or ml in k:
                results.append(v)
                found = True
                break
        if not found:
            # Fallback: keep English (needs manual review)
            results.append(m)
    return '; '.join(dict.fromkeys(results))  # dedupe


def on_to_hanviet(on_readings: list) -> str:
    """Convert On'yomi to Hán Việt."""
    if not on_readings:
        return ''
    # Take first On reading
    on = on_readings[0].upper()
    # Direct lookup
    if on in ON_TO_HV:
        return ON_TO_HV[on]
    # Try prefix match
    for k, v in sorted(ON_TO_HV.items(), key=lambda x: -len(x[0])):
        if on.startswith(k):
            return v
    return on  # fallback: return romaji


def get_sample_words(kanji: str, level: str) -> list:
    """Tạo từ mẫu cơ bản từ các pattern phổ biến."""
    # Không thể fetch JMdict dễ dàng → trả về list rỗng
    # Sẽ được bổ sung thủ công sau
    return []


def generate_entry(kanji: str, kd_data: dict, level: str) -> dict:
    """Generate KOERU entry from kanjidic2 data."""
    on_list  = kd_data.get('readings_on', [])
    kun_list = kd_data.get('readings_kun', [])
    meanings = kd_data.get('meanings', [])

    on_str  = '、'.join(on_list[:3])
    kun_str = '、'.join(k.replace('-','').split('.')[0] for k in kun_list[:3])

    meaning_vi = meanings_to_vi(meanings)
    hanviet    = on_to_hanviet(on_list)

    return {
        'kanji':    kanji,
        'hanviet':  hanviet,
        'on':       on_str,
        'kun':      kun_str,
        'meaning':  meaning_vi,
        'meaning_jp': '、'.join(meanings[:2]),
        'level':    level,
        'words':    [],
        'stroke':   kd_data.get('strokes', 0),
        'freq_rank':kd_data.get('freq', 9999),
        'grade':    kd_data.get('grade', 0),
        'radical':  '',
        'parts':    [],
    }


def entry_to_js(e: dict) -> str:
    """Convert entry dict to JS object string."""
    words_js = json.dumps(e['words'], ensure_ascii=False)
    parts_js = json.dumps(e['parts'], ensure_ascii=False)
    return (
        f'{{kanji:"{e["kanji"]}",'
        f'hanviet:"{e["hanviet"]}",'
        f'on:"{e["on"]}",'
        f'kun:"{e["kun"]}",'
        f'meaning:"{e["meaning"]}",'
        f'meaning_jp:"{e["meaning_jp"]}",'
        f'level:"{e["level"]}",'
        f'words:{words_js},'
        f'stroke:{e["stroke"]},'
        f'freq_rank:{e["freq_rank"]},'
        f'grade:{e["grade"]},'
        f'radical:"",'
        f'parts:{parts_js}}}'
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Fetching kanjidic2...")
    url = 'https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json'
    with urllib.request.urlopen(url, timeout=15) as r:
        kanjidic = json.loads(r.read())

    # Load existing KOERU kanji
    koeru_kanji = {}  # kanji → level
    for lv in ['n5','n4','n3','n2','n1']:
        content = open(JS_DIR / f'kanji-data-{lv}.js', encoding='utf-8').read()
        for m in re.finditer(r'kanji\s*:\s*"(.)"', content):
            koeru_kanji[m.group(1)] = lv.upper()

    print(f"KOERU hiện có: {len(koeru_kanji)} kanji")

    # ── 1. Tìm kanji hoàn toàn thiếu cho N4 và N3 ────────────────────────────
    missing = {'N4': [], 'N3': []}
    for kanji, data in kanjidic.items():
        lv = data.get('jlpt_new') or data.get('jlpt_old')
        if lv in (3, 4):
            target = f'N{lv}'
            if kanji not in koeru_kanji:
                missing[target].append(kanji)

    print(f"\nThiếu hoàn toàn: N4={len(missing['N4'])}, N3={len(missing['N3'])}")

    # ── 2. Thêm kanji thiếu vào file tương ứng ───────────────────────────────
    for level, kanji_list in missing.items():
        if not kanji_list:
            continue
        fpath = JS_DIR / f'kanji-data-{level.lower()}.js'
        content = fpath.read_text(encoding='utf-8')

        new_entries = []
        for k in sorted(kanji_list, key=lambda x: kanjidic.get(x, {}).get('freq', 9999)):
            entry = generate_entry(k, kanjidic.get(k, {}), level)
            new_entries.append(entry_to_js(entry))
            print(f"  + {level} {k} ({entry['hanviet']}) — {entry['meaning']}")

        # Insert before closing ];
        insert_block = ',\n' + ',\n'.join(new_entries)
        new_content = content.rstrip()
        if new_content.endswith('];'):
            new_content = new_content[:-2] + insert_block + '\n];'
        elif new_content.endswith(']'):
            new_content = new_content[:-1] + insert_block + '\n]'
        fpath.write_text(new_content + '\n', encoding='utf-8')
        print(f"  → Đã thêm {len(new_entries)} kanji vào {fpath.name}")

    # ── 3. Reclassify N3 kanji bị để nhầm ở N2 ───────────────────────────────
    print("\nReclassifying N3 kanji currently in N2...")
    n2_path = JS_DIR / 'kanji-data-n2.js'
    n3_path = JS_DIR / 'kanji-data-n3.js'
    n2_content = n2_path.read_text(encoding='utf-8')
    n3_content = n3_path.read_text(encoding='utf-8')

    # Find N3 kanji in kanjidic that are currently in KOERU N2
    to_move = []
    for kanji, data in kanjidic.items():
        lv = data.get('jlpt_new') or data.get('jlpt_old')
        if lv == 3 and koeru_kanji.get(kanji) == 'N2':
            to_move.append(kanji)

    print(f"  Cần chuyển {len(to_move)} kanji N2 → N3")

    # For each kanji to move: update level:"N2" → level:"N3" in n2 file
    # and move the entire entry to n3 file
    moved_entries = []
    remaining_n2 = n2_content

    for k in to_move:
        # Find and extract the entry from n2
        # Match the full object for this kanji
        pattern = r'\{kanji:"' + re.escape(k) + r'"[^}]*(?:\{[^}]*\}[^}]*)?\}'
        m = re.search(pattern, remaining_n2)
        if m:
            entry_str = m.group(0)
            # Update level
            entry_str = re.sub(r'level\s*:\s*"N2"', 'level:"N3"', entry_str)
            moved_entries.append(entry_str)

    if moved_entries:
        # Remove moved entries from N2 (update level field only — easier to just relabel)
        # Strategy: change level:"N2" → level:"N3" only for these specific kanji in n2_content
        updated_n2 = n2_content
        for k in to_move:
            # Find the block for this kanji and change its level
            def replace_level(match):
                return match.group(0).replace('level:"N2"', 'level:"N3"', 1)
            # Find block containing this kanji
            block_pat = r'(\{kanji:"' + re.escape(k) + r'"[^{]*(?:\{[^}]*\}[^{]*)*?\})'
            updated_n2 = re.sub(block_pat, replace_level, updated_n2)

        # Actually, it's simpler to:
        # 1. Keep entries in n2 file but change level to N3
        # 2. Remove them from n2 file
        # 3. Add them to n3 file
        # But the regex for multi-line JS objects is fragile.
        # Better approach: just update the 'level' field for these kanji in the n2 file
        # This means they'll show up in N3 study pages but still be in kanji-data-n2.js

        # For now, just update level field in n2 file
        n2_path.write_text(updated_n2, encoding='utf-8')

        # Add entries to n3 file (append)
        insert_block = ',\n' + ',\n'.join(moved_entries)
        nc = n3_content.rstrip()
        if nc.endswith('];'):
            nc = nc[:-2] + insert_block + '\n];'
        elif nc.endswith(']'):
            nc = nc[:-1] + insert_block + '\n]'
        n3_path.write_text(nc + '\n', encoding='utf-8')
        print(f"  → Đã cập nhật level cho {len(moved_entries)} kanji trong N2→N3")

    # ── 4. Rebuild kanji-data.js tổng hợp ────────────────────────────────────
    print("\nRebuilding kanji-data.js...")
    all_entries = []
    for lv in ['n5','n4','n3','n2','n1']:
        content = (JS_DIR / f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        # Extract array content
        m = re.search(r'window\.KANJI_N\d\s*=\s*(\[[\s\S]*\]);?', content)
        if m:
            arr_str = m.group(1)
            # Remove outer brackets, trim
            inner = arr_str.strip()[1:-1].strip()
            if inner:
                all_entries.append(inner)

    combined = 'window.KANJI_DATA = [\n' + ',\n'.join(all_entries) + '\n];\n'
    (JS_DIR / 'kanji-data.js').write_text(combined, encoding='utf-8')
    print("  → kanji-data.js đã rebuild")

    # Final count
    print("\n=== KẾT QUẢ ===")
    for lv in ['n5','n4','n3','n2','n1']:
        content = (JS_DIR / f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        count = len(re.findall(r'kanji\s*:\s*"."', content))
        std = {'n5':80,'n4':167,'n3':367,'n2':373,'n1':1244}
        lv_std = std.get(lv, '?')
        print(f"  N{lv[1]}: {count} kanji (chuẩn JLPT: ~{lv_std})")


if __name__ == '__main__':
    main()
