// ══════════════════════════════════════════
// KOERU · Học Kanji — kanji-study.js
// ══════════════════════════════════════════
// Dữ liệu: ALL_KANJI lazy-load theo level (kanji-data-n5.js…)
// Stroke order: KanjiVG (CC BY-SA 3.0)
//   via cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/

const KANJIVG_CDN = 'https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/';

// ── State ──────────────────────────────────
let currentLevel  = 'N5';
let currentSearch = '';
let currentKanji  = null;
let svgCache      = {};
let masteryStore  = null;

// ── Lazy-load data theo level ───────────────
const _loadedLevels = new Set();
const _loadCallbacks = {};

function ensureLevelLoaded(level, cb) {
  if (level === 'ALL') {
    // ALL cần tất cả levels
    const all = ['N5','N4','N3','N2','N1'];
    let pending = all.filter(lv => !_loadedLevels.has(lv));
    if (!pending.length) { cb(); return; }
    let done = 0;
    pending.forEach(lv => ensureLevelLoaded(lv, () => { if(++done === pending.length) cb(); }));
    return;
  }
  if (_loadedLevels.has(level)) { cb(); return; }
  if (_loadCallbacks[level]) { _loadCallbacks[level].push(cb); return; }
  _loadCallbacks[level] = [cb];
  const s = document.createElement('script');
  s.src = `js/kanji-data-${level.toLowerCase()}.js?v=20260527d`;
  s.onload = () => {
    // Merge window.KANJI_Nx vào ALL_KANJI
    const key = `KANJI_${level}`;
    if (window[key]) {
      window[key].forEach(k => { if (!ALL_KANJI.find(x => x.kanji === k.kanji)) ALL_KANJI.push(k); });
    }
    _loadedLevels.add(level);
    (_loadCallbacks[level] || []).forEach(fn => fn());
    delete _loadCallbacks[level];
  };
  document.head.appendChild(s);
}

// ── Mastery (từ koeru-mastery.js nếu đã load) ──
function getStatus(kanji) {
  if (!masteryStore) return '';
  const data = masteryStore.get ? masteryStore.get(kanji) : null;
  if (!data) return '';
  if (data.box >= 4)  return 'learned';
  if (data.seen > 0)  return 'seen';
  return '';
}

// ── Filtering ──────────────────────────────
function getFilteredKanji() {
  let list = ALL_KANJI;
  if (currentLevel !== 'ALL') {
    list = list.filter(k => k.level === currentLevel);
  }
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    list = list.filter(k =>
      k.kanji.includes(q) ||
      (k.hanviet  || '').toLowerCase().includes(q) ||
      (k.meaning  || '').toLowerCase().includes(q) ||
      (k.on       || '').toLowerCase().includes(q) ||
      (k.kun      || '').toLowerCase().includes(q)
    );
  }
  return list;
}

// ── Render grid (progressive — 150 cells đầu, load thêm khi scroll) ──
const BATCH = 150;
let _currentList = [];
let _rendered = 0;
let _scrollObserver = null;

function makeCell(k, i) {
  const cell = document.createElement('div');
  const status = getStatus(k.kanji);
  cell.className = 'k-cell' + (status ? ' ' + status : '');
  cell.style.animationDelay = Math.min(i * 8, 200) + 'ms';
  cell.dataset.kanji = k.kanji;
  cell.innerHTML = `
    <span class="k-dot"></span>
    <span class="k-char">${k.kanji}</span>
    <span class="k-hv">${k.hanviet || ''}</span>
    <span class="k-mean">${(k.meaning || '').split(';')[0].trim()}</span>
    <span class="k-level lv-${k.level}">${k.level}</span>`;
  cell.addEventListener('click', () => openDetail(k, cell));
  return cell;
}

function renderBatch(grid, from, to) {
  const frag = document.createDocumentFragment();
  for (let i = from; i < Math.min(to, _currentList.length); i++) {
    frag.appendChild(makeCell(_currentList[i], i));
  }
  // Xóa sentinel cũ nếu có
  const old = grid.querySelector('.grid-sentinel');
  if (old) old.remove();
  grid.appendChild(frag);
  _rendered = Math.min(to, _currentList.length);
  // Thêm sentinel nếu còn data
  if (_rendered < _currentList.length) {
    const sentinel = document.createElement('div');
    sentinel.className = 'grid-sentinel';
    sentinel.style.cssText = 'height:1px;width:100%;grid-column:1/-1;';
    grid.appendChild(sentinel);
    if (_scrollObserver) _scrollObserver.observe(sentinel);
  }
}

function renderGrid() {
  const list  = getFilteredKanji();
  const grid  = document.getElementById('kanji-grid');
  const empty = document.getElementById('study-empty');
  const count = document.getElementById('study-stats-count');

  count.textContent = list.length + ' kanji';

  if (list.length === 0) {
    grid.innerHTML = '';
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  _currentList = list;
  _rendered = 0;
  grid.innerHTML = '';

  // Setup IntersectionObserver để load thêm khi scroll tới đáy
  if (_scrollObserver) _scrollObserver.disconnect();
  _scrollObserver = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && _rendered < _currentList.length) {
      renderBatch(grid, _rendered, _rendered + BATCH);
    }
  }, { rootMargin: '200px' });

  renderBatch(grid, 0, BATCH);
}

