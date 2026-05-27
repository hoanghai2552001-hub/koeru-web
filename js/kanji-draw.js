// ══════════════════════════════════════════
// ══ GAME 5: VẼ KANJI ══
// ══════════════════════════════════════════
// Nhận dạng chữ viết tay qua handwriting.js (MIT)
// https://github.com/ChenYuHo/handwriting.js

let drawDeck       = [];
let drawIdx        = 0;
let drawCorrect    = 0;
let drawTotal      = 0;
let drawCurrentK   = null;   // kanji object hiện tại
let drawStrokes    = [];     // tất cả nét đã vẽ
let drawCurStroke  = [];     // nét đang vẽ
let drawIsDrawing  = false;
let drawAutoTimer  = null;
let drawCanvas, drawCtx;
let drawWaitingResult = false; // đang chờ API trả về

// ── Canvas init ─────────────────────────────────────
function initDrawCanvas() {
  drawCanvas = document.getElementById('draw-canvas');
  if (!drawCanvas) return;
  drawCtx = drawCanvas.getContext('2d');
  resizeDrawCanvas();

  // Pointer API (chuột + bút stylus + ngón tay — dùng 1 set event)
  drawCanvas.addEventListener('pointerdown', onDrawDown);
  drawCanvas.addEventListener('pointermove', onDrawMove);
  drawCanvas.addEventListener('pointerup',   onDrawUp);
  drawCanvas.addEventListener('pointerleave',onDrawUp);
  drawCanvas.addEventListener('pointercancel',onDrawUp);
  // Prevent touch scroll khi vẽ
  drawCanvas.addEventListener('touchstart', e => e.preventDefault(), { passive:false });
  drawCanvas.addEventListener('touchmove',  e => e.preventDefault(), { passive:false });

  window.addEventListener('resize', resizeDrawCanvas);
}

function resizeDrawCanvas() {
  if (!drawCanvas) return;
  const wrap = document.getElementById('draw-canvas-wrap');
  if (!wrap) return;
  const size = Math.min(wrap.clientWidth - 2, 320);
  drawCanvas.width  = size;
  drawCanvas.height = size;
  redrawCanvas();
}

function getDrawPos(e) {
  const rect = drawCanvas.getBoundingClientRect();
  const sx   = drawCanvas.width  / rect.width;
  const sy   = drawCanvas.height / rect.height;
  return {
    x: Math.round((e.clientX - rect.left) * sx),
    y: Math.round((e.clientY - rect.top)  * sy)
  };
}

function onDrawDown(e) {
  e.preventDefault();
  if (drawWaitingResult) return;
  clearDrawAutoTimer();
  drawIsDrawing = true;
  const p = getDrawPos(e);
  drawCurStroke = [p];
  drawCtx.beginPath();
  drawCtx.moveTo(p.x, p.y);
  applyBrush();
}

function onDrawMove(e) {
  if (!drawIsDrawing) return;
  e.preventDefault();
  const p = getDrawPos(e);
  drawCurStroke.push(p);
  drawCtx.lineTo(p.x, p.y);
  drawCtx.stroke();
}

function onDrawUp(e) {
  if (!drawIsDrawing) return;
  drawIsDrawing = false;
  if (drawCurStroke.length > 1) {
    drawStrokes.push([...drawCurStroke]);
    drawCurStroke = [];
    // Tự động nhận dạng sau 1.5s dừng vẽ
    clearDrawAutoTimer();
    drawAutoTimer = setTimeout(recognizeDrawing, 1500);
  }
}

function applyBrush() {
  drawCtx.strokeStyle = '#ffffff';
  drawCtx.lineWidth   = Math.max(Math.round(drawCanvas.width / 36), 7);
  drawCtx.lineCap     = 'round';
  drawCtx.lineJoin    = 'round';
}

