"""
fill_vocab_missing.py
Điền từ vựng mẫu cho 100 kanji mới thêm (44 N4 + 56 N3) còn words:[]
Nguồn: JMdict qua jisho.org unofficial API / hardcoded từ tra tay
"""
import re
from pathlib import Path

JS_DIR = Path(__file__).parent.parent / "js"

# ── Từ vựng mẫu cho 44 N4 kanji thiếu ────────────────────────────────────────
# Format: kanji → list of {w, r, m}
# w = từ, r = cách đọc hiragana, m = nghĩa tiếng Việt
VOCAB_N4 = {
    "業": [{"w":"業務","r":"ぎょうむ","m":"công vụ; nghiệp vụ"},{"w":"工業","r":"こうぎょう","m":"công nghiệp"}],
    "場": [{"w":"場所","r":"ばしょ","m":"địa điểm; nơi chốn"},{"w":"工場","r":"こうじょう","m":"nhà máy; xưởng"}],
    "題": [{"w":"問題","r":"もんだい","m":"vấn đề; câu hỏi"},{"w":"題名","r":"だいめい","m":"tiêu đề; tên bài"}],
    "意": [{"w":"意味","r":"いみ","m":"ý nghĩa"},{"w":"意見","r":"いけん","m":"ý kiến"}],
    "持": [{"w":"持つ","r":"もつ","m":"cầm; giữ; có"},{"w":"気持ち","r":"きもち","m":"cảm giác; tâm trạng"}],
    "以": [{"w":"以上","r":"いじょう","m":"trên; hơn; ít nhất"},{"w":"以下","r":"いか","m":"dưới; ít hơn"}],
    "院": [{"w":"病院","r":"びょういん","m":"bệnh viện"},{"w":"学院","r":"がくいん","m":"học viện"}],
    "品": [{"w":"品物","r":"しなもの","m":"hàng hóa; đồ vật"},{"w":"食品","r":"しょくひん","m":"thực phẩm"}],
    "町": [{"w":"町","r":"まち","m":"thị trấn; khu phố"},{"w":"下町","r":"したまち","m":"phố cũ; khu thương mại"}],
    "転": [{"w":"転ぶ","r":"ころぶ","m":"ngã; vấp ngã"},{"w":"転職","r":"てんしょく","m":"chuyển việc"}],
    "験": [{"w":"経験","r":"けいけん","m":"kinh nghiệm"},{"w":"試験","r":"しけん","m":"kỳ thi; kiểm tra"}],
    "写": [{"w":"写真","r":"しゃしん","m":"ảnh; hình chụp"},{"w":"写す","r":"うつす","m":"sao chép; chụp"}],
    "悪": [{"w":"悪い","r":"わるい","m":"xấu; tồi; tệ"},{"w":"最悪","r":"さいあく","m":"tệ nhất; tồi tệ nhất"}],
    "室": [{"w":"教室","r":"きょうしつ","m":"phòng học; lớp học"},{"w":"室内","r":"しつない","m":"trong phòng; trong nhà"}],
    "風": [{"w":"風","r":"かぜ","m":"gió"},{"w":"台風","r":"たいふう","m":"bão; typhoon"}],
    "曜": [{"w":"日曜日","r":"にちようび","m":"Chủ Nhật"},{"w":"月曜日","r":"げつようび","m":"Thứ Hai"}],
    "貸": [{"w":"貸す","r":"かす","m":"cho mượn; cho thuê"},{"w":"貸し出し","r":"かしだし","m":"cho thuê; mượn"}],
    "堂": [{"w":"食堂","r":"しょくどう","m":"nhà ăn; căn tin"},{"w":"講堂","r":"こうどう","m":"hội trường; giảng đường"}],
    "勉": [{"w":"勉強","r":"べんきょう","m":"học tập; học bài"},{"w":"勉強する","r":"べんきょうする","m":"học; ôn bài"}],
    # Các kanji từ N5 vốn có nhưng bị lọc duplicate (夕台写町...)
    "夕": [{"w":"夕方","r":"ゆうがた","m":"buổi chiều tối"},{"w":"夕食","r":"ゆうしょく","m":"bữa tối"}],
    "台": [{"w":"台所","r":"だいどころ","m":"nhà bếp"},{"w":"台風","r":"たいふう","m":"bão nhiệt đới"}],
    "自": [{"w":"自分","r":"じぶん","m":"bản thân; tự mình"},{"w":"自動車","r":"じどうしゃ","m":"ô tô; xe hơi"}],
    "死": [{"w":"死ぬ","r":"しぬ","m":"chết"},{"w":"死亡","r":"しぼう","m":"tử vong; qua đời"}],
    "京": [{"w":"東京","r":"とうきょう","m":"Tokyo"},{"w":"京都","r":"きょうと","m":"Kyoto"}],
    "画": [{"w":"映画","r":"えいが","m":"phim; điện ảnh"},{"w":"画家","r":"がか","m":"họa sĩ"}],
    "住": [{"w":"住む","r":"すむ","m":"sống; cư trú"},{"w":"住所","r":"じゅうしょ","m":"địa chỉ"}],
    "究": [{"w":"研究","r":"けんきゅう","m":"nghiên cứu"},{"w":"研究者","r":"けんきゅうしゃ","m":"nhà nghiên cứu"}],
    "朝": [{"w":"朝","r":"あさ","m":"buổi sáng"},{"w":"今朝","r":"けさ","m":"sáng nay"}],
    "屋": [{"w":"部屋","r":"へや","m":"phòng"},{"w":"屋根","r":"やね","m":"mái nhà"}],
    "度": [{"w":"今度","r":"こんど","m":"lần này; lần tới"},{"w":"温度","r":"おんど","m":"nhiệt độ"}],
    "界": [{"w":"世界","r":"せかい","m":"thế giới"},{"w":"業界","r":"ぎょうかい","m":"ngành nghề; lĩnh vực"}],
    "発": [{"w":"出発","r":"しゅっぱつ","m":"khởi hành; xuất phát"},{"w":"発表","r":"はっぴょう","m":"công bố; phát biểu"}],
    "員": [{"w":"社員","r":"しゃいん","m":"nhân viên công ty"},{"w":"会員","r":"かいいん","m":"hội viên; thành viên"}],
    "問": [{"w":"質問","r":"しつもん","m":"câu hỏi"},{"w":"問題","r":"もんだい","m":"vấn đề; câu hỏi"}],
    "野": [{"w":"野球","r":"やきゅう","m":"bóng chày"},{"w":"分野","r":"ぶんや","m":"lĩnh vực; phạm vi"}],
    "集": [{"w":"集める","r":"あつめる","m":"thu thập; tập hợp"},{"w":"集合","r":"しゅうごう","m":"tập hợp; điểm hẹn"}],
    "真": [{"w":"真剣","r":"しんけん","m":"nghiêm túc; chân thành"},{"w":"写真","r":"しゃしん","m":"ảnh; hình chụp"}],
    "料": [{"w":"料理","r":"りょうり","m":"nấu ăn; món ăn"},{"w":"材料","r":"ざいりょう","m":"nguyên liệu; vật liệu"}],
    "質": [{"w":"品質","r":"ひんしつ","m":"chất lượng"},{"w":"質問","r":"しつもん","m":"câu hỏi"}],
    "族": [{"w":"家族","r":"かぞく","m":"gia đình"},{"w":"民族","r":"みんぞく","m":"dân tộc"}],
    "英": [{"w":"英語","r":"えいご","m":"tiếng Anh"},{"w":"英雄","r":"えいゆう","m":"anh hùng"}],
    "風": [{"w":"風景","r":"ふうけい","m":"phong cảnh; cảnh quan"},{"w":"風俗","r":"ふうぞく","m":"phong tục; tập quán"}],
    "洋": [{"w":"洋服","r":"ようふく","m":"quần áo Tây; trang phục"},{"w":"西洋","r":"せいよう","m":"phương Tây"}],
    "借": [{"w":"借りる","r":"かりる","m":"mượn; vay"},{"w":"借金","r":"しゃっきん","m":"nợ; tiền vay"}],
}

