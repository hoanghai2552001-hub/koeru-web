import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Correct w/r/m for each kanji (keyed by kanji character)
# Format: kanji -> (word, reading, meaning)
corrections = {
    # N5 corrections
    '安': ('安心する', 'あんしんする', 'an tâm'),
    '飲': ('飲み物', 'のみもの', 'đồ uống'),
    '立': ('役に立つ', 'やくにたつ', 'có ích'),
    '来': ('来週', 'らいしゅう', 'tuần tới'),
    '友': ('親友', 'しんゆう', 'bạn thân'),
    '名': ('有名な', 'ゆうめいな', 'nổi tiếng'),
    '毎': ('毎日', 'まいにち', 'mỗi ngày'),
    '北': ('南北', 'なんぼく', 'nam bắc'),
    '母': ('お母さん', 'おかあさん', 'mẹ (kính ngữ)'),
    '聞': ('聞く', 'きく', 'nghe'),
    '分': ('一分', 'いっぷん', '1 phút'),
    '父': ('お父さん', 'おとうさん', 'bố (kính ngữ)'),
    '百': ('百人', 'ひゃくにん', '100 người'),
    '半': ('半分', 'はんぶん', 'một nửa'),
    '白': ('白紙', 'はくし', 'trang trắng'),
    '買': ('買い物', 'かいもの', 'mua sắm'),
    '年': ('一年', 'いちねん', '1 năm'),
    '入': ('入学する', 'にゅうがくする', 'nhập học'),
    '日': ('先日', 'せんじつ', 'hôm trước'),
    '南': ('南北', 'なんぼく', 'nam bắc'),
    '読': ('読書', 'どくしょ', 'đọc sách'),
    '道': ('書道', 'しょどう', 'thư đạo'),
    '東': ('東京', 'とうきょう', 'Tokyo'),
    '土': ('土地', 'とち', 'đất đai'),
    '電': ('電車', 'でんしゃ', 'tàu điện'),
    '店': ('店員', 'てんいん', 'nhân viên cửa hàng'),
    '天': ('天気', 'てんき', 'thời tiết'),
    '長': ('社長', 'しゃちょう', 'giám đốc'),
    '中': ('中国', 'ちゅうごく', 'Trung Quốc'),
    '男': ('長男', 'ちょうなん', 'con trai cả'),
    '大': ('大学', 'だいがく', 'trường đại học'),
    '多': ('多い', 'おおい', 'nhiều'),
    '足': ('足音', 'あしおと', 'tiếng chân'),
    '先': ('先月', 'せんげつ', 'tháng trước'),
    '西': ('西口', 'にしぐち', 'cổng phía Tây'),
    '生': ('先生', 'せんせい', 'thầy/cô giáo'),
    '水': ('水曜日', 'すいようび', 'thứ Tư'),
    '人': ('四人', 'よにん', '4 người'),
    '新': ('新聞', 'しんぶん', 'báo'),
    '食': ('食堂', 'しょくどう', 'căng tin, nhà ăn'),
    '上': ('屋上', 'おくじょう', 'sân thượng'),
    '少': ('少し', 'すこし', 'một chút'),
    '小': ('小学校', 'しょうがっこう', 'trường tiểu học'),
    '女': ('長女', 'ちょうじょ', 'con gái cả'),
    '書': ('読書', 'どくしょ', 'đọc sách'),
    '出': ('出かける', 'でかける', 'ra ngoài'),
    '週': ('今週', 'こんしゅう', 'tuần này'),
    '社': ('会社', 'かいしゃ', 'công ty'),
    '車': ('自動車', 'じどうしゃ', 'ô tô'),
    '七': ('七人', 'しちにん', '7 người'),
    '時': ('一時', 'いちじ', '1 giờ'),
    '子': ('女の子', 'おんなのこ', 'bé gái'),
    '四': ('四月', 'しがつ', 'tháng 4'),
    '山': ('富士山', 'ふじさん', 'núi Phú Sĩ'),
    '今': ('今週', 'こんしゅう', 'tuần này'),
    '国': ('外国', 'がいこく', 'nước ngoài'),
    '高': ('高校', 'こうこう', 'trường cấp 3'),
    '行': ('銀行', 'ぎんこう', 'ngân hàng'),
    '校': ('学校', 'がっこう', 'trường học'),
    '語': ('日本語', 'にほんご', 'tiếng Nhật'),
    '午': ('午後', 'ごご', 'buổi chiều'),
    '古': ('古い', 'ふるい', 'cũ'),
    '言': ('言葉', 'ことば', 'từ ngữ, ngôn ngữ'),
    '見': ('意見', 'いけん', 'ý kiến'),
    '月': ('九月', 'くがつ', 'tháng 9'),
    '空': ('空気', 'くうき', 'không khí'),
    '金': ('金曜日', 'きんようび', 'thứ Sáu'),
    '魚': ('人魚', 'にんぎょ', 'nàng tiên cá'),
    '気': ('空気', 'くうき', 'không khí'),
    '間': ('時間', 'じかん', 'thời gian'),
    '学': ('大学', 'だいがく', 'đại học'),
    '外': ('外国', 'がいこく', 'nước ngoài'),
    '話': ('電話', 'でんわ', 'điện thoại'),
}

ok = miss = 0
for kanji, (new_w, new_r, new_m) in corrections.items():
    # Find the entry for this kanji and replace its words array
    pattern = re.compile(
        r'(\{kanji:"' + re.escape(kanji) + r'"[^}]+words:\[)\{"w": "[^"]*", "r": "[^"]*", "m": "[^"]*"\}(\])'
    )
    new_word_entry = f'{{"w": "{new_w}", "r": "{new_r}", "m": "{new_m}"}}'
    new_content, n = pattern.subn(r'\g<1>' + new_word_entry + r'\g<2>', content)
    if n:
        content = new_content
        ok += 1
    else:
        print(f'NOT MATCHED: {kanji}')
        miss += 1

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Fixed {ok} | ❌ Not found: {miss}')
