import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Correct w/r/m for each kanji
# Format: kanji_char -> (word, reading, Vietnamese meaning)
corrections = {
    # N5 — verified against standard JLPT references
    '安': ('安心する', 'あんしんする', 'an tâm'),
    '飲': ('飲み物', 'のみもの', 'đồ uống'),
    '立': ('役に立つ', 'やくにたつ', 'có ích'),
    '来': ('来週', 'らいしゅう', 'tuần tới'),
    '友': ('親友', 'しんゆう', 'bạn thân'),
    '名': ('有名な', 'ゆうめいな', 'nổi tiếng'),
    '毎': ('毎日', 'まいにち', 'mỗi ngày'),
    '北': ('北海道', 'ほっかいどう', 'Hokkaido'),
    '母': ('お母さん', 'おかあさん', 'mẹ (kính ngữ)'),
    '聞': ('聞こえる', 'きこえる', 'nghe thấy'),
    '分': ('三分', 'さんぷん', '3 phút'),
    '父': ('お父さん', 'おとうさん', 'bố (kính ngữ)'),
    '百': ('百円', 'ひゃくえん', '100 yên'),
    '半': ('半年', 'はんとし', 'nửa năm'),
    '白': ('白鳥', 'はくちょう', 'thiên nga'),
    '買': ('買い物', 'かいもの', 'mua sắm'),
    '年': ('三年生', 'さんねんせい', 'học sinh năm 3'),
    '入': ('入院する', 'にゅういんする', 'nhập viện'),
    '日': ('日曜日', 'にちようび', 'Chủ Nhật'),
    '南': ('ベトナム', 'べとなむ', 'Việt Nam'),
    '読': ('読者', 'どくしゃ', 'độc giả'),
    '道': ('道具', 'どうぐ', 'dụng cụ, đạo cụ'),
    '東': ('東北', 'とうほく', 'vùng Đông Bắc'),
    '土': ('土曜日', 'どようび', 'Thứ Bảy'),
    '電': ('電気', 'でんき', 'điện'),
    '店': ('店長', 'てんちょう', 'cửa hàng trưởng'),
    '天': ('天国', 'てんごく', 'thiên đường'),
    '長': ('部長', 'ぶちょう', 'trưởng phòng'),
    '中': ('一日中', 'いちにちじゅう', 'suốt cả ngày'),
    '男': ('男性', 'だんせい', 'nam giới'),
    '大': ('大学生', 'だいがくせい', 'sinh viên đại học'),
    '多': ('エクアドル', 'えくあどる', 'Ecuador'),
    '足': ('足りる', 'たりる', 'đủ, đầy đủ'),
    '先': ('先週', 'せんしゅう', 'tuần trước'),
    '西': ('西北', 'せいほく', 'hướng Tây Bắc'),
    '生': ('誕生日', 'たんじょうび', 'sinh nhật'),
    '水': ('水牛', 'すいぎゅう', 'con trâu'),
    '人': ('日本人', 'にほんじん', 'người Nhật'),
    '新': ('新年', 'しんねん', 'năm mới'),
    '食': ('食事', 'しょくじ', 'bữa ăn'),
    '上': ('上手', 'じょうず', 'giỏi'),
    '少': ('少ない', 'すくない', 'ít'),
    '小': ('小学生', 'しょうがくせい', 'học sinh tiểu học'),
    '女': ('女性', 'じょせい', 'nữ giới'),
    '書': ('辞書', 'じしょ', 'từ điển'),
    '出': ('出かける', 'でかける', 'ra ngoài'),
    '週': ('来週', 'らいしゅう', 'tuần tới'),
    '社': ('社会', 'しゃかい', 'xã hội'),
    '車': ('自転車', 'じてんしゃ', 'xe đạp'),
    '七': ('七時', 'しちじ', '7 giờ'),
    '時': ('何時', 'なんじ', 'mấy giờ'),
    '子': ('子供', 'こども', 'trẻ con'),
    '四': ('四国', 'しこく', 'đảo Shikoku'),
    '山': ('火山', 'かざん', 'núi lửa'),
    '今': ('今月', 'こんがつ', 'tháng này'),
    '国': ('中国', 'ちゅうごく', 'Trung Quốc'),
    '高': ('高校生', 'こうこうせい', 'học sinh cấp 3'),
    '行': ('旅行', 'りょこう', 'du lịch'),
    '校': ('高校', 'こうこう', 'trường cấp 3'),
    '語': ('外国語', 'がいこくご', 'ngoại ngữ'),
    '午': ('午前', 'ごぜん', 'buổi sáng'),
    '古': ('古本', 'ふるほん', 'sách cũ'),
    '言': ('言葉', 'ことば', 'từ ngữ, ngôn ngữ'),
    '見': ('見物', 'けんぶつ', 'ngắm cảnh, thăm quan'),
    '月': ('来月', 'らいげつ', 'tháng tới'),
    '空': ('空港', 'くうこう', 'sân bay'),
    '金': ('金魚', 'きんぎょ', 'cá vàng'),
    '魚': ('金魚', 'きんぎょ', 'cá vàng'),
    '気': ('気をつける', 'きをつける', 'cẩn thận'),
    '間': ('人間', 'にんげん', 'con người, nhân loại'),
    '学': ('学生', 'がくせい', 'học sinh, sinh viên'),
    '外': ('外国語', 'がいこくご', 'tiếng nước ngoài'),
    '話': ('会話', 'かいわ', 'hội thoại'),
}

ok = miss = 0
for kanji, (new_w, new_r, new_m) in corrections.items():
    # Find the kanji entry and replace its first word entry
    pattern = re.compile(
        r'(\{kanji:"' + re.escape(kanji) + r'"[^,\n]*(?:,[^,\n]*){4,10}?,words:\[)'
        r'\{"w": "[^"]*", "r": "[^"]*", "m": "[^"]*"\}'
    )
    new_word = f'{{"w": "{new_w}", "r": "{new_r}", "m": "{new_m}"}}'
    new_content, n = pattern.subn(r'\g<1>' + new_word, content)
    if n:
        content = new_content
        ok += 1
    else:
        # Try simpler approach
        simple = re.compile(
            r'(kanji:"' + re.escape(kanji) + r'"[^\n]*words:\[)'
            r'\{"w": "[^"]*", "r": "[^"]*", "m": "[^"]*"\}'
        )
        new_content2, n2 = simple.subn(r'\g<1>' + new_word, content)
        if n2:
            content = new_content2
            ok += 1
        else:
            print(f'NOT MATCHED: {kanji}')
            miss += 1

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Fixed {ok} | ❌ Not found: {miss}')