// ── Detail panel ────────────────────────────
function openDetail(k, cellEl) {
  currentKanji = k;

  // Highlight cell
  document.querySelectorAll('.k-cell.selected').forEach(c => c.classList.remove('selected'));
  if (cellEl) cellEl.classList.add('selected');

  // Show content, hide placeholder
  const placeholder = document.getElementById('detail-placeholder');
  const content     = document.getElementById('detail-content');
  if (placeholder) placeholder.style.display = 'none';
  if (content)     content.style.display     = '';

  // Fill data
  document.getElementById('detail-kanji-big').textContent = k.kanji;
  document.getElementById('detail-hanviet').textContent   = (k.hanviet || '').toUpperCase();
  document.getElementById('detail-meaning').textContent   = k.meaning || '';

  // Readings
  document.getElementById('detail-on').textContent  = k.on  || '—';
  document.getElementById('detail-kun').textContent = k.kun || '—';

  // Badges
  const badges = document.getElementById('detail-badges');
  badges.innerHTML = `<span class="detail-badge lv-${k.level}">${k.level}</span>`;
  if (k.stroke)    badges.innerHTML += `<span class="detail-badge">${k.stroke} nét</span>`;
  if (k.freq_rank) badges.innerHTML += `<span class="detail-badge freq">Top ${k.freq_rank}</span>`;
  if (k.grade)     badges.innerHTML += `<span class="detail-badge grade">Lớp ${k.grade}</span>`;

  // Radical & Components
  const radWrap = document.getElementById('detail-radical');
  if (radWrap) {
    if (k.radical) {
      const segs = k.radical.split('|');
      const rc = segs[0], rn = segs[1], rm = segs[2], rv = segs[3];
      const radLabel = rv ? `${rv} (${rm})` : rm;
      radWrap.innerHTML = `<span class="rad-char">${rc}</span><span class="rad-info">${rn} · ${radLabel}</span>`;
      radWrap.style.display = '';
    } else {
      radWrap.style.display = 'none';
    }
  }

  const partsWrap = document.getElementById('detail-parts');
  if (partsWrap) {
    if (k.parts && k.parts.length) {
      partsWrap.innerHTML = k.parts.map(p => `<span class="part-char">${p}</span>`).join('');
      partsWrap.style.display = '';
    } else {
      partsWrap.style.display = 'none';
    }
  }

  // Mnemonic — ưu tiên bản tiếng Việt nếu có
  const mnWrap = document.getElementById('detail-mnemonic');
  if (mnWrap) {
    const mnText = k.mn_vi || k.mnemonic || '';
    if (mnText) {
      mnWrap.textContent = mnText;
      mnWrap.parentElement.style.display = '';
    } else {
      mnWrap.parentElement.style.display = 'none';
    }
  }

  // Stroke order
  loadStrokeOrder(k.kanji);

  // Vocabulary
  renderVocab(k);

  // Open panel
  const panel = document.getElementById('detail-panel');
  const backdrop = document.getElementById('detail-backdrop');
  panel.classList.add('open');
  backdrop.classList.add('show');

  // Scroll to top of panel
  panel.scrollTop = 0;
}

function closeDetail() {
  document.getElementById('detail-panel').classList.remove('open');
  document.getElementById('detail-backdrop').classList.remove('show');
  document.querySelectorAll('.k-cell.selected').forEach(c => c.classList.remove('selected'));
  currentKanji = null;
}

// ── Stroke order (KanjiVG + JS animation) ───
async function loadStrokeOrder(kanji) {
  const container = document.getElementById('detail-stroke-svg');
  const cp = kanji.codePointAt(0).toString(16).toLowerCase().padStart(5, '0');

  const k = ALL_KANJI.find(x => x.kanji === kanji);
  document.getElementById('detail-stroke-count').textContent =
    k && k.stroke ? `${k.stroke} nét vẽ` : 'Thứ tự nét vẽ';

  container.innerHTML = '<span class="stroke-load-msg">⏳</span>';

  // dùng cache nếu đã fetch
  let svgText = svgCache[cp];
  if (!svgText) {
    try {
      const r = await fetch(KANJIVG_CDN + cp + '.svg');
      if (!r.ok) throw new Error();
      svgText = await r.text();
      svgCache[cp] = svgText;
    } catch(_) {
      container.innerHTML = '<span class="stroke-load-msg">Chưa có dữ liệu</span>';
      return;
    }
  }
  buildStrokeSvg(container, svgText);
}

function buildStrokeSvg(container, svgText) {
  const NS = 'http://www.w3.org/2000/svg';
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml');
  const paths = Array.from(doc.querySelectorAll('path'))
    .map(p => p.getAttribute('d')).filter(Boolean);

  if (!paths.length) {
    container.innerHTML = '<span class="stroke-load-msg">Chưa có dữ liệu</span>';
    return;
  }

  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 109 109');
  svg.style.cssText = 'width:86px;height:86px;display:block;';

  paths.forEach(d => {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', d);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', '#a5b4fc');
    p.setAttribute('stroke-width', '3.5');
    p.setAttribute('stroke-linecap', 'round');
    p.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(p);
  });

  container.innerHTML = '';
  container.appendChild(svg);
  playStrokeAnim(svg);
}

