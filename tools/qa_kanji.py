"""
qa_kanji.py — Kiểm tra toàn diện chất lượng dữ liệu phần Kanji
Chạy: python qa_kanji.py
Output: qa_report.html + qa_report.json
"""

import re, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Regex helpers ──────────────────────────────────────────────────────────────
VIET = re.compile(
    r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
    r'ÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]'
)
HIRAGANA   = re.compile(r'[぀-ゟ]')
KATAKANA   = re.compile(r'[゠-ヿ]')
KANJI_RE   = re.compile(r'[一-鿿㐀-䶿]')
JAPANESE   = re.compile(r'[぀-ヿ一-鿿]')
LATIN_ONLY  = re.compile(r'^[a-zA-Z\s\-\(\)\/\.,\'\"0-9]+$')
VALID_LEVEL = {'N5','N4','N3','N2','N1',''}

# Từ VN ngắn không dấu hợp lệ (phổ biến nhất)
VIET_NO_MARK = {
    'mua','ban','nha','xe','ao','bo','co','do','ga','go','la','le','lo',
    'ma','me','mi','mo','na','ne','ni','no','ra','re','ro','sa','se','si',
    'ta','te','ti','to','tu','va','ve','vi','vo','xa','xe','xi','xo','xu',
    'an','uong','ngu','di','den','ve','len','vao',
    'lon','nho','cao','dai','ngan','mau','cham','tot','xau','moi','cu',
    'toi','anh','chi','em','ong','ba','co','ngay','dem','gio','thang',
    'mot','hai','ba','bon','nam','sau','bay','tam','chin','muoi',
    'tay','chan','mat','dau','lung','vai','bung',
}

# Từ/cụm tiếng Anh đặc trưng — nếu xuất hiện → chắc chắn là EN
EN_MARKERS = {
    'the','a','an','of','in','on','at','to','for','with','by','from',
    'and','or','not','is','are','was','were','be','been','have','has',
    'that','this','which','who','how','what','when','where',
    'one','two','three','four','five','six','seven','eight','nine','ten',
    'person','people','thing','place','time','way','day','year',
    'make','take','get','go','come','see','know','think','look',
    'good','bad','big','small','large','new','old','high','low',
    'national','general','special','main','local','original',
    'school','university','company','government','family',
    'opening','closing','finely','chopped','microscopic','extensive',
    'exemplary','universal','heresy','hornbeam','birch','bookshelf',
    'construction','crucifixion','kaleidoscope','resuscitation',
    'sumo','wrestling','fountain','pen','measuring','ruler',
    'jupiter','planet','spindletree','euonymus','japonicus',
    'approval','policy','hostilities','northern','extremity',
    'arc','cross','lively','living','being','helped',
}

def is_viet(s):   return bool(VIET.search(s)) if s else False
def is_jp(s):     return bool(JAPANESE.search(s)) if s else False

def is_english(s):
    """Phát hiện nghĩa tiếng Anh — dùng cho meaning và words[].m."""
    if not s: return False
    if is_viet(s) or is_jp(s): return False
    s2 = s.strip()
    if not LATIN_ONLY.match(s2): return False
    # Từ rất ngắn (≤4 ký tự) → có thể là VN không dấu
    if len(s2) <= 4: return False
    # Whitelist VN không dấu
    if s2.lower() in VIET_NO_MARK: return False
    # Kiểm tra từ/cụm EN đặc trưng
    words_list = re.split(r'[\s\(\)\-\/,\.]+', s2.lower())
    words_list = [w for w in words_list if w]
    if any(w in EN_MARKERS for w in words_list): return True
    # Cụm ≥ 3 từ Latin không có dấu VN → gần như chắc là EN
    if len(words_list) >= 3: return True
    return False

