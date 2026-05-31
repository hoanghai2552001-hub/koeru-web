"""
KOERU — JLPT Study HTML Generator
Tạo file HTML tự chứa (offline) cho từng cấp JLPT với:
  - Animated SVG stroke order (CSS draw animation, từng nét vẽ lần lượt)
  - Bảng kanji: Hán Việt, On/Kun, nghĩa, gợi nhớ, từ mẫu
  - Filter, search, replay animation
  - In được từ browser (Ctrl+P)
Usage:
  python tools/gen_study_html.py N5
  python tools/gen_study_html.py N5 N4 N3 N2 N1
"""

import sys, re, json, urllib.request, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT      = Path(__file__).parent.parent
JS_DIR    = ROOT / "js"
OUT_DIR   = ROOT / "output"
STUDY_DIR = ROOT / "study"       # deploy target
SVG_CACHE = OUT_DIR / "kanji_svg"
OUT_DIR.mkdir(exist_ok=True)
STUDY_DIR.mkdir(exist_ok=True)
SVG_CACHE.mkdir(exist_ok=True)

LEVELS = ["N5","N4","N3","N2","N1"]
LEVEL_COLOR = {
    "N5": "#22c55e", "N4": "#3b82f6",
    "N3": "#f59e0b", "N2": "#a855f7", "N1": "#ef4444",
}
KANJIVG = "https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{}.svg"


# ── Parse JS data ─────────────────────────────────────────────────────────────
def parse_level(level):
    fpath = JS_DIR / f"kanji-data-{level.lower()}.js"
    txt = fpath.read_text(encoding="utf-8")
    m = re.search(r'=\s*(\[[\s\S]*\])\s*;?\s*$', txt, re.MULTILINE)
    raw = m.group(1)
    raw = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)\s*:', r'\1"\2":', raw)
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    return json.loads(raw)


# ── Fetch & cache SVG ─────────────────────────────────────────────────────────
def fetch_svg(kanji):
    hex_c = f"{ord(kanji):05x}"
    cache = SVG_CACHE / f"{hex_c}.svg"
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    url = KANJIVG.format(hex_c)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            svg = r.read().decode("utf-8")
        cache.write_text(svg, encoding="utf-8")
        return svg
    except Exception as e:
        print(f"  ✗ {kanji}: {e}")
        return None


# ── Build inline animated SVG ─────────────────────────────────────────────────
def build_animated_svg(kanji, svg_raw, color="#6366f1", idx=0):
    """Return inline <svg> string with CSS draw-on animation."""
    try:
        root = ET.fromstring(svg_raw.split("?>")[-1].strip())
    except Exception:
        return f'<svg viewBox="0 0 109 109"><text x="10" y="80" font-size="80">{kanji}</text></svg>'

    # Collect only stroke paths (id ends with -sN)
    ns = "http://www.w3.org/2000/svg"
    paths = [p for p in root.findall(f".//{{{ns}}}path")
             if re.search(r"-s\d+$", p.get("id",""))]
    if not paths:
        paths = root.findall(f".//{{{ns}}}path")

    n = len(paths)
    uid = f"k{idx}"          # unique prefix per kanji

    # Build CSS keyframes per stroke
    css_lines = [f"""
      .{uid} .stroke {{ fill:none; stroke-linecap:round; stroke-linejoin:round; }}
      .{uid} .stroke-guide {{ stroke:rgba(200,200,200,0.5); stroke-width:3; }}
      .{uid} .stroke-done  {{ stroke:#334155; stroke-width:4; }}
      .{uid} .stroke-active{{ stroke:{color}; stroke-width:5; }}
      @keyframes {uid}-draw {{
        from {{ stroke-dashoffset: var(--len); }}
        to   {{ stroke-dashoffset: 0; }}
      }}"""]

    # Guide strokes (all paths, faded)
    guide_paths = ""
    for p in paths:
        d = p.get("d","")
        guide_paths += f'<path class="stroke stroke-guide" d="{d}"/>\n'

    # Animated strokes
    anim_paths = ""
    STEP = 0.45   # seconds per stroke
    HOLD = 1.2    # hold at end before loop

    for i, p in enumerate(paths):
        d = p.get("d","")
        delay     = i * STEP
        dur       = STEP * 0.85
        total_dur = n * STEP + HOLD
        # i < n-1 → done style after drawing; i == n-1 → stays active briefly then resets
        extra_css = ""
        if i < n-1:
            # after drawing, turn dark; use fill-mode forwards
            anim_paths += f"""<path class="stroke stroke-done" d="{d}"
  style="--len:1000;stroke-dasharray:1000;stroke-dashoffset:1000;
         animation:{uid}-draw {dur:.2f}s ease {delay:.2f}s forwards;"/>\n"""
        else:
            anim_paths += f"""<path class="stroke stroke-active" d="{d}"
  style="--len:1000;stroke-dasharray:1000;stroke-dashoffset:1000;
         animation:{uid}-draw {dur:.2f}s ease {delay:.2f}s forwards;"/>\n"""

    # Stroke number dots — small circles at start of each path
    # We skip this to keep SVG simple; JS will handle getTotalLength

    svg_out = f"""<svg class="{uid}" viewBox="0 0 109 109" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;height:100%;display:block;" data-strokes="{n}">
  <style>{chr(10).join(css_lines)}</style>
  <g class="guides">{guide_paths}</g>
  <g class="animated">{anim_paths}</g>
</svg>"""
    return svg_out