# ── Từ vựng mẫu cho 56 N3 kanji thiếu ────────────────────────────────────────
VOCAB_N3 = {
    "議": [{"w":"会議","r":"かいぎ","m":"cuộc họp; hội nghị"},{"w":"議論","r":"ぎろん","m":"tranh luận; thảo luận"}],
    "民": [{"w":"国民","r":"こくみん","m":"quốc dân; công dân"},{"w":"民主","r":"みんしゅ","m":"dân chủ"}],
    "部": [{"w":"部長","r":"ぶちょう","m":"trưởng phòng; trưởng bộ phận"},{"w":"全部","r":"ぜんぶ","m":"tất cả; toàn bộ"}],
    "回": [{"w":"今回","r":"こんかい","m":"lần này"},{"w":"回答","r":"かいとう","m":"trả lời; câu trả lời"}],
    "実": [{"w":"実は","r":"じつは","m":"thực ra; thật ra"},{"w":"実際","r":"じっさい","m":"thực tế; thực sự"}],
    "関": [{"w":"関係","r":"かんけい","m":"quan hệ; liên quan"},{"w":"関心","r":"かんしん","m":"quan tâm; chú ý"}],
    "最": [{"w":"最近","r":"さいきん","m":"gần đây; dạo này"},{"w":"最初","r":"さいしょ","m":"đầu tiên; ban đầu"}],
    "首": [{"w":"首相","r":"しゅしょう","m":"thủ tướng"},{"w":"首都","r":"しゅと","m":"thủ đô"}],
    "期": [{"w":"期間","r":"きかん","m":"khoảng thời gian; thời hạn"},{"w":"時期","r":"じき","m":"thời kỳ; thời điểm"}],
    "都": [{"w":"都市","r":"とし","m":"thành phố; đô thị"},{"w":"東京都","r":"とうきょうと","m":"Tokyo (đô)"}],
    "進": [{"w":"進む","r":"すすむ","m":"tiến lên; tiến bộ"},{"w":"前進","r":"ぜんしん","m":"tiến lên phía trước"}],
    "数": [{"w":"数学","r":"すうがく","m":"toán học"},{"w":"数字","r":"すうじ","m":"con số; chữ số"}],
    "記": [{"w":"記念","r":"きねん","m":"kỷ niệm"},{"w":"記事","r":"きじ","m":"bài báo; tin tức"}],
    "産": [{"w":"産業","r":"さんぎょう","m":"công nghiệp; ngành sản xuất"},{"w":"生産","r":"せいさん","m":"sản xuất"}],
    "求": [{"w":"要求","r":"ようきゅう","m":"yêu cầu; đòi hỏi"},{"w":"求める","r":"もとめる","m":"tìm kiếm; yêu cầu"}],
    "所": [{"w":"場所","r":"ばしょ","m":"địa điểm; nơi chốn"},{"w":"事務所","r":"じむしょ","m":"văn phòng"}],
    "官": [{"w":"官庁","r":"かんちょう","m":"cơ quan nhà nước"},{"w":"警官","r":"けいかん","m":"cảnh sát"}],
    "直": [{"w":"直接","r":"ちょくせつ","m":"trực tiếp"},{"w":"正直","r":"しょうじき","m":"thành thật; trung thực"}],
    "式": [{"w":"方式","r":"ほうしき","m":"phương thức; cách thức"},{"w":"式場","r":"しきじょう","m":"hội trường; lễ đường"}],
    "確": [{"w":"確認","r":"かくにん","m":"xác nhận"},{"w":"確かめる","r":"たしかめる","m":"kiểm tra; xác nhận"}],
    "位": [{"w":"位置","r":"いち","m":"vị trí"},{"w":"一位","r":"いちい","m":"hạng nhất; vị trí số một"}],
    "格": [{"w":"価格","r":"かかく","m":"giá cả; giá"},{"w":"合格","r":"ごうかく","m":"đậu; vượt qua (kỳ thi)"}],
    "疑": [{"w":"疑問","r":"ぎもん","m":"thắc mắc; điều nghi ngờ"},{"w":"疑う","r":"うたがう","m":"nghi ngờ; hoài nghi"}],
    "球": [{"w":"野球","r":"やきゅう","m":"bóng chày"},{"w":"地球","r":"ちきゅう","m":"trái đất"}],
    "割": [{"w":"割引","r":"わりびき","m":"giảm giá; chiết khấu"},{"w":"割る","r":"わる","m":"chia; vỡ; bẻ"}],
    "消": [{"w":"消える","r":"きえる","m":"biến mất; tắt"},{"w":"消費","r":"しょうひ","m":"tiêu thụ; chi tiêu"}],
    "規": [{"w":"規則","r":"きそく","m":"quy tắc; nội quy"},{"w":"規模","r":"きぼ","m":"quy mô"}],
    "害": [{"w":"被害","r":"ひがい","m":"thiệt hại; tổn thất"},{"w":"害虫","r":"がいちゅう","m":"côn trùng có hại"}],
    "声": [{"w":"声","r":"こえ","m":"giọng nói; tiếng"},{"w":"大声","r":"おおごえ","m":"tiếng to; ồn ào"}],
    "葉": [{"w":"言葉","r":"ことば","m":"ngôn ngữ; từ ngữ"},{"w":"葉っぱ","r":"はっぱ","m":"chiếc lá"}],
    "働": [{"w":"働く","r":"はたらく","m":"làm việc"},{"w":"労働","r":"ろうどう","m":"lao động"}],
    "非": [{"w":"非常に","r":"ひじょうに","m":"rất; vô cùng"},{"w":"非常口","r":"ひじょうぐち","m":"lối thoát khẩn cấp"}],
    "観": [{"w":"観光","r":"かんこう","m":"du lịch; tham quan"},{"w":"観察","r":"かんさつ","m":"quan sát"}],
    "科": [{"w":"科学","r":"かがく","m":"khoa học"},{"w":"科目","r":"かもく","m":"môn học"}],
    "太": [{"w":"太陽","r":"たいよう","m":"mặt trời"},{"w":"太い","r":"ふとい","m":"to; dày; béo"}],
    "客": [{"w":"客","r":"きゃく","m":"khách"},{"w":"観客","r":"かんきゃく","m":"khán giả"}],
    "号": [{"w":"番号","r":"ばんごう","m":"số; mã số"},{"w":"号室","r":"ごうしつ","m":"số phòng"}],
    "座": [{"w":"座る","r":"すわる","m":"ngồi"},{"w":"座席","r":"ざせき","m":"chỗ ngồi; ghế"}],
    "給": [{"w":"給料","r":"きゅうりょう","m":"tiền lương"},{"w":"支給","r":"しきゅう","m":"cấp phát; trả"}],
    "寄": [{"w":"寄る","r":"よる","m":"ghé lại; đến gần"},{"w":"寄付","r":"きふ","m":"quyên góp; đóng góp"}],
    "込": [{"w":"込む","r":"こむ","m":"đông; đông đúc"},{"w":"申し込む","r":"もうしこむ","m":"đăng ký; nộp đơn"}],
    "覚": [{"w":"覚える","r":"おぼえる","m":"nhớ; học thuộc"},{"w":"目覚める","r":"めざめる","m":"thức dậy; tỉnh ngủ"}],
    "許": [{"w":"許可","r":"きょか","m":"cho phép; sự cho phép"},{"w":"許す","r":"ゆるす","m":"tha thứ; chấp thuận"}],
    "便": [{"w":"便利","r":"べんり","m":"tiện lợi; thuận tiện"},{"w":"不便","r":"ふべん","m":"bất tiện"}],
    "勤": [{"w":"勤める","r":"つとめる","m":"làm việc; phục vụ"},{"w":"勤務","r":"きんむ","m":"công vụ; làm việc"}],
    "居": [{"w":"居る","r":"いる","m":"ở; có mặt"},{"w":"居間","r":"いま","m":"phòng khách"}],
    "招": [{"w":"招待","r":"しょうたい","m":"mời; lời mời"},{"w":"招く","r":"まねく","m":"vẫy tay; mời"}],
    "願": [{"w":"お願い","r":"おねがい","m":"xin; nhờ"},{"w":"願望","r":"がんぼう","m":"nguyện vọng; ước muốn"}],
    "絵": [{"w":"絵","r":"え","m":"tranh; hình vẽ"},{"w":"絵本","r":"えほん","m":"sách tranh"}],
    "掛": [{"w":"掛ける","r":"かける","m":"treo; đặt; gọi điện"},{"w":"腰掛け","r":"こしかけ","m":"ghế tựa; ngồi tạm"}],
    "吸": [{"w":"吸う","r":"すう","m":"hút; hít"},{"w":"吸収","r":"きゅうしゅう","m":"hấp thụ; hút"}],
    "洗": [{"w":"洗う","r":"あらう","m":"rửa; giặt"},{"w":"洗濯","r":"せんたく","m":"giặt giũ"}],
    "慣": [{"w":"習慣","r":"しゅうかん","m":"thói quen; phong tục"},{"w":"慣れる","r":"なれる","m":"quen; quen thuộc"}],
    "皆": [{"w":"皆","r":"みんな","m":"tất cả mọi người"},{"w":"皆さん","r":"みなさん","m":"mọi người (kính ngữ)"}],
    "幾": [{"w":"幾つ","r":"いくつ","m":"bao nhiêu; mấy tuổi"},{"w":"幾ら","r":"いくら","m":"bao nhiêu tiền"}],
}


