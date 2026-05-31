"""
KOERU — Fill missing JLPT N3/N4 kanji (v2, fixed insertion)
"""
import re, json, urllib.request
from pathlib import Path

JS_DIR = Path(__file__).parent.parent / "js"

ON_TO_HV = {
    'ア':'A','アイ':'AI','アク':'ÁC','アン':'AN','イ':'Y','イチ':'NHẤT','イツ':'NHẤT',
    'イン':'ÂM','ウン':'VẬN','エイ':'ANH','エン':'VIÊN','オウ':'VƯƠNG','オク':'ỨC','オン':'ÂN',
    'カ':'HÁ','カイ':'GIỚI','カク':'CÁCH','カン':'CAN','ガイ':'NGOẠI','ガク':'NHẠC','ガン':'NHAM',
    'キ':'KỲ','キャク':'KHÁCH','キュウ':'CỨU','キョ':'CỰ','キョウ':'CỘNG','キン':'CẦN',
    'ギ':'NGHĨA','ギャク':'NGHỊCH','ギョ':'NGƯ','ギン':'NGÂN','ク':'CU','クウ':'KHÔNG',
    'グン':'QUÂN','ケイ':'KÍNH','ケツ':'QUYẾT','ケン':'KIÊN','ゲイ':'NGHỆ','ゲン':'NGUYÊN',
    'コ':'CỐ','コウ':'CÔNG','コク':'CỐC','コツ':'CỐT','コン':'CĂN','ゴウ':'HÀO','ゴク':'CỰC',
    'サ':'TẢ','サイ':'TẾ','サク':'SÁCH','サツ':'SÁT','サン':'TAM','ザイ':'TÀI','ザン':'TÀN',
    'シ':'CHỈ','シチ':'THẤT','シャ':'XÁ','シャク':'THÍCH','シュ':'THỦ','シュウ':'TẬP',
    'シュン':'XUÂN','ショ':'SƠ','ショウ':'TIỂU','ショク':'THỰC','シン':'TÂM',
    'ジ':'TỰ','ジツ':'THỰC','ジャク':'NHƯỢC','ジュ':'NHU','ジュウ':'THẬP','ジュン':'THUẦN',
    'ジョ':'TRỢ','ジョウ':'THƯỢNG','ジン':'NHÂN','ス':'TỐ','スイ':'THỦY','スウ':'SỐ','ズ':'ĐỒ',
    'セイ':'TINH','セキ':'TỊCH','セツ':'TIẾT','セン':'TIÊN','ゼイ':'THUẾ','ゼン':'THIỆN',
    'ソ':'TỔ','ソウ':'TỔNG','ソク':'TỨC','ゾウ':'TƯỢNG','ゾク':'TỘC',
    'タ':'ĐA','タイ':'ĐẠI','タク':'TRẠCH','タン':'ĐAN','ダイ':'ĐẠI','ダン':'ĐÀN',
    'チ':'TRI','チク':'TRÚC','チャ':'TRÀ','チュウ':'TRUNG','チョ':'TRỮ','チョウ':'ĐIỂU','チン':'TRÂN',
    'テイ':'ĐỀ','テキ':'ĐỊCH','テツ':'THIẾT','テン':'THIÊN','デン':'ĐIỀN',
    'ト':'ĐỒ','トウ':'ĐÁO','トク':'ĐỨC','ドウ':'ĐẠO','ドク':'ĐỘC','ド':'ĐỘ',
    'ナイ':'NỘI','ナン':'NAN','ニ':'NHỊ','ニク':'NHỤC','ニチ':'NHẬT','ニュウ':'NHẬP','ニン':'NHÂN',
    'ネン':'NIÊN','ノウ':'NĂNG',
    'ハ':'BÁT','ハイ':'BỐI','ハク':'BẠCH','ハツ':'PHÁT','ハン':'BÁN','バイ':'BỘI','バン':'VẠN',
    'ヒ':'PHI','ヒツ':'TẤT','ヒャク':'BÁCH','ヒョウ':'BÌNH','ヒン':'PHẨM','ビ':'MỸ','ビョウ':'BỆNH',
    'フ':'PHÚ','フウ':'PHONG','フク':'PHÚC','フン':'PHẦN','ブン':'VĂN',
    'ヘイ':'BÌNH','ヘン':'BIẾN','ボウ':'MẪU','ボク':'MỤC','ボン':'BỔN','ホ':'BỔ','ホウ':'PHƯƠNG','ホン':'BỔN',
    'マイ':'MUỘI','マン':'VẠN','ミ':'VỊ','ミン':'DÂN','ム':'VÔ','メイ':'MINH','モク':'MỘC','モン':'VĂN',
    'ヤ':'DÃ','ユウ':'HỮU','ヨ':'DƯ','ヨウ':'DƯƠNG','ヨク':'DỤC',
    'ライ':'LAI','ラク':'LẠC','ラン':'LAN','リ':'LÝ','リク':'LỤC','リツ':'LUẬT','リャク':'LƯỢC',
    'リュウ':'LƯU','リョウ':'LƯỢNG','リン':'LÂM','レイ':'LỄ','レキ':'LỊCH','レツ':'LIỆT','レン':'LIÊN',
    'ロウ':'LÃO','ロク':'LỤC','ロン':'LUẬN','ワ':'HÒA',
}

