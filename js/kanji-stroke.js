// ══════════════════════════════════════════
// ══ STROKE ORDER (KanjiVG + JS animation) ══
// ══════════════════════════════════════════
// Data: KanjiVG (CC BY-SA 3.0)
// CDN: cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/

const _KANJIVG = 'https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/';
let _strokeCache = {};

async function showStrokeOrder(kanji) {
  if (!kanji || !kanji.trim()) return;
  const char = kanji.trim()[0];
  const cp   = char.codePointAt(0).toString(16).toLowerCase().padStart(5, '0');

  const overlay   = document.getElementById('stroke-overlay');
  const container = document.getElementById('stroke-svg-wrap');
  const title     = document.getElementById('stroke-kanji-title');
  if (!overlay || !container) return;

  title.textContent = char;
  container.innerHTML = '<div class="stroke-loading">⏳ Đang tải nét vẽ…</div>';
  overlay.classList.add('visible');

  let svgText = _strokeCache[cp];
  if (!svgText) {
    try {
      const r = await fetch(_KANJIVG + cp + '.svg');
      if (!r.ok) throw new Error();
      svgText = await r.text();
      _strokeCache[cp] = svgText;
    } catch(_) {
      container.innerHTML = '<div class="stroke-not-found">Chưa có dữ liệu nét vẽ cho kanji này</div>';
      return;
    }
  }
  _buildAndPlay(container, svgText);
}

function _buildAndPlay(container, svgText) {
  const NS  = 'http://www.w3.org/2000/svg';
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml');
  const paths = Array.from(doc.querySelectorAll('path'))
    .map(p => p.getAttribute('d')).filter(Boolean);

  if (!paths.length) {
    container.innerHTML = '<div class="stroke-not-found">Chưa có dữ liệu</div>';
    return;
  }

  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 109 109');
  svg.style.cssText = 'width:100%;max-width:220px;height:auto;display:block;margin:0 auto;';

  paths.forEach(d => {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', d);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', '#c4b5fd');
    p.setAttribute('stroke-width', '3.5');
    p.setAttribute('stroke-linecap', 'round');
    p.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(p);
  });

  container.innerHTML = '';
  container.appendChild(svg);
  container._kanjivgPaths = paths;
  _playAnim(svg);
}

function _playAnim(svg) {
  const els = Array.from(svg.querySelectorAll('path'));
  els.forEach(p => {
    const len = p.getTotalLength() || 100;
    p.style.transition = 'none';
    p.style.strokeDasharray  = len;
    p.style.strokeDashoffset = len;
    p.style.stroke = 'rgba(196,181,253,.12)';
  });
  let delay = 0;
  els.forEach(p => {
    const len = p.getTotalLength() || 100;
    const dur = Math.min(Math.max(len * 4, 250), 900);
    setTimeout(() => {
      p.style.stroke = '#c4b5fd';
      p.style.transition = `stroke-dashoffset ${dur}ms ease, stroke 80ms`;
      p.style.strokeDashoffset = '0';
    }, delay);
    delay += dur + 80;
  });
}

function replayStrokeOrder() {
  const container = document.getElementById('stroke-svg-wrap');
  const svg = container?.querySelector('svg');
  if (svg) _playAnim(svg);
}

function closeStrokeOverlay() {
  document.getElementById('stroke-overlay')?.classList.remove('visible');
}

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('stroke-overlay');
  if (!overlay) return;
  overlay.addEventListener('click', e => { if (e.target === overlay) closeStrokeOverlay(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay.classList.contains('visible')) closeStrokeOverlay();
  });
});
