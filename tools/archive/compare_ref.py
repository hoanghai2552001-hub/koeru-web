import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

ref = {
    '安': {'on':'アン', 'meaning':'rẻ, bình yên, an toàn'},
    '一': {'on':'イチ、イツ', 'meaning':'một'},
    '飲': {'on':'イン', 'meaning':'uống'},
    '右': {'on':'ウ、ユウ', 'meaning':'bên phải'},
    '雨': {'on':'ウ', 'meaning':'mưa'},
    '駅': {'on':'エキ', 'meaning':'nhà ga'},
    '円': {'on':'エン', 'meaning':'đồng yên, tròn'},
    '火': {'on':'カ', 'meaning':'lửa'},
    '花': {'on':'カ、ケ', 'meaning':'hoa'},
    '下': {'on':'カ、ゲ', 'meaning':'dưới, hạ xuống'},
    '何': {'on':'カ', 'meaning':'cái gì, bao nhiêu'},
    '会': {'on':'エ、カイ', 'meaning':'gặp gỡ, hội họp'},
    '話': {'on':'ワ', 'meaning':'nói chuyện'},
    '六': {'on':'ロク', 'meaning':'sáu'},
    '立': {'on':'リツ、リュウ', 'meaning':'đứng, thiết lập'},
    '来': {'on':'ライ', 'meaning':'đến, tới'},
    '友': {'on':'ユウ', 'meaning':'bạn'},
    '目': {'on':'ボク、モク', 'meaning':'mắt, con mắt'},
    '名': {'on':'メイ', 'meaning':'tên'},
    '万': {'on':'マン', 'meaning':'vạn (10.000)'},
    '毎': {'on':'マイ', 'meaning':'mỗi'},
    '本': {'on':'ホン', 'meaning':'sách, nguồn gốc'},
    '木': {'on':'ボク、モク', 'meaning':'cây, gỗ'},
    '北': {'on':'ホク', 'meaning':'phía bắc'},
    '母': {'on':'ボ', 'meaning':'mẹ'},
    '聞': {'on':'ブン', 'meaning':'nghe'},
    '分': {'on':'フン、ブン', 'meaning':'phút, chia, hiểu'},
    '父': {'on':'フ', 'meaning':'bố'},
    '百': {'on':'ヒャク', 'meaning':'trăm'},
    '半': {'on':'ハン', 'meaning':'nửa'},
    '八': {'on':'ハチ', 'meaning':'tám'},
    '白': {'on':'ハク', 'meaning':'trắng'},
    '買': {'on':'バイ', 'meaning':'mua'},
    '年': {'on':'ネン', 'meaning':'năm'},
    '入': {'on':'ニュウ', 'meaning':'vào, nhập'},
    '日': {'on':'ニチ、ジツ', 'meaning':'ngày, mặt trời'},
    '二': {'on':'ニ', 'meaning':'hai'},
    '南': {'on':'ナン', 'meaning':'phía nam'},
    '読': {'on':'ドク', 'meaning':'đọc'},
    '道': {'on':'ドウ', 'meaning':'đường, đạo'},
    '東': {'on':'トウ', 'meaning':'phía đông'},
    '土': {'on':'ド', 'meaning':'đất, thứ bảy'},
    '電': {'on':'デン', 'meaning':'điện'},
    '店': {'on':'テン', 'meaning':'cửa hàng'},
    '天': {'on':'テン', 'meaning':'trời, thiên'},
    '長': {'on':'チョウ', 'meaning':'dài, trưởng'},
    '中': {'on':'チュウ', 'meaning':'giữa, trong'},
    '男': {'on':'ダン、ナン', 'meaning':'nam, đàn ông'},
    '大': {'on':'ダイ', 'meaning':'to, lớn'},
    '多': {'on':'タ', 'meaning':'nhiều'},
    '足': {'on':'ソク', 'meaning':'chân, đủ'},
    '前': {'on':'ゼン', 'meaning':'trước'},
    '先': {'on':'セン', 'meaning':'trước, đầu tiên'},
    '千': {'on':'セン', 'meaning':'một nghìn'},
    '川': {'on':'セン', 'meaning':'sông'},
    '西': {'on':'セイ', 'meaning':'phía tây'},
    '生': {'on':'セイ', 'meaning':'sống, sinh ra'},
    '水': {'on':'スイ', 'meaning':'nước'},
    '人': {'on':'ジン、ニン', 'meaning':'người'},
    '新': {'on':'シン', 'meaning':'mới'},
    '食': {'on':'ショク', 'meaning':'ăn'},
    '上': {'on':'ジョウ', 'meaning':'trên, lên'},
    '少': {'on':'ショウ', 'meaning':'ít, một chút'},
    '小': {'on':'ショウ', 'meaning':'nhỏ'},
    '女': {'on':'ジョ', 'meaning':'phụ nữ, con gái'},
    '書': {'on':'ショ', 'meaning':'viết'},
    '出': {'on':'シュツ', 'meaning':'ra, xuất'},
    '十': {'on':'ジュウ', 'meaning':'mười'},
    '週': {'on':'シュウ', 'meaning':'tuần'},
    '手': {'on':'シュ', 'meaning':'tay'},
    '社': {'on':'シャ', 'meaning':'công ty, đền'},
    '車': {'on':'シャ', 'meaning':'xe'},
    '七': {'on':'シチ', 'meaning':'bảy'},
    '時': {'on':'ジ', 'meaning':'giờ, thời gian'},
    '耳': {'on':'ジ', 'meaning':'tai'},
    '子': {'on':'シ', 'meaning':'đứa trẻ, con'},
    '四': {'on':'シ', 'meaning':'bốn'},
    '山': {'on':'サン', 'meaning':'núi'},
    '三': {'on':'サン', 'meaning':'ba'},
    '左': {'on':'サ', 'meaning':'bên trái'},
    '今': {'on':'コン', 'meaning':'bây giờ'},
    '国': {'on':'コク', 'meaning':'đất nước'},
    '高': {'on':'コウ', 'meaning':'cao, đắt'},
    '行': {'on':'コウ、ギョウ', 'meaning':'đi, thực hiện'},
    '口': {'on':'コウ', 'meaning':'miệng'},
    '校': {'on':'コウ', 'meaning':'trường học'},
    '語': {'on':'ゴ', 'meaning':'ngôn ngữ'},
    '午': {'on':'ゴ', 'meaning':'trưa'},
    '後': {'on':'ゴ', 'meaning':'sau'},
    '五': {'on':'ゴ', 'meaning':'năm (số)'},
    '古': {'on':'コ', 'meaning':'cũ'},
    '言': {'on':'ゲン', 'meaning':'nói'},
    '見': {'on':'ケン', 'meaning':'nhìn, xem'},
    '月': {'on':'ゲツ', 'meaning':'tháng, mặt trăng'},
    '空': {'on':'クウ', 'meaning':'bầu trời, trống'},
    '金': {'on':'キン', 'meaning':'tiền, vàng'},
    '魚': {'on':'ギョ', 'meaning':'cá'},
    '休': {'on':'キュウ', 'meaning':'nghỉ'},
    '九': {'on':'キュウ', 'meaning':'chín'},
    '気': {'on':'キ', 'meaning':'tinh thần, khí'},
    '間': {'on':'カン', 'meaning':'giữa, khoảng'},
    '学': {'on':'ガク', 'meaning':'học, khoa học'},
    '外': {'on':'ガイ', 'meaning':'bên ngoài'},
}

diffs = []
for k, r in ref.items():
    m = re.search(r'\{kanji:"' + re.escape(k) + r'",hanviet:[^}]+\}', content)
    if not m:
        diffs.append({'k': k, 'issues': ['NOT FOUND']})
        continue
    entry = m.group(0)
    on_m = re.search(r'on:"([^"]+)"', entry)
    meaning_m = re.search(r',meaning:"([^"]+)"', entry)
    cur_on = on_m.group(1) if on_m else '?'
    cur_meaning = meaning_m.group(1) if meaning_m else '?'

    issues = []
    if r['on'] != cur_on:
        issues.append(f'on: "{cur_on}" → "{r["on"]}"')
    if r['meaning'] != cur_meaning:
        issues.append(f'meaning: "{cur_meaning}" → "{r["meaning"]}"')
    if issues:
        diffs.append({'k': k, 'issues': issues})

print(f'Cần sửa: {len(diffs)} kanji')
for d in diffs:
    print(f'  {d["k"]}: {" | ".join(d["issues"])}')