MEANING_VI = {
    'evening':'buổi tối','stand':'đứng','copy':'sao chép','town':'thị trấn',
    'self':'tự bản thân','oneself':'bản thân','death':'chết; tử','die':'chết',
    'capital':'thủ đô','picture':'hình; tranh','painting':'tranh vẽ',
    'room':'phòng','reason':'lý do','logic':'lý luận','by means of':'bằng cách',
    'house':'nhà','reside':'cư trú; ở','study':'nghiên cứu','place':'nơi; chỗ',
    'morning':'buổi sáng','shop':'cửa hàng','degree':'độ; mức','hold':'giữ; nắm',
    'world':'thế giới','departure':'xuất phát; khởi hành','fat':'béo; to',
    'number':'số','neck':'cổ','people':'nhân dân; dân','record':'ghi chép',
    'actual':'thực tế','section':'bộ phận; khoa','reality':'thực tế',
    'progress':'tiến bộ','word':'từ; lời','highest':'cao nhất; tối',
    'position':'vị trí; hạng','letter':'thư; chữ','circle':'vòng tròn',
    'return':'trở về','direct':'thẳng; trực tiếp','nature':'thiên nhiên',
    'origin':'gốc nguồn','country':'quốc gia','district':'khu vực','area':'vùng',
    'time':'thời gian','period':'giai đoạn','age':'tuổi; thời đại',
    'begin':'bắt đầu','start':'khởi đầu','finish':'hoàn thành','complete':'hoàn chỉnh',
    'thing':'vật; thứ','matter':'vấn đề','big':'lớn; to lớn','large':'to lớn',
    'great':'vĩ đại','small':'nhỏ','old':'cũ; già','new':'mới','high':'cao',
    'expensive':'đắt','low':'thấp','cheap':'rẻ','long':'dài','short':'ngắn',
    'strong':'mạnh','weak':'yếu','good':'tốt; hay','bad':'xấu; tồi',
    'beautiful':'đẹp','fast':'nhanh','slow':'chậm','hot':'nóng','warm':'ấm',
    'cold':'lạnh','many':'nhiều','few':'ít','all':'tất cả','half':'một nửa',
    'middle':'giữa','heaven':'trời','sky':'bầu trời','earth':'đất','water':'nước',
    'fire':'lửa','tree':'cây','wood':'gỗ','mountain':'núi','field':'cánh đồng',
    'flower':'hoa','grass':'cỏ','bird':'chim','fish':'cá','person':'người',
    'man':'đàn ông; nam','woman':'phụ nữ; nữ','child':'trẻ em; con',
    'father':'cha; bố','mother':'mẹ','friend':'bạn bè','teacher':'giáo viên',
    'student':'học sinh','king':'vua','language':'ngôn ngữ; tiếng',
    'read':'đọc','write':'viết','speak':'nói','listen':'nghe',
    'see':'nhìn; thấy','go':'đi','come':'đến','eat':'ăn','drink':'uống',
    'buy':'mua','sell':'bán','enter':'vào; nhập','exit':'ra; xuất',
    'up':'lên; trên','down':'xuống; dưới','left':'trái','right':'phải',
    'front':'trước','back':'sau','inside':'bên trong','outside':'bên ngoài',
    'year':'năm','month':'tháng','day':'ngày',
    'spring':'mùa xuân','summer':'mùa hè','autumn':'mùa thu','winter':'mùa đông',
    'road':'con đường','school':'trường học','money':'tiền','gold':'vàng',
    'work':'làm việc; công việc','company':'công ty','heart':'trái tim; tâm',
    'body':'cơ thể','life':'cuộc sống; sinh mệnh','love':'tình yêu; yêu',
    'happy':'hạnh phúc; vui','sad':'buồn','pain':'đau','think':'suy nghĩ',
    'know':'biết','learn':'học','teach':'dạy','use':'dùng; sử dụng',
    'make':'làm; tạo','build':'xây dựng','open':'mở','close':'đóng',
    'send':'gửi','receive':'nhận','give':'cho; tặng','take':'lấy; nhận',
    'wait':'chờ; đợi','meet':'gặp; gặp gỡ','join':'tham gia; nối',
    'cut':'cắt','run':'chạy','walk':'đi bộ','sit':'ngồi','sleep':'ngủ',
    'voice':'giọng; tiếng','straight':'thẳng; trực','science':'khoa học',
    'head':'đầu; thủ','citizen':'công dân; dân','advance':'tiến lên; tiến bộ',
    'leaf':'lá','convenience':'thuận tiện; tiện','deliberation':'bàn bạc; thảo luận',
    'fit':'phù hợp','suit':'phù hợp','extreme':'cực đoan; tối',
    'barrier':'rào cản; quan','gateway':'cổng vào','metropolis':'thủ đô',
    'products':'sản phẩm','substance':'chất; thực chất','quality':'chất lượng',
    'tribe':'bộ tộc; tộc','family':'gia đình','verification':'xác minh',
    'exertion':'nỗ lực; cố gắng','salary':'lương; thù lao',
    'diligence':'siêng năng; cần cù','petition':'nguyện vọng; đơn',
    'assurance':'đảm bảo; chắc chắn','status':'địa vị; tư cách',
    'doubt':'nghi ngờ','distrust':'không tin','sphere':'hình cầu; cầu',
    'proportion':'tỉ lệ; phần','extinguish':'tắt; dập tắt',
    'style':'phong cách; kiểu','ceremony':'nghi lễ; lễ',
    'harm':'hại; gây hại','injury':'thương tích','permit':'cho phép',
    'approve':'chấp thuận','beckon':'vẫy; mời','invite':'mời',
    'summon':'triệu tập','revolve':'xoay; quay','research':'nghiên cứu',
    'employee':'nhân viên','member':'thành viên','topic':'chủ đề; đề tài',
    'idea':'ý tưởng; ý kiến','occurrence':'lần xảy ra; lần',
    'plains':'đồng bằng','institution':'tổ chức; viện','temple':'chùa; viện',
    'boundary':'ranh giới; giới','congregate':'tụ tập','dignity':'phẩm giá',
    'pedestal':'bệ; đài','dynasty':'triều đại','regime':'chế độ',
    'dwell':'cư trú; ở','fee':'phí; lệ phí','materials':'nguyên liệu; vật liệu',
    'england':'Anh (quốc)','english':'tiếng Anh','hero':'anh hùng',
    'ocean':'đại dương; biển','roof':'mái nhà','plump':'mập; béo tròn',
    'borrow':'mượn; vay','rent':'thuê','scribe':'ghi chép; thư ký',
    'bureaucrat':'quan liêu; viên chức','request':'yêu cầu; cầu xin',
    'want':'muốn; mong','wish for':'mong muốn','wash':'rửa; giặt',
    'suck':'hút; mút','inhale':'hít vào','accustomed':'quen; thói quen',
    'hang':'treo','nickname':'biệt danh; hiệu','squat':'ngồi xổm',
    'crowded':'đông đúc','memorize':'ghi nhớ; thuộc','remember':'nhớ; ghi nhớ',
    'serve':'phục vụ; làm việc','exist':'tồn tại','item':'mục; vật phẩm',
    'negative':'phủ định; tiêu cực','appearance':'vẻ ngoài; hình dáng',
    'course':'môn học; khóa học','employee':'nhân viên; thành viên',
    'platform':'bục; nền tảng','drawing':'tranh; hình vẽ',
    'reason':'lý do; lý luận','plump':'béo; mập','fat':'béo; to',
}

