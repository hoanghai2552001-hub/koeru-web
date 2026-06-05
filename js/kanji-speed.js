// ══════════════════════════════════════════
// ══ GAME 4: SPEED KANJI ══
// 5 phút · tap đúng nghĩa · combo · FEVER
// ══════════════════════════════════════════

// ══════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════
const SESSION_DURATION  = 5 * 60;  // 5 phút (giây)
const BASE_ANSWER_TIME  = 6000;    // ms mỗi câu (ban đầu)
const MIN_ANSWER_TIME   = 1800;    // tối thiểu
const COMBO_THRESHOLDS  = [3, 6, 10, 15];
const SP_XP_LVL         = 150;
const FEVER_COMBO       = 10;

// ══════════════════════════════════════════
// SESSION STATE
// ══════════════════════════════════════════
let spLvl         = 'ALL';
let spAnswerMode  = 'vn';  // 'vn' | 'jp'
let spDeck        = [], spUsed = new Set();
let spCard        = null;
let spStr         = 0, spMaxStr  = 0;
let spCmb         = 1, spMaxCmb  = 1;
let spSc          = 0, spOk      = 0, spTot = 0;
let spXpG         = 0;           // XP earned this session
let sessionTimeLeft = SESSION_DURATION;
let answerStart     = 0;
let sessionHandle   = null, speedHandle = null;
let isFever         = false;
let spAns           = false;     // true = câu hỏi đang chờ trả lời
let spWrong         = [];        // [{kanji, meaning, count}] SRS trong phiên

// ══════════════════════════════════════════
// PERSISTENT STATS
// ══════════════════════════════════════════
let pStreak = 0, pBest = 0, pTotal = 0;
let pXP = 0, pLevel = 1, pDayStreak = 0;

function spLoadProgress() {
  try {
    const d = JSON.parse(localStorage.getItem('sp_v1') || '{}');
    pBest      = d.best       || 0;
    pTotal     = d.total      || 0;
    pXP        = d.xp         || 0;
    pLevel     = d.level      || 1;
    pDayStreak = d.dayStreak  || 0;
    pStreak    = d.streak     || 0;
  } catch(e) {}
}
function spSaveProgress() {
  try {
    localStorage.setItem('sp_v1', JSON.stringify({
      best: pBest, total: pTotal, xp: pXP,
      level: pLevel, dayStreak: pDayStreak, streak: pStreak,
    }));
  } catch(e) {}
}

// ══════════════════════════════════════════
// HOME UI
// ══════════════════════════════════════════
function spUpdateHome() {
  document.getElementById('sp-hs').textContent    = pStreak;
  document.getElementById('sp-hb').textContent    = pBest;
  document.getElementById('sp-ht').textContent    = pTotal;
  document.getElementById('sp-lvlbdg').textContent = `Lv.${pLevel}`;
  document.getElementById('sp-xpf2').style.width  = `${(pXP / SP_XP_LVL) * 100}%`;
  document.getElementById('sp-xptxt').textContent = `${pXP} / ${SP_XP_LVL} XP`;
}

// ══════════════════════════════════════════
// BACKGROUND PARTICLES (canvas)
// ══════════════════════════════════════════
let spCanvas = null, spCtx = null;
let particles = [];
let particleRafHandle = null;

function initCanvas() {
  spCanvas = document.getElementById('sp-canvas');
  if (!spCanvas) return;
  spCtx = spCanvas.getContext('2d');
  spCanvas.width  = window.innerWidth;
  spCanvas.height = window.innerHeight;
  particles = Array.from({ length: 30 }, () => ({
    x:  Math.random() * spCanvas.width,
    y:  Math.random() * spCanvas.height,
    r:  Math.random() * 2 + 0.5,
    vx: (Math.random() - 0.5) * 0.3,
    vy: (Math.random() - 0.5) * 0.3,
    a:  Math.random() * 0.4 + 0.1,
    color: Math.random() > 0.5 ? '129,140,248' : '244,114,182',
  }));
}
function drawParticles() {
  if (!spCtx || !spCanvas) return;
  spCtx.clearRect(0, 0, spCanvas.width, spCanvas.height);
  particles.forEach(p => {
    spCtx.beginPath();
    spCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    spCtx.fillStyle = `rgba(${p.color},${p.a})`;
    spCtx.fill();
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > spCanvas.width)  p.vx *= -1;
    if (p.y < 0 || p.y > spCanvas.height) p.vy *= -1;
  });
  particleRafHandle = requestAnimationFrame(drawParticles);
}