function redrawCanvas() {
  if (!drawCtx) return;
  const w = drawCanvas.width, h = drawCanvas.height;
  drawCtx.clearRect(0, 0, w, h);

  // Lưới ô vuông truyền thống (giúp định vị nét vẽ)
  drawCtx.strokeStyle = 'rgba(255,255,255,.07)';
  drawCtx.lineWidth   = 1;
  drawCtx.setLineDash([4, 4]);
  // Đường chéo dọc + ngang
  drawCtx.beginPath(); drawCtx.moveTo(w/2,0); drawCtx.lineTo(w/2,h); drawCtx.stroke();
  drawCtx.beginPath(); drawCtx.moveTo(0,h/2); drawCtx.lineTo(w,h/2); drawCtx.stroke();
  // Đường chéo
  drawCtx.strokeStyle = 'rgba(255,255,255,.03)';
  drawCtx.beginPath(); drawCtx.moveTo(0,0); drawCtx.lineTo(w,h); drawCtx.stroke();
  drawCtx.beginPath(); drawCtx.moveTo(w,0); drawCtx.lineTo(0,h); drawCtx.stroke();
  drawCtx.setLineDash([]);

  // Vẽ lại tất cả nét
  applyBrush();
  drawStrokes.forEach(stroke => {
    if (stroke.length < 2) return;
    drawCtx.beginPath();
    drawCtx.moveTo(stroke[0].x, stroke[0].y);
    stroke.slice(1).forEach(p => drawCtx.lineTo(p.x, p.y));
    drawCtx.stroke();
  });
}

function clearDrawCanvas() {
  clearDrawAutoTimer();
  drawStrokes    = [];
  drawCurStroke  = [];
  drawWaitingResult = false;
  redrawCanvas();
  setDrawResult('');
  document.getElementById('draw-submit')?.removeAttribute('disabled');
}

function clearDrawAutoTimer() {
  if (drawAutoTimer) { clearTimeout(drawAutoTimer); drawAutoTimer = null; }
}

// ── Nhận dạng ─────────────────────────────────────
function recognizeDrawing() {
  if (drawStrokes.length === 0) return;
  if (drawWaitingResult) return;

  if (!window.handwriting) {
    setDrawResult('⚠️ Đang tải thư viện nhận dạng, thử lại sau 2 giây…');
    setTimeout(recognizeDrawing, 2000);
    return;
  }

  drawWaitingResult = true;
  setDrawResult('<span class="draw-loading">🔍 Đang nhận dạng…</span>');

  // Chuyển sang format handwriting.js: mỗi nét = [[x0,x1,...],[y0,y1,...]]
  const data = drawStrokes.map(stroke => [
    stroke.map(p => p.x),
    stroke.map(p => p.y)
  ]);

  const options = {
    width: drawCanvas.width,
    height: drawCanvas.height,
    language: 'ja',
    numOfWords: 1,
    numOfReturn: 10
  };

  window.handwriting.recognize(data, options, (results, err) => {
    drawWaitingResult = false;
    if (err || !results || results.length === 0) {
      setDrawResult('❌ Không nhận dạng được. Vẽ lại rõ hơn nhé!');
      return;
    }
    evalDrawResult(results);
  });
}

function evalDrawResult(results) {
  if (!drawCurrentK) return;
  const target    = drawCurrentK.kanji;
  const isCorrect = results.slice(0, 6).includes(target);

  drawTotal++;
  updateDrawScore();

  if (isCorrect) {
    drawCorrect++;
    updateDrawScore();
    setDrawResult(
      `<span class="draw-correct">✅ Chính xác!</span> <span style="font-size:1.6rem">${target}</span>`
    );
    flashCanvas('#22c55e');
    if (typeof playTone === 'function') playTone(880, 'sine', 0.15);
    document.getElementById('draw-submit')?.setAttribute('disabled', 'true');
    setTimeout(nextDrawCard, 1300);
  } else {
    const top3 = results.slice(0, 3).join('  ');
    setDrawResult(
      `<span class="draw-wrong">❌ Chưa đúng</span> — AI đọc: <b>${top3}</b><br>` +
      `<small style="opacity:.55">Thử vẽ lại hoặc nhấn Bỏ qua</small>`
    );
    flashCanvas('#ef4444');
    if (typeof playTone === 'function') playTone(220, 'sawtooth', 0.18);
    // Cho phép vẽ lại (xóa canvas tự động sau 1s gợi ý)
    setTimeout(() => {
      if (!drawWaitingResult) {
        drawStrokes = []; redrawCanvas();
        document.getElementById('draw-submit')?.removeAttribute('disabled');
      }
    }, 1000);
  }
}

