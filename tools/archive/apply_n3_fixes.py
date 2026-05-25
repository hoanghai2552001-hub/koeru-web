import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = [
    ('on:"カ"',                         'on:"カ、ケ"'),  # 化 — but this would affect all カ-only entries, use targeted approach below
    ('meaning:"biến hóa"',              'meaning:"hóa, biến đổi"'),
    ('on:"ダイ、ナイ"',                  'on:"ナイ"'),
    ('on:"タン、ハン、ホ"',              'on:"ハン"'),
    ('meaning:"phản đối"',              'meaning:"phản đối, ngược lại"'),
    ('on:"ヒョウ、ビョウ、ヘイ"',        'on:"ヘイ"'),
    ('meaning:"băng giá"',              'meaning:"băng"'),
    ('on:"コク、シャク、セキ"',          'on:"セキ"'),
    ('meaning:"khác"',                  'meaning:"khác, người khác"'),
    ('meaning:"gia tăng"',              'meaning:"thêm, gia tăng"'),
    ('on:"キ、チュウ"',                  'on:"チュウ"'),
    ('meaning:"giao thông"',            'meaning:"giao, trao đổi"'),
    ('on:"ジョウ、セイ"',                'on:"セイ"'),
    ('meaning:"đến, thức dậy"',         'meaning:"thành, trở thành"'),
    ('meaning:"toàn bộ"',               'meaning:"toàn bộ, toàn"'),
    ('meaning:"tranh giành"',           'meaning:"tranh giành, chiến"'),
    ('meaning:"trách nhiệm"',           'meaning:"giao phó, trách nhiệm"'),
    ('meaning:"lợi ích"',               'meaning:"lợi ích, thuận tiện"'),
    ('meaning:"kết thúc, chiến tranh"', 'meaning:"phòng, ngăn chặn"'),
    ('meaning:"câu trả lời, về, trở lại"', 'meaning:"trả lại, đáp"'),
    ('meaning:"một, người, cơ thể"',    'meaning:"thân thể, bản thân"'),
    ('meaning:"hoàn thành"',            'meaning:"hoàn thành, hoàn hảo"'),
    ('meaning:"góc cạnh"',              'meaning:"góc"'),
    ('on:"ギョウ、ケイ"',                'on:"ケイ"'),
    ('meaning:"hình dạng"',             'meaning:"hình dạng, hình"'),
    ('meaning:"bắt đầu, khởi đầu, nhìn, thấy"', 'meaning:"hy vọng, hiếm"'),
    ('meaning:"hạnh phúc"',             'meaning:"hạnh phúc, may mắn"'),
    ('meaning:"giáo dục"',              'meaning:"nuôi, giáo dục"'),
    ('on:"ジョウ、テイ"',                'on:"テイ"'),
    ('meaning:"quyết định"',            'meaning:"xác định, quyết định"'),
    ('meaning:"sinh mệnh"',             'meaning:"sinh mệnh, mạng"'),
    ('on:"ハッ、フラン、ホウ"',          'on:"ホウ"'),
    ('meaning:"pháp luật"',             'meaning:"pháp luật, phương pháp"'),
    ('meaning:"thay đổi"',              'meaning:"thay đổi, biến"'),
    ('on:"ビ、ミ"',                     'on:"ビ"'),
    ('meaning:"vẻ đẹp"',               'meaning:"đẹp"'),
    ('on:"トク、ドク"',                  'on:"ドク"'),
    ('meaning:"tín nhiệm"',             'meaning:"tin, tin tưởng"'),
    ('meaning:"đơn giản"',              'meaning:"đơn giản, đơn"'),
    ('meaning:"sinh hoạt"',             'meaning:"sống, hoạt động"'),
    ('meaning:"cảm xúc"',               'meaning:"cảm giác, cảm xúc"'),
    ('on:"カイ、ゲ"',                   'on:"カイ"'),
    ('meaning:"giải quyết"',            'meaning:"giải quyết, hiểu"'),
    ('meaning:"cấm đoán"',              'meaning:"cấm"'),
    ('on:"ボウ、ム"',                   'on:"ム"'),
    ('on:"キョウ、コウ、ショク"',        'on:"ゾク"'),
    ('meaning:"tuyển chọn"',            'meaning:"chọn"'),
    ('meaning:"lãnh đạo"',              'meaning:"dẫn dắt, hướng dẫn"'),
    ('meaning:"số lượng"',              'meaning:"lượng, số lượng"'),
    ('meaning:"máy móc"',               'meaning:"máy móc, cơ hội"'),
    ('meaning:"cây cầu"',               'meaning:"cầu"'),
    ('meaning:"con sóng"',              'meaning:"sóng"'),
    ('meaning:"ý tưởng"',               'meaning:"ý niệm, nghĩ"'),
    ('meaning:"chiến thắng"',           'meaning:"thắng, vượt"'),
    ('meaning:"chủng loại"',            'meaning:"loại, giống"'),
    ('on:"シャク、セツ"',               'on:"セツ"'),
    ('meaning:"gãy, gập"',              'meaning:"gập, gãy"'),
    ('on:"ザツ、ゾウ"',                 'on:"ザツ"'),
    ('meaning:"quan sát"',              'meaning:"quan sát, điều tra"'),
    ('meaning:"giao tiếp, bên cạnh"',   'meaning:"dịp, khi"'),
    ('meaning:"muộn, trễ, số"',         'meaning:"tính toán"'),
    ('meaning:"phân tán"',              'meaning:"phân tán, tan"'),
    ('on:"サン、ザン"',                  'on:"ザン"'),
    ('on:"サイ、ザイ、ゾク"',            'on:"ザイ"'),
    ('meaning:"hiện tại"',              'meaning:"tồn tại, ở"'),
    ('on:"サ、サイ"',                   'on:"サイ"'),
    ('meaning:"đâm chích"',             'meaning:"đâm, thẻ"'),
    ('meaning:"dáng vẻ"',               'meaning:"dáng vẻ, tư thế"'),
    ('meaning:"người, mát"',            'meaning:"lạnh"'),
    ('on:"ライ、レイ"',                  'on:"レイ"'),
    ('meaning:"lễ nghi"',               'meaning:"lễ phép, lễ nghi"'),
    ('meaning:"đàn ông, tốt, giỏi, luật pháp"', 'meaning:"lệnh, pháp lệnh"'),
    ('on:"ル、ロ"',                     'on:"ロ"'),
    ('meaning:"con đường"',             'meaning:"đường, lộ"'),
    ('meaning:"liên kết"',              'meaning:"liên kết, kết nối"'),
    ('meaning:"cũ, già, đàn ông"',      'meaning:"già"'),
]

ok = miss = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        ok += 1
    else:
        print(f'NOT FOUND: {old}')
        miss += 1

# 化: targeted fix for on-yomi (カ → カ、ケ only for 化)
content = re.sub(r'(kanji:"化"[^}]+)on:"カ"', r'\1on:"カ、ケ"', content)

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Sửa {ok}/{len(fixes)} | ❌ Không tìm thấy: {miss}')
