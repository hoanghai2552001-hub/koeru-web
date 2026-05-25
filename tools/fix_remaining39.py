#!/usr/bin/env python3
"""Fix 39 remaining English meanings manually."""
import re, os

BASE  = os.path.dirname(os.path.abspath(__file__))
JS    = os.path.join(BASE, '..', 'js', 'kanji-data.js')

# Exact string replacements: (old, new)
FIXES = [
    # 万花鏡 appears twice (万 and 鏡)
    ('"kaleidoscope"',          '"kính vạn hoa"'),
    # 鳥 — double-space Vietnamese (qa_kanji false-positive on comma+space)
    ('"chim non,  chim con"',   '"chim non, chim con"'),
    # 季
    ('"(season of) winter"',    '"mùa đông"'),
    # 頂
    ('"summit (of a mountain)"','"đỉnh núi"'),
    # 袋
    ('"bags and purses (handbags)"', '"túi xách, ví"'),
    # 存
    ('"being alive"',           '"còn sống"'),
    # 蔵
    ('"(in one\'s) possession"', '"sở hữu"'),
    ('"(in one\'s) possession"', '"sở hữu"'),  # fallback
    # 贈
    ('"exchange of presents"',  '"trao đổi quà tặng"'),
    # 泉
    ('"miraculous spring or fountain"', '"suối thiêng"'),
    # 晴
    ('"clear autumnal weather"', '"trời thu trong"'),
    # 制
    ('"(air traffic) controller"', '"kiểm soát viên không lưu"'),
    # 伸
    ('"continuous rise (in market price)"', '"tăng liên tiếp"'),
    # 商
    ('"businessman with political ties"', '"thương nhân có quan hệ chính trị"'),
    # 昨 / 及 (可及的 appears twice)
    ('"day before yesterday"',  '"hôm kia"'),
    # 軒
    ('"one house"',             '"một căn nhà"'),
    # 肩
    ('"shoulder width (breadth)"', '"bề rộng vai"'),
    # 玉
    ('"Saitama (city, prefecture)"', '"Saitama (tỉnh)"'),
    # 硬
    ('"cirrhosis (of the liver)"', '"xơ gan"'),
    # 更
    ('"second month of the lunar calendar"', '"thay quần áo"'),
    # 可 / 及 — same meaning
    ('"as ... as possible"',    '"càng nhiều càng tốt"'),
    # 芋
    ('"potato (Solanum tuberosum)"', '"khoai tây"'),
    # 翁
    ('"lychnis (Lychnis senno)"', '"hoa nhân điệu"'),
    # 叶
    ('"to fulfill (conditions)"', '"thực hiện, đạt được"'),
    # 嚙
    ('"to be involved in"',     '"cắn, liên quan đến"'),
    # 仰
    ('"being amazed"',          '"kinh ngạc"'),
    # 碁
    ('"Go board"',              '"bàn cờ vây"'),
    # 旨
    ('"point of an argument"',  '"luận điểm"'),
    # 儒
    ('"dugong (Dugong dugon)"',  '"cá nàng tiên (dugong)"'),
    # 諦
    ('"four noble truths"',     '"tứ diệu đế"'),
    # 溺
    ('"to struggle in the water"', '"chìm đắm, đuối nước"'),
    # 剥
    ('"to come unstuck from"',  '"bong ra, tróc ra"'),
    # 盛
    ('"growth period (in children)"', '"giai đoạn phát triển"'),
    # 揚
    ('"deep-fried food"',       '"đồ chiên"'),
    # 隔
    ('"to be distant"',         '"cách xa"'),
    # 臭
    ('"sense of smell"',        '"khứu giác"'),
    # 宅 reading fix — separate handling below
]

with open(JS, encoding='utf-8') as f:
    text = f.read()

count = 0
for old, new in FIXES:
    if old in text:
        text = text.replace(old, new)
        count += 1
        print(f'  ✓ {old} → {new}')
    else:
        # Try without escaping
        pass

# Fix 宅 reading: "帰宅" is the reading field but has no kana
# The issue is reading: "帰宅" should be "きたく"  but it's stored in reading field
# Let's find the exact pattern and fix
# words[0] "お宅": reading "帰宅" — meaning the reading key has kanji instead of kana
# Pattern: { "word": "お宅", "reading": "帰宅",
old_tak = '"word": "お宅", "reading": "帰宅"'
new_tak = '"word": "お宅", "reading": "おたく"'
if old_tak in text:
    text = text.replace(old_tak, new_tak)
    count += 1
    print(f'  ✓ 宅 reading fix')
else:
    # Try single quotes style or different spacing
    old_tak2 = "'word': 'お宅', 'reading': '帰宅'"
    if old_tak2 in text:
        text = text.replace(old_tak2, "'word': 'お宅', 'reading': 'おたく'")
        count += 1
        print(f'  ✓ 宅 reading fix (single quotes)')
    else:
        print(f'  ⚠ 宅 reading pattern not found, skipping')

with open(JS, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'\n✅ Đã fix {count} chỗ → {JS}')
