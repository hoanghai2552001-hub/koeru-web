// ══════════════════════════════════════════
// ══ STROKE ORDER ANIMATION (animCJK) ══
// ══════════════════════════════════════════
// Source: animCJK (Arphic Public License)
// CDN: cdn.jsdelivr.net/gh/parsimonhi/animCJK

const ANIMCJK_BASE = 'https://cdn.jsdelivr.net/gh/parsimonhi/animCJK@master/svgsJa/';
let _strokeSvgCache = {}; // cache để không fetch lại

function showStrokeOrder(kanji) {
  if (!kanji || !kanji.trim()) return;
  const char = kanji.trim()[0]; // chỉ lấy ký tự đầu
  const cp   = char.codePointAt(0).toString(16).toLowerCase().padStart(5, '0');
  const url  = ANIMCJK_BASE + cp + '.svg';

  const overlay   = document.getElementById('stroke-overlay');
  const container = document.getElementById('stroke-svg-wrap');
  const title     = document.getElementById('stroke-kanji-title');
  if (!overlay || !container) return;

  title.textContent = char;
  container.innerHTML = '<div class="stroke-loading">⏳ Đang tải nét vẽ…</div>';
  overlay.classList.add('visible');

  // Dùng cache nếu đã fetch rồi
  if (_strokeSvgCache[cp]) {
    _injectStrokeSvg(container, _strokeSvgCache[cp]);
    return;
  }

  fetch(url)
    .then(r => {
      if (!r.ok) throw new Error('not_found');
      return r.text();
    })
    .then(svg => {
      _strokeSvgCache[cp] = svg;
      _injectStrokeSvg(container, svg);
    })
    .catch(() => {
      container.innerHTML =
        '<div class="stroke-not-found">Chưa có dữ liệu nét vẽ cho kanji này</div>';
    });
}

function _injectStrokeSvg(container, svgText) {
  container.innerHTML = svgText;
  const svgEl = container.querySelector('svg');
  if (svgEl) {
    // Xoá width/height cứng, cho CSS điều khiển kích thước
    svgEl.removeAttribute('width');
    svgEl.removeAttribute('height');
    svgEl.style.cssText =
      'width:100%;max-width:240px;height:auto;display:block;margin:0 auto;';
  }
  // Lưu lại để replay
  container.dataset.lastSvg = svgText;
  container.dataset.lastCp  = container.dataset.lastCp || '';
}

function replayStrokeOrder() {
  const container = document.getElementById('stroke-svg-wrap');
  if (!container || !container.dataset.lastSvg) return;
  // Re-inject SVG → animations restart
  _injectStrokeSvg(container, container.dataset.lastSvg);
}

function closeStrokeOverlay() {
  const overlay = document.getElementById('stroke-overlay');
  if (overlay) overlay.classList.remove('visible');
}

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('stroke-overlay');
  if (!overlay) return;

  // Đóng khi click vùng tối bên ngoài modal
  overlay.addEventListener('click', e => {
    if (e.target === overlay) closeStrokeOverlay();
  });

  // Đóng bằng Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay.classList.contains('visible')) {
      closeStrokeOverlay();
    }
  });
});