def is_english_hanviet(s):
    """Kiểm tra hanviet — ít nghiêm ngặt hơn vì HV thường ngắn, không dấu."""
    if not s: return False
    if is_viet(s): return False  # có dấu VN → OK
    # HV luôn là chữ HOA tiếng Việt không dấu, 2-8 ký tự
    # Chỉ flag nếu là từ tiếng Anh thực sự
    s2 = s.strip().lower()
    return s2 in EN_MARKERS

# ── Parse kanji-data.js ────────────────────────────────────────────────────────
def parse_kanji_js(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries = []
    for line in content.splitlines():
        s = line.strip()
        if not s.startswith('{kanji:'): continue
        s = s.rstrip(',')
        try:
            j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', s)
            entries.append(json.loads(j))
        except:
            try:
                entries.append({'_raw': s[:80], '_parse_error': True})
            except: pass
    return entries

# ── Kiểm tra từng kanji ────────────────────────────────────────────────────────
def check_kanji(obj, idx):
    issues = []
    warn   = []

    def err(msg):  issues.append(msg)
    def note(msg): warn.append(msg)

    if obj.get('_parse_error'):
        err(f'Không parse được dòng JS')
        return issues, warn

    k = obj.get('kanji','')
    if not k:                              err('Thiếu trường kanji')
    elif not KANJI_RE.match(k):            err(f'kanji "{k}" không phải ký tự Hán')

    # hanviet — chữ HOA tiếng Việt. Kokuji dùng nhãn riêng ("(国字)") hoặc "—" → bỏ qua
    KOKUJI_MARKS = ('—', '(国字)')
    hv = obj.get('hanviet','')
    if not hv:                             err('Thiếu hanviet')
    elif hv not in KOKUJI_MARKS and not hv.isupper():
        note(f'hanviet "{hv}" chưa VIẾT HOA')

    # readings — nhiều kanji chỉ có on (万,百,電) hoặc chỉ có kun (峠 kokuji).
    # On-only / kun-only là HỢP LỆ; chỉ cảnh báo khi cả hai đều trống.
    on = obj.get('on','')
    kun = obj.get('kun','')
    on_empty = not on or on == '—'
    kun_empty = not kun or kun == '—'
    if on_empty and kun_empty:
        note('Không có cách đọc nào (on & kun đều trống)')
    if not on_empty and not KATAKANA.search(on):
        err(f'On "{on}" không phải Katakana')
    if not kun_empty and not HIRAGANA.search(kun) and not KATAKANA.search(kun):
        err(f'Kun "{kun}" không có Hiragana/Katakana')

    # meaning (VN)
    meaning = obj.get('meaning','')
    if not meaning:                        err('Thiếu meaning (nghĩa VN)')
    elif is_english(meaning):             err(f'meaning "{meaning[:40]}" là tiếng Anh')

    # level
    level = obj.get('level','')
    if level not in VALID_LEVEL:           err(f'level "{level}" không hợp lệ')
    if not level:                          note('level trống')

    # strokes
    strokes = obj.get('strokes')
    if strokes and (not isinstance(strokes, int) or strokes < 1 or strokes > 64):
        note(f'strokes={strokes} có vẻ bất thường')

    # words
    words = obj.get('words', [])
    if not words:
        note('Không có từ ghép (words trống)')
    else:
        for wi, w in enumerate(words):
            ww = w.get('w','')
            wr = w.get('r','')
            wm = w.get('m','')

            if not ww:             err(f'words[{wi}].w trống')
            if not wr:             err(f'words[{wi}] "{ww}": thiếu reading')
            elif not HIRAGANA.search(wr) and not KATAKANA.search(wr):
                err(f'words[{wi}] "{ww}": reading "{wr}" không có kana')
            # Kiểm tra reading không phải chính tả của từ khác
            if ww and wr and is_jp(wr) and KANJI_RE.search(wr):
                note(f'words[{wi}] "{ww}": reading "{wr}" chứa kanji (nên là furigana)')

            if not wm:             err(f'words[{wi}] "{ww}": thiếu nghĩa')
            elif is_english(wm):   err(f'words[{wi}] "{ww}": nghĩa "{wm}" tiếng Anh')

    return issues, warn

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    js_path = os.path.join(BASE, '..', 'js', 'kanji-data.js')
    print(f'📂 Đọc {js_path}...')
    entries = parse_kanji_js(js_path)
    print(f'   {len(entries)} kanji\n')

    results = []
    total_errors = 0
    total_warns  = 0
    err_kanji    = []
    warn_kanji   = []

    # Thống kê theo loại lỗi
    error_types  = {}
    warn_types   = {}

    for i, obj in enumerate(entries):
        issues, warns = check_kanji(obj, i)
        k = obj.get('kanji', f'[{i}]')
        level = obj.get('level','?')

        if issues:
            total_errors += len(issues)
            err_kanji.append(k)
            for e in issues:
                t = e.split(' ')[0]
                error_types[t] = error_types.get(t,0)+1
        if warns:
            total_warns += len(warns)
            warn_kanji.append(k)
            for w in warns:
                t = w.split(' ')[0]
                warn_types[t] = warn_types.get(t,0)+1

        results.append({
            'idx': i, 'kanji': k, 'level': level,
            'errors': issues, 'warnings': warns
        })

    # ── In tóm tắt ───────────────────────────────────────────────────────────
    print('='*60)
    print('KẾT QUẢ KIỂM TRA')
    print('='*60)
    print(f'  Tổng kanji      : {len(entries)}')
    print(f'  Có lỗi (errors) : {len(err_kanji)} kanji  ({total_errors} lỗi)')
    print(f'  Có cảnh báo     : {len(warn_kanji)} kanji  ({total_warns} cảnh báo)')
    print(f'  Sạch hoàn toàn  : {len(entries)-len(set(err_kanji+warn_kanji))} kanji')

    if error_types:
        print('\n  Loại lỗi phổ biến:')
        for t,c in sorted(error_types.items(), key=lambda x:-x[1])[:8]:
            print(f'    {c:4d}×  {t}')

    if warn_types:
        print('\n  Loại cảnh báo phổ biến:')
        for t,c in sorted(warn_types.items(), key=lambda x:-x[1])[:8]:
            print(f'    {c:4d}×  {t}')

    # In mẫu lỗi
    print('\n  Ví dụ lỗi (10 kanji đầu có lỗi):')
    shown = 0
    for r in results:
        if r['errors'] and shown < 10:
            print(f'    [{r["level"]}] {r["kanji"]} — {r["errors"][0]}')
            shown += 1

    # ── Ghi JSON ──────────────────────────────────────────────────────────────
    json_path = os.path.join(BASE, 'qa_report.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': len(entries),
                'with_errors': len(err_kanji),
                'total_errors': total_errors,
                'with_warnings': len(warn_kanji),
                'total_warnings': total_warns,
                'clean': len(entries) - len(set(err_kanji+warn_kanji)),
            },
            'results': [r for r in results if r['errors'] or r['warnings']]
        }, f, ensure_ascii=False, indent=2)
    print(f'\n💾 Chi tiết → {json_path}')

    # ── Ghi HTML report ───────────────────────────────────────────────────────
    html_path = os.path.join(BASE, 'qa_report.html')
    write_html(results, html_path, len(entries), total_errors, total_warns)
    print(f'🌐 HTML report → {html_path}')

    return total_errors