def js_word(w):
    return '{' + f'\"w\":\"{w["w"]}\",\"r\":\"{w["r"]}\",\"m\":\"{w["m"]}\"' + '}'


def patch_words(content, kanji, words):
    """Thay words:[] bằng words với dữ liệu thực"""
    words_js = '[' + ','.join(js_word(w) for w in words) + ']'
    # Match kanji entry có words:[]
    pattern = r'(kanji:"' + re.escape(kanji) + r'"(?:[^}]{0,200}?)words:\[\])'
    replacement = lambda m: m.group(0).replace('words:[]', f'words:{words_js}')
    new_content, count = re.subn(pattern, replacement, content, count=1)
    return new_content, count


def main():
    n4_path = JS_DIR / "kanji-data-n4.js"
    n3_path = JS_DIR / "kanji-data-n3.js"
    n2_path = JS_DIR / "kanji-data-n2.js"

    n4 = n4_path.read_text(encoding='utf-8')
    n3 = n3_path.read_text(encoding='utf-8')
    n2 = n2_path.read_text(encoding='utf-8')

    stats = {"n4": 0, "n3": 0, "n2": 0, "miss": []}

    for kanji, words in VOCAB_N4.items():
        patched = False
        for name, content in [("n4", n4), ("n3", n3), ("n2", n2)]:
            if f'kanji:"{kanji}"' in content:
                new_c, cnt = patch_words(content, kanji, words)
                if cnt:
                    if name == "n4": n4 = new_c
                    elif name == "n3": n3 = new_c
                    else: n2 = new_c
                    stats[name] += 1
                    patched = True
                    print(f"  ✓ {name.upper()} {kanji} → {words[0]['w']} ({words[0]['m']})")
                    break
        if not patched:
            stats["miss"].append(kanji)

    for kanji, words in VOCAB_N3.items():
        patched = False
        for name, content in [("n3", n3), ("n4", n4), ("n2", n2)]:
            if f'kanji:"{kanji}"' in content:
                new_c, cnt = patch_words(content, kanji, words)
                if cnt:
                    if name == "n4": n4 = new_c
                    elif name == "n3": n3 = new_c
                    else: n2 = new_c
                    stats[name] += 1
                    patched = True
                    print(f"  ✓ {name.upper()} {kanji} → {words[0]['w']} ({words[0]['m']})")
                    break
        if not patched:
            stats["miss"].append(kanji)

    # Write back
    n4_path.write_text(n4, encoding='utf-8')
    n3_path.write_text(n3, encoding='utf-8')
    n2_path.write_text(n2, encoding='utf-8')

    print(f"\nĐã điền từ vựng: N4={stats['n4']}, N3={stats['n3']}, N2={stats['n2']}")
    if stats["miss"]:
        print(f"Không tìm thấy trong file: {stats['miss']}")

    # Rebuild kanji-data.js
    print("Rebuilding kanji-data.js...")
    parts = []
    for lv in ['n5', 'n4', 'n3', 'n2', 'n1']:
        c = (JS_DIR / f"kanji-data-{lv}.js").read_text(encoding='utf-8')
        start = c.index('[')
        end = c.rindex(']') + 1
        inner = c[start+1:end-1].strip().rstrip(',')
        if inner:
            parts.append(inner)
    combined = 'window.KANJI_DATA = [\n' + ',\n'.join(parts) + '\n];\n'
    (JS_DIR / 'kanji-data.js').write_text(combined, encoding='utf-8')
    print("Done!")

    # Verify
    print("\nVerify sau khi điền:")
    for lv in ["n4", "n3"]:
        t = (JS_DIR / f"kanji-data-{lv}.js").read_text(encoding='utf-8')
        empty = len(re.findall(r'words:\[\]', t))
        total = len(re.findall(r'kanji:"', t))
        print(f"  {lv.upper()}: {total} kanji, {empty} còn trống words")


if __name__ == "__main__":
    main()
