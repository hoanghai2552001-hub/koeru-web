/* ════════════════════════════════
   KANA SPEED — Write Mode
   Stroke order animation + writing guide
════════════════════════════════ */

let writeIdx    = 0;
let writeScript = 'hiragana';

const WRITE_LISTS = { hiragana: HIRAGANA_BASIC, katakana: KATAKANA_BASIC };
const GIF_PREFIX  = { hiragana: 'Hiragana',     katakana: 'Katakana' };

function getWriteList() { return WRITE_LISTS[writeScript]; }

function openWriteMode() {
  writeScript = 'hiragana';
  writeIdx    = 0;
  document.getElementById('wtab-hira').classList.add('active');
  document.getElementById('wtab-kata').classList.remove('active');
  buildWriteGrid();
  switchWriteTab('grid');
  showScreen('write-screen');
}

function switchWriteScript(script) {
  writeScript = script;
  writeIdx    = 0;
  document.getElementById('wtab-hira').classList.toggle('active', script === 'hiragana');
  document.getElementById('wtab-kata').classList.toggle('active', script === 'katakana');
  buildWriteGrid();
  switchWriteTab('grid');
}

function buildWriteGrid() {
  document.getElementById('write-grid-wrap').innerHTML =
    getWriteList().map((x, i) =>
      `<button class="wg-btn" id="wg-${i}" onclick="openWriteChar(${i})">${x.k}<span>${x.r}</span></button>`
    ).join('');
}

function openWriteChar(idx) {
  writeIdx = idx;
  switchWriteTab('view');
  renderWriteViewer();
}

function renderWriteViewer() {
  const list   = getWriteList();
  const item   = list[writeIdx];
  const prefix = GIF_PREFIX[writeScript];
  const ts     = Date.now();

  // Stroke order animation (trái)
  const gif = document.getElementById('write-gif');
  gif.src = '';
  gif.src = `images/stroke/${prefix}_${item.k}_stroke_order_animation.gif?t=${ts}`;

  // Writing guide (phải)
  const guideWrap = document.getElementById('write-guide-wrap');
  const guide     = document.getElementById('write-guide-gif');
  guide.src = '';
  guide.src = `images/stroke-guide/${writeScript}/${encodeURIComponent(item.k)}.gif?t=${ts}`;
  guide.onerror = () => { guideWrap.classList.add('no-guide');    guide.style.display = 'none'; };
  guide.onload  = () => { guideWrap.classList.remove('no-guide'); guide.style.display = 'block'; };

  document.getElementById('write-char-kana').textContent = item.k;
  document.getElementById('write-romaji').textContent    = item.r;
  document.getElementById('write-pos').textContent       = `${writeIdx + 1} / ${list.length}`;
  document.getElementById('prev-btn').disabled = writeIdx === 0;
  document.getElementById('next-btn').disabled = writeIdx === list.length - 1;
  document.querySelectorAll('.wg-btn').forEach((b, i) => b.classList.toggle('active', i === writeIdx));

  if (audioEnabled) playKanaAudio(item.k);
}

function replayGif() {
  const item   = getWriteList()[writeIdx];
  const prefix = GIF_PREFIX[writeScript];
  const ts     = Date.now();
  const gif    = document.getElementById('write-gif');
  gif.src = '';
  gif.src = `images/stroke/${prefix}_${item.k}_stroke_order_animation.gif?t=${ts}`;
  const guide  = document.getElementById('write-guide-gif');
  guide.src = guide.src.split('?')[0] + `?t=${ts}`;
}

function writeNav(dir) {
  const next = writeIdx + dir;
  if (next < 0 || next >= getWriteList().length) return;
  writeIdx = next;
  renderWriteViewer();
}

function switchWriteTab(tab) {
  document.getElementById('write-grid-wrap').style.display = tab === 'grid' ? 'grid' : 'none';
  document.getElementById('write-viewer').style.display    = tab === 'view' ? 'flex'  : 'none';
  document.getElementById('wtab-grid').classList.toggle('active', tab === 'grid');
  document.getElementById('wtab-view').classList.toggle('active', tab === 'view');
}
