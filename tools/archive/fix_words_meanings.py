"""
Fix words[].m meanings: loại bỏ phần tiếng Anh trong các entry song ngữ.
Logic:
  - Tách theo '; ' hoặc ', ' (khi rõ ràng là separator, không phải chú thích)
  - Giữ lại các phần có chứa ký tự tiếng Việt có dấu
  - Nếu không có phần nào có tiếng Việt → giữ nguyên (proper noun hoặc đã OK)
  - Ghép lại bằng '; '
Sau đó sync vào kanji-data.js.
"""
import re, shutil, json
from pathlib import Path

PROJECT = Path(r"C:\Users\hoang\Desktop\BUILD WEB KOERU")

VI_CHARS = set("àáảãạăắặằẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
               "ÀÁẢÃẠĂẮẶẰẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ")

# Các từ/cụm tiếng Anh thường gặp cần bỏ (lowercase, so sánh sau khi lower())
EN_WORDS = {
    'to','the','a','an','of','in','on','at','by','for','with','and','or','not',
    'is','be','do','go','come','make','take','have','get','give','put','see',
    'know','think','say','look','want','use','find','tell','ask','seem','feel',
    'try','leave','call','keep','let','begin','show','hear','play','run','move',
    'change','point','turn','start','carry','write','set','stop','cut','open',
    'appear','lead','grow','fall','reach','kill','remain','suggest','raise',
    'pass','sell','require','report','decide','pull','break','become','meet',
    'send','build','stand','lose','pay','run','include','continue','lie','bring',
    'happen','provide','hold','turn','follow','win','drive','choose','strike',
    'allow','add','spend','return','speak','receive','hit','draw','base','discuss',
    'finish','act','face','place','cover','line','meet','join','serve','light',
    'fit','sit','stay','force','develop','plan','control','manage','support',
    'power','force','action','ability','nature','value','form','level','rate',
    'cause','case','fact','mind','system','field','body','part','group','life',
    'moment','type','view','area','body','result','purpose','sense','matter',
    'subject','increase','general','special','free','state','high','main',
    'public','private','small','large','long','short','great','single','common',
    'right','left','hard','real','old','new','young','full','clear','strong',
    'important','possible','political','economic','social','national','local',
    'powerful','beautiful','difficult','different','following','major',
    # Game/education terms
    'shift','variation','warp','warped','curve','conflagration','lance',
    'scaffold','scaffold','weave','grapple',
}

def has_vi(s):
    return any(c in VI_CHARS for c in s)

def is_mostly_english(segment):
    """Trả về True nếu segment chủ yếu là tiếng Anh."""
    if has_vi(segment):
        return False
    words = re.findall(r'[a-zA-Z]+', segment)
    if not words:
        return False
    en_count = sum(1 for w in words if w.lower() in EN_WORDS)
    # Nếu có ít nhất 1 từ EN và không có tiếng Việt
    return len(words) > 0 and (en_count > 0 or len(words) > 1)

def is_proper_noun(segment):
    """Proper noun: viết hoa đầu, không có dấu VI, ngắn."""
    s = segment.strip()
    if not s or has_vi(s):
        return False
    words = s.split()
    return all(w[0].isupper() for w in words if w) and len(words) <= 4

def clean_meaning_m(m):
    """Làm sạch 1 giá trị words[].m."""
    # Tách theo '; ' (separator chính)
    parts = [p.strip() for p in m.split('; ') if p.strip()]

    vi_parts = [p for p in parts if has_vi(p)]
    non_vi = [p for p in parts if not has_vi(p)]

    if not vi_parts:
        # Không có tiếng Việt → giữ nguyên (proper noun hoặc đã OK)
        return m

    # Có tiếng Việt → chỉ giữ phần tiếng Việt
    # Ngoại lệ: giữ proper noun nếu nó đi kèm nghĩa VI
    kept = vi_parts[:]

    # Trong phần VI, xử lý thêm: nếu còn ", EN_PART" trong 1 segment
    cleaned = []
    for seg in kept:
        # Tách tiếp bằng ', ' nếu còn EN lẫn lộn
        sub = [s.strip() for s in seg.split(', ') if s.strip()]
        vi_sub = [s for s in sub if has_vi(s)]
        if vi_sub and len(vi_sub) < len(sub):
            cleaned.append(', '.join(vi_sub))
        else:
            cleaned.append(seg)

    result = '; '.join(cleaned)
    return result if result else m


def fix_file(path, label):
    shutil.copy2(path, str(path) + '.bakm')
    with open(path, encoding='utf-8') as f:
        content = f.read()

    original = content
    fixed_count = 0
    unchanged = 0

    def replacer(match):
        nonlocal fixed_count, unchanged
        old_m = match.group(1)
        new_m = clean_meaning_m(old_m)
        if new_m != old_m:
            fixed_count += 1
            return f'"m":"{new_m}"'
        unchanged += 1
        return match.group(0)

    content = re.sub(r'"m":"(.*?)"', replacer, content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  {label}: fixed={fixed_count}, unchanged={unchanged}")
    return fixed_count


# ── Fix N-level files ──────────────────────────────────────────────────────
print("=== Fix words[].m meanings ===")
total_fixed = 0
for level in ['n5', 'n4', 'n3']:
    path = PROJECT / 'js' / f'kanji-data-{level}.js'
    total_fixed += fix_file(path, f'kanji-data-{level}.js')

# ── Sync vào kanji-data.js ─────────────────────────────────────────────────
print("\n=== Sync meanings vào kanji-data.js ===")
main_path = PROJECT / 'js' / 'kanji-data.js'
shutil.copy2(main_path, str(main_path) + '.bakm')

with open(main_path, encoding='utf-8') as f:
    main_content = f.read()

# Build lookup: kanji_char → toàn bộ words[] string từ N-level files (đã clean)
kanji_words = {}
for level in ['n5', 'n4', 'n3']:
    path = PROJECT / 'js' / f'kanji-data-{level}.js'
    with open(path, encoding='utf-8') as f:
        nc = f.read()
    # Extract từng entry
    for m in re.finditer(r'\{kanji:"(.)".+?(?=\},?\n\{kanji:|\n\];)', nc, re.DOTALL):
        entry_text = m.group(0)
        k = m.group(1)
        words_m = re.search(r'words:\[(.+?)\]', entry_text, re.DOTALL)
        if words_m:
            kanji_words[k] = words_m.group(0)  # "words:[...]"

print(f"  Words loaded từ N3+N4+N5: {len(kanji_words)} kanji")

# Replace words[] trong kanji-data.js cho các kanji đã clean
sync_count = 0
def sync_replacer(m):
    global sync_count
    entry = m.group(0)
    k_m = re.search(r'kanji:"(.)"', entry)
    if not k_m:
        return entry
    k = k_m.group(1)
    if k not in kanji_words:
        return entry
    # Replace words section
    new_entry = re.sub(r'words:\[.+?\]', kanji_words[k], entry, flags=re.DOTALL)
    if new_entry != entry:
        sync_count += 1
    return new_entry

main_content = re.sub(
    r'\{kanji:".".+?(?=\},?\n\{kanji:|\n\];)',
    sync_replacer, main_content, flags=re.DOTALL
)

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(main_content)

print(f"  Synced {sync_count} kanji entries vào kanji-data.js")
print(f"\n✅ Tổng: {total_fixed} word meanings được làm sạch")