# ── HTML template ─────────────────────────────────────────────────────────────
PAGE_CSS = """
:root {
  --bg: #0f1117;
  --card: #1a1d2e;
  --border: rgba(255,255,255,0.07);
  --text: #e2e8f0;
  --sub: #94a3b8;
  --muted: #475569;
  font-size: 14px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Noto Sans JP', 'Segoe UI', system-ui, sans-serif;
  background: var(--bg); color: var(--text);
  min-height: 100vh;
}
/* ── Header ── */
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: rgba(15,17,23,0.92); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 12px 24px;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.site-header h1 { font-size: 1.1rem; font-weight: 700; }
.level-badge {
  padding: 3px 10px; border-radius: 20px;
  font-size: .75rem; font-weight: 700; letter-spacing: .5px;
}
.stats { font-size: .8rem; color: var(--sub); margin-left: auto; }
/* search */
#search {
  padding: 6px 12px; border-radius: 8px;
  background: rgba(255,255,255,.06); border: 1px solid var(--border);
  color: var(--text); font-size: .85rem; width: 180px;
  outline: none;
}
#search:focus { border-color: rgba(255,255,255,.2); }
/* replay btn */
.replay-btn {
  padding: 5px 14px; border-radius: 8px; border: 1px solid var(--border);
  background: rgba(255,255,255,.06); color: var(--sub);
  font-size: .8rem; cursor: pointer; transition: all .2s;
}
.replay-btn:hover { background: rgba(255,255,255,.12); color: var(--text); }

/* ── Grid ── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(660px, 1fr));
  gap: 1px;
  background: var(--border);
  border-top: 1px solid var(--border);
}
/* ── Kanji Card ── */
.kcard {
  background: var(--card);
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 0;
  transition: background .15s;
}
.kcard:hover { background: #1e2238; }
.kcard.hidden { display: none; }

/* Left: SVG panel */
.svg-panel {
  background: rgba(0,0,0,.25);
  border-right: 1px solid var(--border);
  padding: 12px;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  cursor: pointer;
  position: relative;
}
.svg-wrap {
  width: 120px; height: 120px;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}
/* replay hint */
.svg-panel::after {
  content: "▶ tap to replay";
  position: absolute; bottom: 6px;
  font-size: .6rem; color: var(--muted);
  letter-spacing: .3px;
}
.stroke-count {
  font-size: .7rem; color: var(--muted);
  letter-spacing: .3px;
}

/* Right: Info panel */
.info-panel {
  padding: 14px 16px;
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 8px;
}
/* Row 1: kanji char + hanviet + readings */
.row-top {
  display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
}
.kanji-char {
  font-size: 2.8rem; font-weight: 700; line-height: 1;
}
.hanviet {
  font-size: .75rem; font-weight: 700;
  letter-spacing: 1px; text-transform: uppercase;
  color: var(--sub); padding-top: 4px;
}
/* Readings */
.readings { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.read-tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 6px;
  font-size: .78rem;
}
.on-tag  { background: rgba(59,130,246,.12); color: #93c5fd; }
.kun-tag { background: rgba(20,184,166,.12); color: #5eead4; }
.read-label { font-size: .62rem; opacity: .6; font-weight: 600; }

/* Row 2: meaning */
.meaning-row { display: flex; align-items: baseline; gap: 8px; }
.meaning-vi {
  font-size: 1rem; font-weight: 600; color: var(--text);
}
.radical-tag {
  font-size: .7rem; color: var(--muted);
  padding: 1px 6px; border-radius: 4px;
  background: rgba(255,255,255,.04);
  border: 1px solid var(--border);
}

/* Row 3: mnemonic */
.mnemonic {
  font-size: .8rem; color: var(--sub); font-style: italic;
  line-height: 1.5;
  border-left: 2px solid var(--border);
  padding-left: 10px;
}

/* Row 4: words */
.words { display: flex; flex-wrap: wrap; gap: 6px; padding-top: 2px; }
.word-pill {
  display: inline-flex; flex-direction: column;
  padding: 4px 10px; border-radius: 8px;
  background: rgba(255,255,255,.04);
  border: 1px solid var(--border);
  font-size: .75rem; line-height: 1.4;
  min-width: 80px;
}
.word-jp  { font-weight: 700; color: var(--text); }
.word-read { font-size: .68rem; color: var(--muted); }
.word-vi  { font-size: .7rem; color: var(--sub); font-style: italic; }

/* ── Print ── */
@media print {
  body { background:#fff; color:#000; }
  .site-header { position:static; background:#fff; }
  .kcard { background:#fff; break-inside:avoid; border:1px solid #ddd; margin-bottom:4px; }
  .svg-panel { background:#f9f9f9; }
  .svg-panel::after { display:none; }
  .svg-wrap { border:1px solid #ddd; }
  /* freeze animation in last frame for print */
  .kcard svg * { animation-play-state: paused !important;
                 animation-delay: -9999s !important; }
}
@page { margin: 1cm; size: A4 landscape; }

/* ── Utility ── */
.no-result {
  grid-column: 1/-1; padding: 60px; text-align:center;
  color: var(--muted); font-size: 1rem;
}

/* ── Footer attribution ── */
.site-footer {
  border-top: 1px solid var(--border);
  padding: 20px 28px;
  display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start;
  background: rgba(0,0,0,.2);
}
.footer-title {
  font-size: .68rem; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: var(--muted);
  margin-bottom: 8px;
}
.attr-block {
  flex: 1; min-width: 220px;
  padding: 12px 16px; border-radius: 10px;
  background: rgba(255,255,255,.03);
  border: 1px solid var(--border);
}
.attr-name { font-size: .85rem; font-weight: 700; color: var(--text); }
.attr-desc { font-size: .75rem; color: var(--sub); margin: 3px 0 6px; line-height: 1.5; }
.attr-link { font-size: .72rem; color: #818cf8; text-decoration: none; }
.attr-link:hover { text-decoration: underline; }
.license-badge {
  display: inline-block; font-size: .62rem; font-weight: 700;
  padding: 2px 7px; border-radius: 4px;
  background: rgba(99,102,241,.15); color: #818cf8;
  border: 1px solid rgba(99,102,241,.3);
  margin-left: 6px; vertical-align: middle;
}
.footer-copy {
  width: 100%; font-size: .7rem; color: var(--muted);
  padding-top: 10px; border-top: 1px solid var(--border);
  margin-top: 4px;
}
@media print { .site-footer { display:none; } }
"""

