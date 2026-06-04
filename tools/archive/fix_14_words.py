"""Fix 14 words còn nghĩa tiếng Anh"""
import re
from pathlib import Path

JS = Path(__file__).parent.parent / "js"

# (word, old_meaning, new_vietnamese)
FIXES = [
    ("漁村", "fishing village", "làng chài"),
    ("山村", "mountain village", "làng miền núi"),
    ("番頭", "(head) clerk", "quản lý cửa hàng; trưởng quầy"),
    ("亡くす", "to lose (through death; e.g. a wife, child)", "mất (người thân qua đời)"),
    ("熱湯", "boiling water", "nước sôi"),
    ("領収書", "formal receipt (of payment; oft. hand-written)", "biên lai; hóa đơn chính thức"),
    ("漁獲", "fishing", "đánh bắt cá; sản lượng cá"),
    ("収穫", "catch (fishing)", "thu hoạch"),
    ("渇水", "water shortage", "thiếu nước; hạn nước"),
    ("浄水", "clean water", "nước sạch"),
    ("魚釣", "fishing", "câu cá"),
    ("貴霜", "Kushan (dynasty of India; approx. 60-375 CE)", "Quý Sương (triều đại Ấn Độ)"),
    ("貴霜朝", "Kushan dynasty (of India; approx. 60-375 CE)", "triều đại Quý Sương (Ấn Độ)"),
    ("師範学校", "normal school (Japan; 1872-1947)", "trường sư phạm"),
]

total = 0
for lv in ['n5','n4','n3','n2','n1']:
    path = JS / f"kanji-data-{lv}.js"
    content = path.read_text(encoding='utf-8')
    for word, old_m, new_m in FIXES:
        # Match "w":"word",...,"m":"old_m"
        pattern = r'("w":"' + re.escape(word) + r'","r":"[^"]*","m":")' + re.escape(old_m) + r'(")'
        new_content, cnt = re.subn(pattern, r'\g<1>' + new_m + r'\g<2>', content)
        if cnt:
            content = new_content
            total += cnt
            print(f"  {lv.upper()} {word} → {new_m}")
    path.write_text(content, encoding='utf-8')

print(f"\nTổng fix: {total}")

# Rebuild
parts = []
for lv in ['n5','n4','n3','n2','n1']:
    c = (JS/f"kanji-data-{lv}.js").read_text(encoding='utf-8')
    start = c.index('['); end = c.rindex(']')+1
    inner = c[start+1:end-1].strip().rstrip(',')
    if inner: parts.append(inner)
(JS/'kanji-data.js').write_text('window.KANJI_DATA = [\n'+',\n'.join(parts)+'\n];\n', encoding='utf-8')
print("kanji-data.js rebuilt")