// ══════════════════════════════════════════
// VISUAL HELPERS
// ══════════════════════════════════════════
function ripple(x, y, color) {
  const el = document.createElement('div');
  el.className = 'ripple';
  el.style.cssText = `left:${x - 24}px;top:${y - 24}px;width:48px;height:48px;background:${color};`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 500);
}
function floatScore(text, color, x, y) {
  const el = document.createElement('div');
  el.className = 'score-float';
  el.style.cssText = `color:${color};left:${x - 20}px;top:${y - 10}px;`;
  el.textContent = text;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 800);
}

// ══════════════════════════════════════════
// GAME LOGIC
// ══════════════════════════════════════════
const _SP_ENABLED = new Set(['N5','N4','N3','N2']);
function spGetDeck() {
  const base = ALL_KANJI.filter(k => _SP_ENABLED.has(k.level));
  return spLvl === 'ALL' ? base : base.filter(k => k.level === spLvl);
}
function getAnswerTime() {
  const reduction = Math.min(spCmb - 1, 12) * 200;
  return Math.max(BASE_ANSWER_TIME - reduction, MIN_ANSWER_TIME);
}
function spGetAns(k) {
  if (spAnswerMode === 'jp') {
    const kun = k.kun && k.kun !== '—' ? k.kun : '';
    const on  = k.on  && k.on  !== '—' ? k.on  : '';
    return kun || on || k.meaning;
  }
  return k.meaning;
}

function startGame() {
  if (!spCanvas) { initCanvas(); if (spCanvas) drawParticles(); }
  stopGame();
  showScreen('s-speed');
  spDeck = shuffle(spGetDeck());
  spUsed.clear();
  spWrong = [];
  spStr = 0; spMaxStr = 0;
  spCmb = 1; spMaxCmb = 1;
  spSc  = 0; spOk     = 0; spTot = 0;
  spXpG = 0;
  isFever = false;
  spAns   = false;
  sessionTimeLeft = SESSION_DURATION;
  setFever(false);
  updateHUD();
  sessionHandle = setInterval(() => {
    sessionTimeLeft--;
    updateSessionBar();
    if (sessionTimeLeft <= 0) { clearInterval(sessionHandle); endGame(); }
  }, 1000);
  nextCard();
}

function stopGame() {
  clearInterval(sessionHandle);
  clearTimeout(speedHandle);
  sessionHandle = speedHandle = null;
  if (particleRafHandle) { cancelAnimationFrame(particleRafHandle); particleRafHandle = null; }
  particles = [];
  const hintEl = document.getElementById('sp-jp-hint');
  if (hintEl) { hintEl.style.color = ''; hintEl.textContent = ''; }
}

function updateHUD() {
  document.getElementById('sp-sv').textContent  = spStr;
  document.getElementById('sp-cv').textContent  = `×${spCmb}`;
  document.getElementById('sp-scv').textContent = spSc;
  const m = Math.floor(sessionTimeLeft / 60), s = sessionTimeLeft % 60;
  document.getElementById('sp-tv').textContent  = `${m}:${s.toString().padStart(2, '0')}`;
}
function updateSessionBar() {
  const ratio = sessionTimeLeft / SESSION_DURATION;
  document.getElementById('sp-ss').style.transform = `scaleX(${ratio})`;
  updateHUD();
}

// ── Speed bar per question ──
function startSpeedBar() {
  clearTimeout(speedHandle);
  const limit = getAnswerTime();
  answerStart = Date.now();
  const bar = document.getElementById('sp-sb');
  bar.style.transition = 'none';
  bar.style.transform  = 'scaleX(1)';
  function tick() {
    const elapsed = Date.now() - answerStart;
    const ratio   = Math.max(0, 1 - elapsed / limit);
    bar.style.transform = `scaleX(${ratio})`;
    if (ratio <= 0) { spOnTimeout(); return; }
    speedHandle = setTimeout(tick, 30);
  }
  speedHandle = setTimeout(tick, 30);
}
function stopSpeedBar() { clearTimeout(speedHandle); }