def meanings_to_vi(meanings_en):
    results = []
    for m in meanings_en[:2]:
        ml = m.lower().strip()
        if ml in MEANING_VI:
            results.append(MEANING_VI[ml])
            continue
        found = False
        for k,v in MEANING_VI.items():
            if k == ml or (len(k) > 4 and k in ml):
                results.append(v)
                found = True
                break
        if not found:
            results.append(m)
    seen = []
    for r in results:
        if r not in seen:
            seen.append(r)
    return '; '.join(seen)

def on_to_hv(on_readings):
    if not on_readings: return ''
    on = on_readings[0].upper()
    for k,v in sorted(ON_TO_HV.items(), key=lambda x: -len(x[0])):
        if on.startswith(k): return v
    return on

def entry_to_js(k, kd, level):
    on  = '、'.join(kd.get('readings_on',[])[:3])
    kun = '、'.join(x.replace('-','').split('.')[0] for x in kd.get('readings_kun',[])[:3])
    meaning    = meanings_to_vi(kd.get('meanings',[])) or kd.get('meanings',[''])[0]
    meaning_jp = '、'.join(kd.get('meanings',[])[:2])
    hv = on_to_hv(kd.get('readings_on',[]))
    s = kd.get('strokes',0)
    f = kd.get('freq',9999)
    g = kd.get('grade',0)
    # Escape special chars in strings
    def esc(s): return s.replace('\\','\\\\').replace('"','\\"')
    return (f'{{kanji:"{esc(k)}",hanviet:"{esc(hv)}",on:"{esc(on)}",kun:"{esc(kun)}",'
            f'meaning:"{esc(meaning)}",meaning_jp:"{esc(meaning_jp)}",level:"{level}",'
            f'words:[],stroke:{s},freq_rank:{f},grade:{g},radical:"",parts:[]}}')