PAGE_JS = """
// Replay animation by cloning SVG
document.querySelectorAll('.svg-panel').forEach(panel => {
  panel.addEventListener('click', () => {
    const wrap = panel.querySelector('.svg-wrap');
    const svg  = wrap.querySelector('svg');
    if (!svg) return;
    const clone = svg.cloneNode(true);
    wrap.replaceChild(clone, svg);
  });
});

// Search / filter
const searchEl = document.getElementById('search');
const cards    = document.querySelectorAll('.kcard');
const noResult = document.getElementById('no-result');

searchEl.addEventListener('input', () => {
  const q = searchEl.value.toLowerCase().trim();
  let shown = 0;
  cards.forEach(c => {
    const hit = !q || c.dataset.search.includes(q);
    c.classList.toggle('hidden', !hit);
    if (hit) shown++;
  });
  noResult.style.display = shown === 0 ? 'block' : 'none';
});

// Replay all
document.getElementById('replay-all').addEventListener('click', () => {
  document.querySelectorAll('.svg-wrap').forEach(wrap => {
    const svg = wrap.querySelector('svg');
    if (!svg) return;
    wrap.replaceChild(svg.cloneNode(true), svg);
  });
});

// Fix dashoffset with actual path lengths (runs once after load)
requestAnimationFrame(() => {
  document.querySelectorAll('.animated path').forEach(p => {
    try {
      const len = Math.ceil(p.getTotalLength()) + 10;
      p.style.setProperty('--len', len);
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = len;
    } catch(e) {}
  });
});
"""