function flashCanvas(color) {
  if (!drawCtx) return;
  drawCtx.save();
  drawCtx.globalAlpha = 0.25;
  drawCtx.fillStyle   = color;
  drawCtx.fillRect(0, 0, drawCanvas.width, drawCanvas.height);
  drawCtx.restore();
  setTimeout(() => redrawCanvas(), 500);
}

function updateDrawScore() {
  const el = document.getElementById('draw-score-text');
  if (el) el.textContent = `${drawCorrect} / ${drawTotal}`;
}

function setDrawResult(html) {
  const el = document.getElementById('draw-result');
  if (el) el.innerHTML = html;
}

// ── Card navigation ────────────────────────────────
function loadDrawCard() {
  clearDrawCanvas();
  drawCurrentK = drawDeck[drawIdx];
  const k = drawCurrentK;

  document.getElementById('draw-meaning').textContent  = k.meaning;
  document.getElementById('draw-reading').textContent  =
    `On: ${k.on || '—'}  ·  Kun: ${k.kun || '—'}`;
  document.getElementById('draw-hanviet').textContent  = k.hanviet || '';
  document.getElementById('draw-kanji-reveal').textContent  = '';
  document.getElementById('draw-kanji-reveal').classList.remove('revealed');
  document.getElementById('draw-show-kanji').style.display = '';
  document.getElementById('draw-progress-text').textContent =
    `${drawIdx + 1} / ${drawDeck.length}`;
  setDrawResult('');
  document.getElementById('draw-done').classList.remove('visible');
}

function nextDrawCard() {
  drawIdx++;
  if (drawIdx >= drawDeck.length) { showDrawDone(); return; }
  loadDrawCard();
}

function revealDrawKanji() {
  if (!drawCurrentK) return;
  const el = document.getElementById('draw-kanji-reveal');
  el.textContent = drawCurrentK.kanji;
  el.classList.add('revealed');
  document.getElementById('draw-show-kanji').style.display = 'none';
}

function showDrawDone() {
  const pct = drawTotal
    ? Math.round((drawCorrect / drawTotal) * 100) : 0;
  document.getElementById('draw-done-pct').textContent    = pct + '%';
  document.getElementById('draw-done-detail').textContent =
    `Đúng: ${drawCorrect}  ·  Tổng: ${drawTotal} kanji`;
  document.getElementById('draw-done').classList.add('visible');
  if (typeof playTone === 'function') playTone(880, 'triangle', 0.3);
}

function buildDrawDeck() {
  const all  = getFilteredDeck();        // từ kanji-state.js
  drawDeck   = shuffle(all).slice(0, 20);
  drawIdx    = 0;
  drawCorrect= 0;
  drawTotal  = 0;
  updateDrawScore();
  loadDrawCard();
}

// ── DOM init ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('draw-screen')) return;

  initDrawCanvas();

  // Nút quay về
  document.getElementById('draw-back').addEventListener('click', () => {
    clearDrawAutoTimer();
    showScreen('home-screen');
    updateHomeProgress();
  });

  // Nút điều khiển
  document.getElementById('draw-clear').addEventListener('click', clearDrawCanvas);

  document.getElementById('draw-submit').addEventListener('click', () => {
    clearDrawAutoTimer();
    if (drawStrokes.length > 0) recognizeDrawing();
  });

  document.getElementById('draw-skip').addEventListener('click', () => {
    clearDrawAutoTimer();
    if (!drawCurrentK) return;
    setDrawResult(
      `⏭ Bỏ qua · Kanji: <span class="draw-reveal-kanji">${drawCurrentK.kanji}</span>`
    );
    drawTotal++;
    updateDrawScore();
    setTimeout(nextDrawCard, 1000);
  });

  document.getElementById('draw-show-kanji').addEventListener('click', revealDrawKanji);

  // Kết thúc session
  document.getElementById('draw-restart').addEventListener('click', buildDrawDeck);
  document.getElementById('draw-home').addEventListener('click', () => {
    showScreen('home-screen');
    updateHomeProgress();
  });

  // Bắt đầu game từ card trên home
  document.getElementById('go-draw').addEventListener('click', () => {
    showScreen('draw-screen');
    buildDrawDeck();
  });
});
