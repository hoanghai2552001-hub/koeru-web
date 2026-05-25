import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

ref = {
    '化': {'on':'カ、ケ', 'meaning':'hóa, biến đổi'},
    '内': {'on':'ナイ', 'meaning':'bên trong'},
    '反': {'on':'ハン', 'meaning':'phản đối, ngược lại'},
    '平': {'on':'ヘイ', 'meaning':'bằng phẳng, hòa bình'},
    '氷': {'on':'ヒョウ', 'meaning':'băng'},
    '石': {'on':'セキ', 'meaning':'đá'},
    '他': {'on':'タ', 'meaning':'khác, người khác'},
    '加': {'on':'カ', 'meaning':'thêm, gia tăng'},
    '失': {'on':'シツ', 'meaning':'mất, thất'},
    '血': {'on':'ケツ', 'meaning':'máu'},
    '共': {'on':'キョウ', 'meaning':'cùng nhau'},
    '曲': {'on':'キョク', 'meaning':'cong, khúc nhạc'},
    '竹': {'on':'チク', 'meaning':'tre, trúc'},
    '虫': {'on':'チュウ', 'meaning':'côn trùng'},
    '交': {'on':'コウ', 'meaning':'giao, trao đổi'},
    '成': {'on':'セイ', 'meaning':'thành, trở thành'},
    '全': {'on':'ゼン', 'meaning':'toàn bộ, toàn'},
    '争': {'on':'ソウ', 'meaning':'tranh giành, chiến'},
    '任': {'on':'ニン', 'meaning':'giao phó, trách nhiệm'},
    '利': {'on':'リ', 'meaning':'lợi ích, thuận tiện'},
    '防': {'on':'ボウ', 'meaning':'phòng, ngăn chặn'},
    '返': {'on':'ヘン', 'meaning':'trả lại, đáp'},
    '身': {'on':'シン', 'meaning':'thân thể, bản thân'},
    '努': {'on':'ド', 'meaning':'nỗ lực'},
    '谷': {'on':'コク', 'meaning':'thung lũng'},
    '完': {'on':'カン', 'meaning':'hoàn thành, hoàn hảo'},
    '角': {'on':'カク', 'meaning':'góc'},
    '形': {'on':'ケイ', 'meaning':'hình dạng, hình'},
    '決': {'on':'ケツ', 'meaning':'quyết định'},
    '希': {'on':'キ', 'meaning':'hy vọng, hiếm'},
    '幸': {'on':'コウ', 'meaning':'hạnh phúc, may mắn'},
    '季': {'on':'キ', 'meaning':'mùa'},
    '泣': {'on':'キュウ', 'meaning':'khóc'},
    '易': {'on':'イ、エキ', 'meaning':'dễ, trao đổi'},
    '育': {'on':'イク', 'meaning':'nuôi, giáo dục'},
    '泳': {'on':'エイ', 'meaning':'bơi'},
    '定': {'on':'テイ', 'meaning':'xác định, quyết định'},
    '底': {'on':'テイ', 'meaning':'đáy'},
    '命': {'on':'メイ', 'meaning':'sinh mệnh, mạng'},
    '法': {'on':'ホウ', 'meaning':'pháp luật, phương pháp'},
    '勇': {'on':'ユウ', 'meaning':'dũng cảm'},
    '変': {'on':'ヘン', 'meaning':'thay đổi, biến'},
    '飛': {'on':'ヒ', 'meaning':'bay'},
    '美': {'on':'ビ', 'meaning':'đẹp'},
    '独': {'on':'ドク', 'meaning':'một mình, độc'},
    '草': {'on':'ソウ', 'meaning':'cỏ'},
    '信': {'on':'シン', 'meaning':'tin, tin tưởng'},
    '星': {'on':'セイ', 'meaning':'ngôi sao'},
    '単': {'on':'タン', 'meaning':'đơn giản, đơn'},
    '炭': {'on':'タン', 'meaning':'than'},
    '活': {'on':'カツ', 'meaning':'sống, hoạt động'},
    '感': {'on':'カン', 'meaning':'cảm giác, cảm xúc'},
    '解': {'on':'カイ', 'meaning':'giải quyết, hiểu'},
    '愛': {'on':'アイ', 'meaning':'yêu thương'},
    '禁': {'on':'キン', 'meaning':'cấm'},
    '夢': {'on':'ム', 'meaning':'giấc mơ'},
    '続': {'on':'ゾク', 'meaning':'tiếp tục'},
    '選': {'on':'セン', 'meaning':'chọn'},
    '導': {'on':'ドウ', 'meaning':'dẫn dắt, hướng dẫn'},
    '熱': {'on':'ネツ', 'meaning':'nóng, nhiệt, đam mê'},
    '量': {'on':'リョウ', 'meaning':'lượng, số lượng'},
    '機': {'on':'キ', 'meaning':'máy móc, cơ hội'},
    '橋': {'on':'キョウ', 'meaning':'cầu'},
    '波': {'on':'ハ', 'meaning':'sóng'},
    '念': {'on':'ネン', 'meaning':'ý niệm, nghĩ'},
    '勝': {'on':'ショウ', 'meaning':'thắng, vượt'},
    '種': {'on':'シュ', 'meaning':'loại, giống'},
    '折': {'on':'セツ', 'meaning':'gập, gãy'},
    '雑': {'on':'ザツ', 'meaning':'tạp, hỗn hợp'},
    '察': {'on':'サツ', 'meaning':'quan sát, điều tra'},
    '際': {'on':'サイ', 'meaning':'dịp, khi'},
    '算': {'on':'サン', 'meaning':'tính toán'},
    '散': {'on':'サン', 'meaning':'phân tán, tan'},
    '残': {'on':'ザン', 'meaning':'còn lại'},
    '財': {'on':'ザイ', 'meaning':'tài sản'},
    '罪': {'on':'ザイ', 'meaning':'tội lỗi'},
    '在': {'on':'ザイ', 'meaning':'tồn tại, ở'},
    '再': {'on':'サイ', 'meaning':'lại, một lần nữa'},
    '刺': {'on':'シ', 'meaning':'đâm, thẻ'},
    '姿': {'on':'シ', 'meaning':'dáng vẻ, tư thế'},
    '冷': {'on':'レイ', 'meaning':'lạnh'},
    '例': {'on':'レイ', 'meaning':'ví dụ'},
    '礼': {'on':'レイ', 'meaning':'lễ phép, lễ nghi'},
    '令': {'on':'レイ', 'meaning':'lệnh, pháp lệnh'},
    '路': {'on':'ロ', 'meaning':'đường, lộ'},
    '労': {'on':'ロウ', 'meaning':'lao động'},
    '連': {'on':'レン', 'meaning':'liên kết, kết nối'},
    '練': {'on':'レン', 'meaning':'luyện tập'},
    '老': {'on':'ロウ', 'meaning':'già'},
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