def build_html(level, kanji_list, color):
    # Pre-fetch all SVGs
    print(f"  Fetching {len(kanji_list)} SVGs...")
    svgs = {}
    for i, entry in enumerate(kanji_list):
        k = entry["kanji"]
        svg = fetch_svg(k)
        svgs[k] = svg
        print(f"  {i+1}/{len(kanji_list)} {k}", end="\r", flush=True)
        if svg is None:
            time.sleep(0.1)
    print()

    # Build cards HTML
    cards_html = []
    for idx, entry in enumerate(kanji_list):
        k        = entry["kanji"]
        hanviet  = entry.get("hanviet", "")
        on_r     = entry.get("on", "")
        kun_r    = entry.get("kun", "")
        meaning  = entry.get("meaning", "")
        mnemonic = entry.get("mn_vi", entry.get("mnemonic", ""))
        strokes  = entry.get("stroke", "?")
        radical  = entry.get("radical", "").split("|")[0]
        words    = entry.get("words", [])[:5]

        svg_raw = svgs.get(k)
        svg_tag = build_animated_svg(k, svg_raw, color=color, idx=idx) if svg_raw else \
                  f'<svg viewBox="0 0 109 109"><text x="10" y="90" font-size="90" fill="#334155">{k}</text></svg>'

        # Search index
        search_str = " ".join([
            k, hanviet.lower(), meaning.lower(), on_r.lower(), kun_r.lower(),
            " ".join(w.get("w","") for w in words),
            " ".join(w.get("m","") for w in words),
        ])

        # Words pills
        words_html = ""
        for w in words:
            words_html += f"""<span class="word-pill">
  <span class="word-jp">{w.get('w','')}</span>
  <span class="word-read">{w.get('r','')}</span>
  <span class="word-vi">{w.get('m','')}</span>
</span>"""

        cards_html.append(f"""<div class="kcard" data-search="{search_str}">
  <div class="svg-panel" title="Tap to replay stroke order">
    <div class="svg-wrap">{svg_tag}</div>
    <span class="stroke-count">{strokes} nét</span>
  </div>
  <div class="info-panel">
    <div class="row-top">
      <span class="kanji-char" style="color:{color}">{k}</span>
      <span class="hanviet">{hanviet}</span>
      <div class="readings">
        <span class="read-tag on-tag"><span class="read-label">On</span>{on_r or "—"}</span>
        <span class="read-tag kun-tag"><span class="read-label">Kun</span>{kun_r or "—"}</span>
      </div>
    </div>
    <div class="meaning-row">
      <span class="meaning-vi">{meaning}</span>
      {"<span class='radical-tag'>"+radical+"</span>" if radical else ""}
    </div>
    {"<div class='mnemonic'>"+mnemonic+"</div>" if mnemonic else ""}
    <div class="words">{words_html}</div>
  </div>
</div>""")

    cards_joined = "\n".join(cards_html)
    total_words  = sum(len(e.get("words", [])) for e in kanji_list)

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KOERU JLPT {level} — Bảng Kanji Hoạt Họa</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">
<style>
{PAGE_CSS}
.level-badge {{ background:{color}22; color:{color}; border:1px solid {color}44; }}
.kanji-char {{ font-family:'Noto Sans JP',sans-serif; }}
</style>
</head>
<body>