# ── HTML report ────────────────────────────────────────────────────────────────
def write_html(results, path, total, total_errors, total_warns):
    rows = []
    for r in results:
        if not r['errors'] and not r['warnings']: continue
        cls = 'err' if r['errors'] else 'warn'
        issues_html = ''.join(
            f'<li class="e">❌ {e}</li>' for e in r['errors']
        ) + ''.join(
            f'<li class="w">⚠️ {w}</li>' for w in r['warnings']
        )
        rows.append(f'''
        <tr class="{cls}">
          <td class="lv">{r["level"]}</td>
          <td class="kj">{r["kanji"]}</td>
          <td><ul>{issues_html}</ul></td>
        </tr>''')

    html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Koeru QA Report — Kanji</title>
<style>
  body {{ font-family: sans-serif; font-size:14px; margin:24px; background:#f8f9fa; }}
  h1 {{ color:#1a1a2e; }}
  .summary {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:24px; }}
  .card {{ background:#fff; border-radius:8px; padding:16px 24px; box-shadow:0 1px 4px #0001; min-width:140px; }}
  .card .num {{ font-size:2em; font-weight:bold; }}
  .card.red .num {{ color:#ef4444; }}
  .card.yellow .num {{ color:#f59e0b; }}
  .card.green .num {{ color:#22c55e; }}
  .card .lbl {{ color:#666; font-size:12px; }}
  table {{ border-collapse:collapse; width:100%; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 4px #0001; }}
  th {{ background:#1a1a2e; color:#fff; padding:10px 14px; text-align:left; }}
  tr.err {{ background:#fff5f5; }}
  tr.warn {{ background:#fffbeb; }}
  tr:hover {{ filter:brightness(0.97); }}
  td {{ padding:8px 14px; border-bottom:1px solid #f0f0f0; vertical-align:top; }}
  td.lv {{ font-weight:bold; color:#6366f1; width:44px; }}
  td.kj {{ font-size:1.6em; width:48px; }}
  ul {{ margin:0; padding-left:16px; }}
  li {{ margin:2px 0; }}
  li.e {{ color:#dc2626; }}
  li.w {{ color:#92400e; }}
  input {{ padding:8px 12px; border:1px solid #ddd; border-radius:6px; width:260px; margin-bottom:16px; }}
  .filter-bar {{ display:flex; gap:10px; align-items:center; margin-bottom:12px; flex-wrap:wrap; }}
  button {{ padding:8px 14px; border-radius:6px; border:1px solid #ddd; cursor:pointer; background:#fff; }}
  button.active {{ background:#1a1a2e; color:#fff; border-color:#1a1a2e; }}
</style>
</head>
<body>
<h1>🔍 Koeru QA Report — Kanji Data</h1>
<div class="summary">
  <div class="card"><div class="num">{total}</div><div class="lbl">Tổng kanji</div></div>
  <div class="card red"><div class="num">{sum(1 for r in results if r["errors"])}</div><div class="lbl">Có lỗi ❌</div></div>
  <div class="card yellow"><div class="num">{sum(1 for r in results if r["warnings"] and not r["errors"])}</div><div class="lbl">Chỉ cảnh báo ⚠️</div></div>
  <div class="card green"><div class="num">{sum(1 for r in results if not r["errors"] and not r["warnings"])}</div><div class="lbl">Sạch ✅</div></div>
</div>
<div class="filter-bar">
  <input id="search" placeholder="Tìm kanji, lỗi..." oninput="filterRows()">
  <button class="active" onclick="setFilter('all',this)">Tất cả</button>
  <button onclick="setFilter('err',this)">Chỉ lỗi ❌</button>
  <button onclick="setFilter('warn',this)">Chỉ cảnh báo ⚠️</button>
</div>
<table id="tbl">
  <thead><tr><th>Level</th><th>Kanji</th><th>Vấn đề</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<script>
let activeFilter = 'all';
function setFilter(f, btn) {{
  activeFilter = f;
  document.querySelectorAll('.filter-bar button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterRows();
}}
function filterRows() {{
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('#tbl tbody tr').forEach(tr => {{
    const txt = tr.textContent.toLowerCase();
    const matchQ = !q || txt.includes(q);
    const matchF = activeFilter==='all' ||
                   (activeFilter==='err'  && tr.classList.contains('err')) ||
                   (activeFilter==='warn' && tr.classList.contains('warn'));
    tr.style.display = (matchQ && matchF) ? '' : 'none';
  }});
}}
</script>
</body></html>'''

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    errors = main()
    sys.exit(0 if errors == 0 else 1)