function setFever(on) {
  isFever = on;
  document.getElementById('sp-fov').classList.toggle('active',  on);
  document.getElementById('sp-ft').classList.toggle('visible',  on);
  document.getElementById('sp-k').classList.toggle('fever-glow', on);
}

function nextCard() {
  spAns = true; // kích hoạt trả lời
  if (spUsed.size >= spDeck.length) {
    spUsed.clear();
    // SRS: re-sort deck mỗi vòng để ưu tiên thẻ đến hạn
    const base = spGetDeck();
    spDeck = window.koeruMastery ? window.koeruMastery.sortDeckByPriority(base) : shuffle(base);
  }
  let idx;
  // Ưu tiên thẻ sai trong phiên (40% cơ hội)
  const wrongAvail = spWrong.filter(w => w.count > 0);
  if (wrongAvail.length > 0 && Math.random() < 0.4) {
    const w = wrongAvail[Math.floor(Math.random() * wrongAvail.length)];
    idx = spDeck.findIndex(k => k.kanji === w.kanji);
    if (idx === -1) idx = pickUnused();
  } else {
    idx = pickUnused();
  }
  spUsed.add(idx);
  spCard = spDeck[idx];

  // Animate card in
  const stage = document.getElementById('sp-stage');
  stage.style.animation = 'none';
  stage.offsetHeight; // reflow
  stage.style.animation = 'stageIn .25s cubic-bezier(.34,1.56,.64,1)';

  document.getElementById('sp-k').textContent  = spCard.kanji;
  document.getElementById('sp-hv').textContent = spCard.hanviet;
  const reading = spCard.on !== '—' ? spCard.on : spCard.kun;
  document.getElementById('sp-rd').textContent = reading;

  // Phát âm kanji sau 0.8s (không chặn UX)
  if (soundEnabled && window.speechSynthesis) {
    speechSynthesis.cancel();
    setTimeout(() => {
      const utt = new SpeechSynthesisUtterance(spCard.kanji);
      utt.lang = 'ja-JP'; utt.rate = 0.9; utt.volume = 0.7;
      speechSynthesis.speak(utt);
    }, 800);
  }

  renderOptions();
  startSpeedBar();
}

function pickUnused() {
  let tries = 0, idx;
  do {
    idx = Math.floor(Math.random() * spDeck.length);
    tries++;
  } while (spUsed.has(idx) && tries < spDeck.length);
  return idx;
}

function renderOptions() {
  const grid = document.getElementById('sp-opts');
  grid.innerHTML = '';
  const wrong = shuffle(spDeck.filter(k => k.kanji !== spCard.kanji)).slice(0, 3).map(k => spGetAns(k));
  const opts  = shuffle([spGetAns(spCard), ...wrong]);
  // JP mode: gợi ý nghĩa VN nhỏ
  const hint = document.getElementById('sp-jp-hint');
  if (hint) hint.textContent = spAnswerMode === 'jp' ? spCard.meaning : '';
  grid.style.gridTemplateColumns = '1fr 1fr';
  opts.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = `opt-btn appear-${i + 1}`;
    btn.textContent = opt;
    btn.addEventListener('click', e => spOnAnswer(btn, opt, e));
    grid.appendChild(btn);
  });
}