<header class="site-header">
  <h1>KOERU</h1>
  <span class="level-badge">JLPT {level}</span>
  <span style="font-size:.85rem;color:var(--sub)">Bảng Kanji Hoạt Họa</span>
  <span class="stats">{len(kanji_list)} kanji · ~{total_words} từ</span>
  <input id="search" type="search" placeholder="Tìm kanji, nghĩa, từ…" autocomplete="off">
  <button class="replay-btn" id="replay-all">↺ Replay tất cả</button>
  <button class="replay-btn" onclick="window.print()">🖨 In / PDF</button>
</header>

<main>
  <div class="grid" id="grid">
{cards_joined}
    <div id="no-result" class="no-result" style="display:none">Không tìm thấy kết quả</div>
  </div>
</main>

<footer class="site-footer">
  <div style="width:100%"><div class="footer-title">Nguồn dữ liệu &amp; Bản quyền</div></div>

  <div class="attr-block">
    <div class="attr-name">KanjiVG <span class="license-badge">CC BY-SA 3.0</span></div>
    <div class="attr-desc">
      Dữ liệu thứ tự nét (stroke order) và hình ảnh SVG của từng chữ Kanji.<br>
      © Ulrich Apel
    </div>
    <a class="attr-link" href="https://kanjivg.tagaini.net" target="_blank" rel="noopener">
      🔗 kanjivg.tagaini.net
    </a>
    &nbsp;·&nbsp;
    <a class="attr-link" href="https://github.com/KanjiVG/kanjivg" target="_blank" rel="noopener">
      GitHub: KanjiVG/kanjivg
    </a>
  </div>

  <div class="attr-block">
    <div class="attr-name">the-kanji-map <span class="license-badge">CC BY-SA 3.0</span></div>
    <div class="attr-desc">
      Dữ liệu bộ thủ (radical), thành phần chữ (parts) và câu gợi nhớ (mnemonic).
    </div>
    <a class="attr-link" href="https://github.com/thekanjimap/the-kanji-map" target="_blank" rel="noopener">
      GitHub: thekanjimap/the-kanji-map
    </a>
  </div>

  <div class="attr-block">
    <div class="attr-name">KOERU Japanese</div>
    <div class="attr-desc">
      Biên soạn nội dung tiếng Việt: nghĩa, Hán Việt, gợi nhớ tiếng Việt, từ mẫu.<br>
      Tổng hợp và trình bày bởi đội ngũ KOERU.
    </div>
    <a class="attr-link" href="https://hoanghai2552001-hub.github.io/koeru-web/" target="_blank" rel="noopener">
      🔗 koeruapp.com
    </a>
  </div>

  <div class="footer-copy">
    Stroke order SVG data © KanjiVG (Ulrich Apel), licensed under
    <a class="attr-link" href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener">CC BY-SA 3.0</a>.
    Việc sử dụng lại yêu cầu ghi nguồn và giữ nguyên giấy phép.
    File này được tạo tự động bởi KOERU — không dùng cho mục đích thương mại khi chưa có sự đồng ý.
  </div>
</footer>

<script>
{PAGE_JS}
</script>
</body>
</html>"""
    return html


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    targets = [a.upper() for a in sys.argv[1:] if a.upper() in LEVELS] or ["N5"]
    for level in targets:
        print(f"\n{'='*55}")
        print(f"  KOERU JLPT {level} HTML")
        print(f"{'='*55}")
        t0 = time.time()
        data  = parse_level(level)
        color = LEVEL_COLOR[level]
        html  = build_html(level, data, color)
        # Write to output/ (backup) và study/ (deploy)
        out_bak  = OUT_DIR   / f"KOERU_JLPT_{level}.html"
        out_web  = STUDY_DIR / f"{level.lower()}.html"
        out_bak.write_text(html, encoding="utf-8")
        out_web.write_text(html, encoding="utf-8")
        kb = out_bak.stat().st_size // 1024
        print(f"  ✅ study/{level.lower()}.html  ({kb} KB)  [{time.time()-t0:.1f}s]")
    print(f"\nDone! Deploy tại: study/")
    print("Mở file HTML trong Chrome/Edge để xem animation.")

if __name__ == "__main__":
    main()