function playStrokeAnim(svg) {
  const pathEls = Array.from(svg.querySelectorAll('path'));
  // reset
  pathEls.forEach(p => {
    const len = p.getTotalLength() || 100;
    p.style.transition = 'none';
    p.style.strokeDasharray = len;
    p.style.strokeDashoffset = len;
    p.style.stroke = 'rgba(165,180,252,.15)';
  });

  let delay = 0;
  pathEls.forEach(p => {
    const len = p.getTotalLength() || 100;
    const dur  = Math.min(Math.max(len * 4, 250), 900); // 250–900ms per stroke
    setTimeout(() => {
      p.style.stroke = '#a5b4fc';
      p.style.transition = `stroke-dashoffset ${dur}ms ease, stroke 80ms`;
      p.style.strokeDashoffset = '0';
    }, delay);
    delay += dur + 80;
  });
}

function replayStroke() {
  const container = document.getElementById('detail-stroke-svg');
  const svg = container.querySelector('svg');
  if (svg) playStrokeAnim(svg);
}

// ── Vocabulary ──────────────────────────────
function renderVocab(k) {
  const list = document.getElementById('detail-vocab-list');
  const words = k.words || [];
  if (!words.length) {
    list.innerHTML = '<p style="font-size:.78rem;color:var(--muted)">Chưa có từ vựng mẫu.</p>';
    return;
  }
  list.innerHTML = words.slice(0, 8).map(w => `
    <div class="vocab-item">
      <span class="vocab-w">${w.w || ''}</span>
      <span class="vocab-r">${w.r || ''}</span>
      <span class="vocab-m">${w.m || ''}</span>
    </div>`).join('');
}

// ── Init & event binding ────────────────────
document.addEventListener('DOMContentLoaded', () => {
  masteryStore = window.koeruMastery || null;
  // N5 đã được load từ HTML — đánh dấu sẵn
  _loadedLevels.add('N5');
  // Preload N4 ngầm sau 2s khi browser rảnh
  setTimeout(() => ensureLevelLoaded('N4', () => {}), 2000);

  // Level tabs
  document.querySelectorAll('.lvl-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.lvl-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentLevel = tab.dataset.lvl;
      currentSearch = '';
      document.getElementById('study-search').value = '';
      document.getElementById('study-search-clear').style.display = 'none';
      closeDetail();
      // Hiện loading indicator nhẹ
      const count = document.getElementById('study-stats-count');
      count.textContent = 'Đang tải…';
      ensureLevelLoaded(currentLevel, renderGrid);
    });
  });

  // Search
  const searchInput = document.getElementById('study-search');
  const clearBtn    = document.getElementById('study-search-clear');
  searchInput.addEventListener('input', () => {
    currentSearch = searchInput.value.trim();
    clearBtn.style.display = currentSearch ? 'block' : 'none';
    renderGrid();
  });
  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    currentSearch = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
    renderGrid();
  });

  // Close detail
  document.getElementById('detail-backdrop').addEventListener('click', closeDetail);
  document.getElementById('detail-close')?.addEventListener('click', closeDetail);

  // Replay stroke
  document.getElementById('btn-replay-stroke').addEventListener('click', replayStroke);

  // Go to games button (header)
  document.getElementById('study-goto-game').addEventListener('click', () => {
    window.location.href = 'kanji.html';
  });

  // "Luyện ngay" in detail panel → mở kanji.html với level tương ứng
  document.getElementById('detail-go-game').addEventListener('click', () => {
    if (currentKanji) {
      localStorage.setItem('koeru_study_launch_level', currentKanji.level);
    }
    window.location.href = 'kanji.html';
  });

  // Nút "Vào Kanji Map"
  document.getElementById('detail-go-map')?.addEventListener('click', () => {
    window.location.href = 'kanji-map.html';
  });

  // Keyboard: Escape đóng panel, ←→ điều hướng kanji
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { closeDetail(); return; }
    if (!currentKanji) return;
    const list = getFilteredKanji();
    const idx  = list.findIndex(k => k.kanji === currentKanji.kanji);
    if (e.key === 'ArrowRight' && idx < list.length - 1) {
      openDetail(list[idx + 1]);
    }
    if (e.key === 'ArrowLeft' && idx > 0) {
      openDetail(list[idx - 1]);
    }
  });

  // Initial render
  renderGrid();

  // Nếu kanji.html đã set level gần nhất → áp dụng
  const savedLevel = localStorage.getItem('koeru_study_launch_level');
  if (savedLevel && ['N5','N4','N3','N2','N1'].includes(savedLevel)) {
    const tab = document.querySelector(`.lvl-tab[data-lvl="${savedLevel}"]`);
    if (tab) tab.click();
  }
});