function spOnAnswer(btn, chosen, e) {
  if (!spAns) return;
  spAns = false;
  stopSpeedBar();
  spTot++;
  const isRight = chosen === spGetAns(spCard);
  const rect = btn.getBoundingClientRect();
  const cx = (rect.left + rect.right) / 2, cy = (rect.top + rect.bottom) / 2;

  if (isRight) {
    spOk++; spStr++;
    spMaxStr = Math.max(spMaxStr, spStr);
    spCmb    = Math.min(spCmb + 1, 20);
    spMaxCmb = Math.max(spMaxCmb, spCmb);

    const elapsed    = Date.now() - answerStart;
    const speedBonus = Math.max(1, Math.round(3 * (1 - elapsed / getAnswerTime())));
    const pts = 10 * spCmb * speedBonus;
    spSc  += pts;
    spXpG += Math.max(5, Math.floor(pts / 4));

    btn.classList.add('correct');
    ripple(cx, cy, 'rgba(16,185,129,.4)');
    floatScore(`+${pts}`, '#6ee7b7', cx, cy - 40);
    playTone(660 + spCmb * 30, 'sine', 0.1);

    if (spCmb >= 3) showComboText();
    if (spCmb >= FEVER_COMBO && !isFever) setFever(true);

    // Ghi nhận vào unified mastery
    if (window.koeruMastery) window.koeruMastery.record(spCard.kanji, true, 'speed');
    // Giảm đếm SRS phiên
    const wi = spWrong.findIndex(w => w.kanji === spCard.kanji);
    if (wi > -1) spWrong[wi].count = Math.max(0, spWrong[wi].count - 1);

    setTimeout(() => { btn.classList.remove('correct'); nextCard(); }, 300);

  } else {
    spStr = 0;
    spCmb = Math.max(1, spCmb - 2);
    if (isFever) setFever(false);

    btn.classList.add('wrong');
    document.querySelectorAll('.opt-btn').forEach(b => {
      if (b.textContent === spGetAns(spCard)) b.classList.add('reveal');
    });
    ripple(cx, cy, 'rgba(244,63,94,.4)');
    playTone(200, 'sawtooth', 0.12);

    const stage = document.getElementById('sp-stage');
    stage.classList.add('wrong-shake');
    setTimeout(() => stage.classList.remove('wrong-shake'), 400);

    const hint = document.getElementById('sp-jp-hint');
    if (hint) {
      hint.style.color = '#f87171';
      hint.textContent = `✗  ${spCard.meaning}  ·  ${spCard.on !== '—' ? spCard.on : spCard.kun}`;
    }

    // Ghi nhận sai vào unified mastery
    if (window.koeruMastery) window.koeruMastery.record(spCard.kanji, false, 'speed');
    const wi = spWrong.findIndex(w => w.kanji === spCard.kanji);
    if (wi > -1) spWrong[wi].count++;
    else spWrong.push({ kanji: spCard.kanji, meaning: spCard.meaning, count: 2 });

    setTimeout(() => {
      btn.classList.remove('wrong');
      document.querySelectorAll('.opt-btn.reveal').forEach(b => b.classList.remove('reveal'));
      if (hint) { hint.style.color = ''; hint.textContent = spAnswerMode === 'jp' ? spCard.meaning : ''; }
      nextCard();
    }, 1200);
  }
  updateHUD();
}

function spOnTimeout() {
  if (!spAns) return;
  spAns = false;
  spTot++; spStr = 0;
  spCmb = Math.max(1, spCmb - 1);
  if (isFever) setFever(false);

  document.querySelectorAll('.opt-btn').forEach(b => {
    if (b.textContent === spGetAns(spCard)) b.classList.add('reveal');
  });
  playTone(180, 'sawtooth', 0.1);

  const hintT = document.getElementById('sp-jp-hint');
  if (hintT) {
    hintT.style.color = '#f87171';
    hintT.textContent = `⏱  ${spCard.meaning}  ·  ${spCard.on !== '—' ? spCard.on : spCard.kun}`;
  }

  const wi = spWrong.findIndex(w => w.kanji === spCard.kanji);
  if (wi > -1) spWrong[wi].count++;
  else spWrong.push({ kanji: spCard.kanji, meaning: spCard.meaning, count: 2 });

  setTimeout(() => {
    document.querySelectorAll('.opt-btn.reveal').forEach(b => b.classList.remove('reveal'));
    if (hintT) { hintT.style.color = ''; hintT.textContent = spAnswerMode === 'jp' ? spCard.meaning : ''; }
    nextCard();
  }, 1000);
  updateHUD();
}

function showComboText() {
  const el     = document.getElementById('sp-cp');
  const labels = { 3: '🔥 COMBO!', 6: '⚡ SUPER!', 10: '💥 FEVER!', 15: '🌟 GODLIKE!' };
  const colors = { 3: '#f472b6', 6: '#818cf8', 10: '#f59e0b', 15: '#10b981' };
  const key    = COMBO_THRESHOLDS.filter(t => spCmb >= t).pop() || 3;
  el.textContent = labels[key] || `×${spCmb}`;
  el.style.color = colors[key] || '#f472b6';
  el.classList.remove('show');
  el.offsetHeight;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 600);
}

