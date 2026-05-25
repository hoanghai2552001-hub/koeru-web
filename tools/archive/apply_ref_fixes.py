import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Each tuple: (old_string, new_string)
fixes = [
    # 安
    ('meaning:"rẻ, thấp, bình yên, an toàn"', 'meaning:"rẻ, bình yên, an toàn"'),
    # 飲
    ('on:"イン、オン"', 'on:"イン"'),
    # 何
    ('meaning:"cái gì, cái nào"', 'meaning:"cái gì, bao nhiêu"'),
    # 六
    ('on:"リク、ロク"', 'on:"ロク"'),
    # 来
    ('on:"タイ、ライ"', 'on:"ライ"'),
    # 名
    ('on:"ミョウ、メイ"', 'on:"メイ"'),
    ('meaning:"danh, tên"', 'meaning:"tên"'),
    # 万
    ('on:"バン、マン"', 'on:"マン"'),
    ('meaning:"vạn (mười ngàn)"', 'meaning:"vạn (10.000)"'),
    # 毎
    ('meaning:"mỗi, mọi"', 'meaning:"mỗi"'),
    # 聞
    ('on:"ブン、モン"', 'on:"ブン"'),
    ('meaning:"nghe, hỏi"', 'meaning:"nghe"'),
    # 分
    ('on:"フン、ブ、ブン"', 'on:"フン、ブン"'),
    ('meaning:"phút, phân chia, hiểu"', 'meaning:"phút, chia, hiểu"'),
    # 百
    ('on:"ヒャク、ビャク"', 'on:"ヒャク"'),
    # 半
    ('meaning:"một nửa"', 'meaning:"nửa"'),
    # 八
    ('on:"ハチ、ハツ"', 'on:"ハチ"'),
    # 白
    ('on:"ハク、ビャク"', 'on:"ハク"'),
    # 入
    ('on:"ジュ、ニュウ"', 'on:"ニュウ"'),
    ('meaning:"vào"', 'meaning:"vào, nhập"'),
    # 日 — reorder
    ('on:"ジツ、ニチ"', 'on:"ニチ、ジツ"'),
    # 二
    ('on:"ジ、ニ"', 'on:"ニ"'),
    # 南
    ('on:"ナ、ナン"', 'on:"ナン"'),
    # 読
    ('on:"トウ、トク、ドク"', 'on:"ドク"'),
    # 道
    ('on:"トウ、ドウ"', 'on:"ドウ"'),
    ('meaning:"đường"', 'meaning:"đường, đạo"'),
    # 土
    ('on:"ト、ド"', 'on:"ド"'),
    ('meaning:"đất"', 'meaning:"đất, thứ bảy"'),
    # 天
    ('meaning:"trời, thiên đàng, bầu trời"', 'meaning:"trời, thiên"'),
    # 中
    ('meaning:"trung tâm, giữa, chín, bên trong, ý nghĩa"', 'meaning:"giữa, trong"'),
    # 大
    ('on:"タイ、ダイ"', 'on:"ダイ"'),
    # 足
    ('meaning:"chân, đầy đủ"', 'meaning:"chân, đủ"'),
    # 先
    ('meaning:"đầu, trước"', 'meaning:"trước, đầu tiên"'),
    # 千
    ('meaning:"một ngàn"', 'meaning:"một nghìn"'),
    # 川
    ('meaning:"sông, ba"', 'meaning:"sông"'),
    # 西
    ('on:"サイ、ス、セイ"', 'on:"セイ"'),
    # 生
    ('on:"ショウ、セイ"', 'on:"セイ"'),
    # 食
    ('on:"ショク、ジキ"', 'on:"ショク"'),
    ('meaning:"ăn, thức ăn, đồ ăn"', 'meaning:"ăn"'),
    # 上
    ('on:"シャン、ショウ、ジョウ"', 'on:"ジョウ"'),
    ('meaning:"trên, phía trên"', 'meaning:"trên, lên"'),
    # 少
    ('meaning:"một chút"', 'meaning:"ít, một chút"'),
    # 小
    ('meaning:"nhỏ, bé"', 'meaning:"nhỏ"'),
    # 女
    ('on:"ジョ、ニョ、ニョウ"', 'on:"ジョ"'),
    ('meaning:"phụ nữ"', 'meaning:"phụ nữ, con gái"'),
    # 出
    ('on:"シュツ、スイ"', 'on:"シュツ"'),
    ('meaning:"đến, ra, đi"', 'meaning:"ra, xuất"'),
    # 十
    ('on:"ジッ、ジュウ、ジュッ"', 'on:"ジュウ"'),
    # 手
    ('on:"シュ、ズ"', 'on:"シュ"'),
    # 社
    ('meaning:"đền, công ty"', 'meaning:"công ty, đền"'),
    # 車
    ('meaning:"xe, xe hơi"', 'meaning:"xe"'),
    # 時
    ('meaning:"thời gian, giờ"', 'meaning:"giờ, thời gian"'),
    # 子
    ('on:"シ、ス、ツ"', 'on:"シ"'),
    ('meaning:"đứa bé, trẻ con"', 'meaning:"đứa trẻ, con"'),
    # 山
    ('on:"サン、セン"', 'on:"サン"'),
    # 三
    ('on:"サン、ゾウ"', 'on:"サン"'),
    # 左
    ('on:"サ、シャ"', 'on:"サ"'),
    # 今
    ('on:"キン、コン"', 'on:"コン"'),
    # 行
    ('on:"アン、ギョウ、コウ"', 'on:"コウ、ギョウ"'),
    # 口
    ('on:"ク、コウ"', 'on:"コウ"'),
    # 校
    ('on:"キョウ、コウ"', 'on:"コウ"'),
    ('meaning:"đúng, trường học"', 'meaning:"trường học"'),
    # 語
    ('meaning:"ngôn ngữ, từ, lời nói"', 'meaning:"ngôn ngữ"'),
    # 午
    ('meaning:"trưa, 12 giờ"', 'meaning:"trưa"'),
    # 後
    ('on:"コウ、ゴ"', 'on:"ゴ"'),
    ('meaning:"sau, phía sau"', 'meaning:"sau"'),
    # 五
    ('meaning:"năm (số 5)"', 'meaning:"năm (số)"'),
    # 古
    ('meaning:"cũ, cổ, xưa"', 'meaning:"cũ"'),
    # 言
    ('on:"ゲン、ゴン"', 'on:"ゲン"'),
    ('meaning:"nói, ngôn ngữ"', 'meaning:"nói"'),
    # 月
    ('on:"ガツ、ゲツ"', 'on:"ゲツ"'),
    # 空
    ('meaning:"bầu trời"', 'meaning:"bầu trời, trống"'),
    # 金
    ('on:"キン、コン、ゴン"', 'on:"キン"'),
    ('meaning:"vàng, tiền"', 'meaning:"tiền, vàng"'),
    # 魚
    ('meaning:"con cá"', 'meaning:"cá"'),
    # 休
    ('meaning:"ngày, ngủ"', 'meaning:"nghỉ"'),
    # 九
    ('on:"キュウ、ク"', 'on:"キュウ"'),
    # 気
    ('on:"キ、ケ"', 'on:"キ"'),
    ('meaning:"tinh thần, tâm trạng"', 'meaning:"tinh thần, khí"'),
    # 間
    ('on:"カン、ケン"', 'on:"カン"'),
    ('meaning:"trong khoảng, ở giữa"', 'meaning:"giữa, khoảng"'),
    # 外
    ('on:"ガイ、ゲ"', 'on:"ガイ"'),
]

ok = miss = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        ok += 1
    else:
        print(f'NOT FOUND: {old[:70]}')
        miss += 1

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Sửa {ok}/{len(fixes)} | ❌ Không tìm thấy: {miss}')