def insert_entries(filepath, new_entries_js, level_name):
    """Insert JS entries before the closing ]; of the array."""
    content = filepath.read_text(encoding='utf-8')
    # Find the closing ]; of the main array (last one before optional callback)
    # The pattern is: ...last_entry},\n];
    # We insert before ];
    idx = content.rfind('];')
    if idx == -1:
        print(f"ERROR: Cannot find ]; in {filepath}")
        return 0
    block = ',\n' + ',\n'.join(new_entries_js)
    new_content = content[:idx] + block + '\n' + content[idx:]
    filepath.write_text(new_content, encoding='utf-8')
    return len(new_entries_js)

def main():
    print("Fetching kanjidic2 standard list...")
    url = 'https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json'
    with urllib.request.urlopen(url, timeout=15) as r:
        kanjidic = json.loads(r.read())

    # Build existing kanji set with their KOERU level
    koeru = {}  # kanji → 'N2','N3', etc.
    for lv in ['n5','n4','n3','n2','n1']:
        c = (JS_DIR/f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        for m in re.finditer(r'kanji\s*:\s*"(.)"', c):
            koeru[m.group(1)] = lv.upper()

    print(f"KOERU current: {len(koeru)} unique kanji")

    # ── STEP 1: Add completely missing kanji to N4 and N3 ────────────────────
    for jlpt_lv, level_name in [(4,'N4'), (3,'N3')]:
        missing = [(k,d) for k,d in kanjidic.items()
                   if (d.get('jlpt_new') or d.get('jlpt_old')) == jlpt_lv
                   and k not in koeru]
        missing.sort(key=lambda x: x[1].get('freq', 9999))

        if not missing:
            print(f"{level_name}: nothing missing ✓")
            continue

        entries_js = [entry_to_js(k, d, level_name) for k,d in missing]
        fpath = JS_DIR / f'kanji-data-{level_name.lower()}.js'
        n = insert_entries(fpath, entries_js, level_name)
        for k,_ in missing:
            koeru[k] = level_name
        print(f"{level_name}: added {n} missing kanji")

    # ── STEP 2: Reclassify N3 kanji in N2 file ───────────────────────────────
    # These are kanji kanjidic marks as N3 but KOERU put in N2
    # Strategy: update level field in kanji-data-n2.js only
    n2_path = JS_DIR/'kanji-data-n2.js'
    n2_content = n2_path.read_text(encoding='utf-8')

    to_reclassify = [k for k,d in kanjidic.items()
                     if (d.get('jlpt_new') or d.get('jlpt_old')) == 3
                     and koeru.get(k) == 'N2']

    print(f"\nReclassifying {len(to_reclassify)} kanji: level N2→N3 in kanji-data-n2.js")

    # Update level field for each kanji in N2 file
    updated = n2_content
    changed = 0
    for k in to_reclassify:
        # Find this kanji's entry block and change its level field
        # Pattern: kanji:"X" followed by level:"N2" within 400 chars
        old = updated
        pat = r'(kanji:"' + re.escape(k) + r'"(?:[^{}]|\{[^}]*\}){0,300}?level:")N2(")'
        updated = re.sub(pat, r'\1N3\2', updated, count=1)
        if updated != old:
            changed += 1

    n2_path.write_text(updated, encoding='utf-8')
    print(f"  → Updated level field for {changed}/{len(to_reclassify)} kanji")

    # ── STEP 3: Rebuild kanji-data.js ────────────────────────────────────────
    print("\nRebuilding kanji-data.js (combined)...")
    all_inner = []
    for lv in ['n5','n4','n3','n2','n1']:
        c = (JS_DIR/f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        m = re.search(r'window\.KANJI_N\d\s*=\s*\[([\s\S]*?)\]\s*;', c)
        if m:
            inner = m.group(1).strip().rstrip(',')
            if inner:
                all_inner.append(inner)

    combined = 'window.KANJI_DATA = [\n' + ',\n'.join(all_inner) + '\n];\n'
    (JS_DIR/'kanji-data.js').write_text(combined, encoding='utf-8')

    # ── Final count ───────────────────────────────────────────────────────────
    print("\n=== KẾT QUẢ CUỐI ===")
    std = {'n5':80,'n4':167,'n3':367,'n2':373,'n1':1244}
    for lv in ['n5','n4','n3','n2','n1']:
        c = (JS_DIR/f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        total   = len(re.findall(r'kanji\s*:\s*"."', c))
        as_n3   = len(re.findall(r'level\s*:\s*"N3"', c))
        lv_std  = std.get(lv,'?')
        extra   = f" (incl. {as_n3} labeled N3)" if lv == 'n2' and as_n3 else ""
        status  = "✅" if total >= lv_std else "⚠️"
        print(f"  {status} {lv.upper()}: {total} kanji (JLPT std ~{lv_std}){extra}")

if __name__ == '__main__':
    main()