// ══════════════════════════════════════════
// END GAME / KẾT QUẢ
// ══════════════════════════════════════════
function endGame() {
  stopGame();
  setFever(false);
  const acc   = spTot > 0 ? Math.round((spOk / spTot) * 100) : 0;
  const grade = acc >= 95 && spMaxCmb >= 10 ? 'S'
              : acc >= 85 ? 'A'
              : acc >= 70 ? 'B'
              : acc >= 55 ? 'C' : 'D';
  const emojis = { S: '🏆', A: '🔥', B: '✨', C: '👍', D: '💪' };
  const titles = { S: 'Xuất sắc!', A: 'Tuyệt vời!', B: 'Không tệ!', C: 'Cố lên!', D: 'Luyện thêm nhé!' };

  pBest   = Math.max(pBest, spSc);
  pTotal += spOk;
  pStreak = spMaxStr;
  pXP    += spXpG;
  while (pXP >= SP_XP_LVL) { pXP -= SP_XP_LVL; pLevel++; }
  spSaveProgress();

  document.getElementById('sr-e').textContent   = emojis[grade];
  document.getElementById('sr-t').textContent   = titles[grade];
  document.getElementById('sr-g').textContent   = grade;
  document.getElementById('sr-stk').textContent = spMaxStr;
  document.getElementById('sr-cmb').textContent = `×${spMaxCmb}`;
  document.getElementById('sr-acc').textContent = acc + '%';
  document.getElementById('sr-xp').textContent  = '+' + spXpG;

  // SRS feedback
  const srsEl    = document.getElementById('sr-srs-list');
  const hardCards = spWrong.filter(w => w.count > 0).slice(0, 5);
  srsEl.innerHTML = hardCards.length === 0
    ? '<div class="srs-item" style="color:var(--ok)">✅ Không có từ nào cần ôn lại!</div>'
    : hardCards.map(w => `
        <div class="srs-item">
          <span class="kanji">${w.kanji}</span>
          <span class="srs-dot hard"></span>
          <span>${w.meaning}</span>
        </div>`).join('');

  playTone(grade === 'S' ? 1000 : grade === 'A' ? 880 : 660, 'triangle', 0.2);
  showScreen('s-spr');
}

// ══════════════════════════════════════════
// INIT & EVENT LISTENERS
// ══════════════════════════════════════════
spLoadProgress();

document.addEventListener('DOMContentLoaded', () => {
  applyModeUI(); // từ kanji-flashcard.js — khởi tạo mode buttons (phải sau khi DOM sẵn sàng)
  spUpdateHome();

  // Level filter (home SP)
  document.querySelectorAll('.sp-lb').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sp-lb').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
      spLvl = btn.dataset.lvl;
    });
  });

  // Answer mode (VN / JP)
  document.querySelectorAll('.sp-mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sp-mode-btn').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
      spAnswerMode = btn.dataset.mode;
      const sub = document.getElementById('sp-psub');
      if (sub) sub.textContent = spAnswerMode === 'jp'
        ? 'chọn nghĩa tiếng Nhật · combo = nhiều XP'
        : 'tap đúng nghĩa · combo = nhiều XP';
    });
  });

  // Navigation buttons
  document.getElementById('sp-pbtn')?.addEventListener('click', startGame);
  document.getElementById('sp-back')?.addEventListener('click', () => {
    stopGame(); showScreen('home-screen'); spUpdateHome();
  });
  document.getElementById('sr-retry')?.addEventListener('click', startGame);
  document.getElementById('sr-home')?.addEventListener('click', () => {
    showScreen('home-screen'); spUpdateHome();
  });
  document.getElementById('spr-back')?.addEventListener('click', () => {
    showScreen('s-sph'); spUpdateHome();
  });
  document.getElementById('go-speed')?.addEventListener('click', () => {
    showScreen('s-sph'); spLoadProgress(); spUpdateHome();
  });
});
