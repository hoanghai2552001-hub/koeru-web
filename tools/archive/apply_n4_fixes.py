import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = [
    ('on:"リキ、リョク"',           'on:"リョク"'),
    ('on:"ク、グ、コウ"',            'on:"コウ"'),
    ('meaning:"công sức"',          'meaning:"công việc, xây dựng"'),
    ('on:"ガン、ゲン"',              'on:"ゲン"'),
    ('meaning:"bắt đầu, khởi đầu, thời gian"', 'meaning:"ban đầu, nguyên gốc"'),
    ('meaning:"con trâu, bò"',      'meaning:"bò, trâu"'),
    ('meaning:"con chó"',           'meaning:"chó"'),
    ('meaning:"văn học"',           'meaning:"văn, chữ"'),
    ('meaning:"phương hướng"',      'meaning:"hướng, cách"'),
    ('on:"サイ、セツ"',              'on:"セツ"'),
    ('meaning:"cắt, đứt"',          'meaning:"cắt, quan trọng"'),
    ('meaning:"đại diện, thay thế"','meaning:"thay thế, đời"'),
    ('on:"セ、セイ、ソウ"',          'on:"セ、セイ"'),
    ('meaning:"thế giới"',          'meaning:"đời, thế giới"'),
    ('meaning:"đúng, công lý, phải"','meaning:"đúng, chính xác"'),
    ('on:"キョウ、ケイ"',            'on:"ケイ"'),
    ('on:"キョ、コ"',               'on:"キョ"'),
    ('meaning:"quá khứ"',           'meaning:"qua, đi"'),
    ('meaning:"thành phố, thị trấn"','meaning:"thành phố"'),
    ('meaning:"đường, rộng"',       'meaning:"rộng"'),
    ('on:"シュ、シュウ、ス"',        'on:"シュ"'),
    ('meaning:"chủ nhân"',          'meaning:"chủ, chính"'),
    ('meaning:"thư, làng, từ, lời nói"', 'meaning:"chữ, ký tự"'),
    ('on:"ウ、ユウ"',               'on:"ユウ"'),
    ('meaning:"cùng"',              'meaning:"giống nhau, cùng"'),
    ('on:"シキ、ショク"',            'on:"ショク"'),
    ('on:"サッ、ソウ"',              'on:"ソウ"'),
    ('on:"ジ、チ"',                 'on:"チ"'),
    ('meaning:"đất, thứ bảy"',      'meaning:"đất, vùng"'),
    ('meaning:"thị trấn, làng"',    'meaning:"làng"'),
    ('on:"タイ、テイ"',              'on:"タイ"'),
    ('on:"ダイ、テイ、デ"',          'on:"テイ"'),
    ('on:"シャク、セキ"',            'on:"セキ"'),
    ('meaning:"riêng biệt"',        'meaning:"riêng biệt, chia tay"'),
    ('meaning:"bác sĩ, thuốc"',     'meaning:"bác sĩ, y học"'),
    ('on:"コン"',                   'on:"キン"'),
    ('on:"サ、サク"',               'on:"サク"'),
    ('meaning:"làm"',               'meaning:"làm, tạo"'),
    ('on:"ジ、ズ"',                 'on:"ジ"'),
    ('meaning:"công việc"',         'meaning:"việc, sự"'),
    ('meaning:"mùi vị"',            'meaning:"vị, hương vị"'),
    ('meaning:"trang phục"',        'meaning:"quần áo"'),
    ('on:"ブツ、モツ"',              'on:"ブツ"'),
    ('on:"フ、ブ、ホ"',              'on:"ホ"'),
    ('meaning:"cổng, cửa"',         'meaning:"cổng, môn"'),
    ('meaning:"buổi tối, đêm"',     'meaning:"ban đêm"'),
    ('on:"ミョウ、ミン、メイ"',      'on:"メイ"'),
    ('meaning:"ánh sáng, sáng"',    'meaning:"sáng, rõ"'),
    ('meaning:"xanh lam, xanh lá"', 'meaning:"xanh"'),
    ('meaning:"ghi chú"',           'meaning:"chú ý, đổ"'),
    ('meaning:"buổi trưa"',         'meaning:"ban ngày, trưa"'),
    ('on:"サ、チャ"',               'on:"チャ"'),
    ('meaning:"kết thúc, chờ"',     'meaning:"chờ"'),
    ('meaning:"gửi đi"',            'meaning:"gửi"'),
    ('on:"-ノン、イン、オン"',       'on:"オン"'),
    ('meaning:"gấp"',               'meaning:"gấp, khẩn cấp"'),
    ('meaning:"dụng cụ đo"',        'meaning:"kế hoạch, đo"'),
    ('on:"ケン、コン"',              'on:"ケン"'),
    ('meaning:"suy nghĩ"',          'meaning:"nghĩ"'),
    ('on:"ショウ、ジョウ"',          'on:"ジョウ"'),
    ('meaning:"lên xe"',            'meaning:"lên (xe)"'),
    ('meaning:"tờ giấy"',           'meaning:"giấy"'),
    ('meaning:"trở về"',            'meaning:"về"'),
    ('meaning:"thức dậy, dùng, sử dụng"', 'meaning:"thức dậy"'),
    ('on:"カ、ガ、ゲ"',              'on:"カ"'),
    ('on:"カ、ケ"',                 'on:"カ"'),
    ('on:"ビョウ、ヘイ"',            'on:"ビョウ"'),
    ('meaning:"ốm đau"',            'meaning:"bệnh"'),
    ('meaning:"du lịch, chuyến đi"','meaning:"du lịch"'),
    ('on:"ツ、ツウ"',               'on:"ツウ"'),
    ('meaning:"đi qua"',            'meaning:"đi qua, thông"'),
    ('on:"キョウ、ゴウ"',            'on:"キョウ"'),
    ('on:"シュウ、ジュ"',            'on:"シュウ"'),
    ('meaning:"học tập"',           'meaning:"học, tập"'),
    ('on:"キョウ、キン、ケイ"',      'on:"ケイ"'),
    ('meaning:"xe hơi, quần áo"',   'meaning:"vận chuyển, may mắn"'),
    ('meaning:"mở, cũ, già, biển"', 'meaning:"mở"'),
    ('meaning:"rừng rậm"',          'meaning:"rừng"'),
    ('meaning:"nóng, mùa hè"',      'meaning:"nóng"'),
    ('on:"ジャク、チャク"',          'on:"チャク"'),
    ('meaning:"đến, mặc"',          'meaning:"mặc, đến"'),
    ('meaning:"ngắn, yếu"',         'meaning:"ngắn"'),
    ('on:"ガク、ゴウ、ラク"',        'on:"ガク"'),
    ('meaning:"vui vẻ"',            'meaning:"vui, dễ chịu"'),
]

ok = miss = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        ok += 1
    else:
        print(f'NOT FOUND: {old}')
        miss += 1

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Sửa {ok}/{len(fixes)} | ❌ Không tìm thấy: {miss}')
