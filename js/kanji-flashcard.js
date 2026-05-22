// ══════════════════════════════════════════
// ══ GAME 1: FLASHCARD ══
// ══════════════════════════════════════════
let deck = [], idx = 0, correct = 0, incorrect = 0;
let isAnimating = false, isFlipped = false;
let currentIsCorrectMeaning = true;
let mode = "easy", streak = 0;
let timerHandle = null, TIME_LIMIT = 6000;

const cardEl       = document.getElementById('card');
const kanjiEl      = document.getElementById('kanji');
const hanvietEl    = document.getElementById('han-viet');
const hardReadingEl= document.getElementById('hard-reading');
const shownMeaning = document.getElementById('shown-meaning');
const readingOn    = document.getElementById('reading-on');
const readingKun   = document.getElementById('reading-kun');
const verdictBadge = document.getElementById('verdict-badge');
const verdictHint  = document.getElementById('verdict-hint');
const meaningArea  = document.getElementById('meaning-area');
const backKanjiEl  = document.getElementById('back-kanji');
const backContent  = document.getElementById('back-content');
const progressText = document.getElementById('progress-text');
const progressBar  = document.getElementById('progress-bar');
const timerWrap    = document.getElementById('timer-wrap');
const timerBar     = document.getElementById('timer-bar');
const sCorrect     = document.getElementById('s-correct');
const sIncorrect   = document.getElementById('s-incorrect');
const feedbackEl   = document.getElementById('feedback');
const doneScreen   = document.getElementById('done-screen');
const streakBadge  = document.getElementById('streak-badge');
const instruction  = document.getElementById('instruction');
const kanjiArea    = document.getElementById('kanji-area');

function playTone(freq, type, vol) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(vol, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + .25);
    o.start(); o.stop(ctx.currentTime + .25);
  } catch(e){}
}

function stopTimer() {
  clearInterval(timerHandle); timerHandle = null;
  timerWrap.style.display = 'none';
  timerBar.style.transform = 'scaleX(1)';
}

function startTimer() {
  stopTimer();
  timerWrap.style.display = 'block';
  timerBar.style.transition = 'none';
  timerBar.style.transform = 'scaleX(1)';
  const start = Date.now();
  timerHandle = setInterval(() => {
    const elapsed = Date.now() - start;
    const ratio = Math.max(0, 1 - elapsed / TIME_LIMIT);
    timerBar.style.transition = 'none';
    timerBar.style.transform = `scaleX(${ratio})`;
    if (elapsed >= TIME_LIMIT) { clearInterval(timerHandle); handleWrong(true); }
  }, 50);
}

function renderCard() {
  if (idx >= deck.length) { showDone(); return; }
  stopTimer(); isFlipped = false;
  cardEl.classList.remove('flipped');
  const k = deck[idx];
  kanjiEl.textContent = k.kanji;
  hanvietEl.textContent = k.hanviet;
  backKanjiEl.textContent = k.kanji;
  progressText.textContent = `${idx + 1} / ${deck.length}`;
  progressBar.style.width = `${(idx / deck.length) * 100}%`;
  sCorrect.textContent = correct; sIncorrect.textContent = incorrect;
  streakBadge.textContent = `🔥 ${streak}`;
  streakBadge.style.display = streak >= 3 ? 'block' : 'none';
  verdictBadge.className = ''; verdictBadge.style.display = 'none';
  verdictHint.style.display = 'block';
  meaningArea.classList.remove('hidden');

  if (mode === 'easy') {
    kanjiArea.classList.remove('hard-glow');
    hardReadingEl.style.display = 'none';
    readingOn.style.display = ''; readingKun.style.display = '';
    timerWrap.style.display = 'none';
    const showCorrect = Math.random() > .45;
    currentIsCorrectMeaning = showCorrect;
    if (showCorrect) {
      shownMeaning.innerHTML = k.meaning +
        '<div class="shown-reading"><span class="sr-on">' + k.on + '</span>' +
        '<span class="sr-kun">' + k.kun + '</span></div>';
    } else {
      const pool = deck.filter((_,i) => i !== idx);
      const fake = pool[Math.floor(Math.random() * pool.length)];
      const fk = fake || k;
      shownMeaning.innerHTML = fk.meaning +
        '<div class="shown-reading"><span class="sr-on">' + fk.on + '</span>' +
        '<span class="sr-kun">' + fk.kun + '</span></div>';
      currentIsCorrectMeaning = false;
    }
    readingOn.textContent  = `On: ${k.on}`;
    readingKun.textContent = `Kun: ${k.kun}`;
    backContent.innerHTML = `
      <strong>${k.kanji}</strong> · ${k.hanviet}<br>
      <span style="color:#a78bfa">On: ${k.on}</span> · <span style="color:#67e8f9">Kun: ${k.kun}</span><br>
      <span class="correct-meaning">${k.meaning}</span>`;
  } else {
    // HARD: giống Easy — hiện nghĩa ngẫu nhiên đúng/sai
    // Không hiện On/Kun để khó hơn, có timer, sai = reset streak
    kanjiArea.classList.add('hard-glow');
    hardReadingEl.style.display = 'none';
    readingOn.style.display = 'none';
    readingKun.style.display = 'none';
    meaningArea.classList.remove('hidden');
    document.getElementById('btn-correct').style.visibility   = 'visible';
    document.getElementById('btn-incorrect').style.visibility = 'visible';
    // Nghĩa ngẫu nhiên đúng/sai + kèm hiragana/katakana
    const showCorrect = Math.random() > .45;
    currentIsCorrectMeaning = showCorrect;
    if (showCorrect) {
      shownMeaning.innerHTML = k.meaning +
        '<div class="shown-reading"><span class="sr-on">' + k.on + '</span>' +
        '<span class="sr-kun">' + k.kun + '</span></div>';
    } else {
      const pool = deck.filter((_,i) => i !== idx);
      const fake = pool[Math.floor(Math.random() * pool.length)];
      const fk = fake || k;
      shownMeaning.innerHTML = fk.meaning +
        '<div class="shown-reading"><span class="sr-on">' + fk.on + '</span>' +
        '<span class="sr-kun">' + fk.kun + '</span></div>';
      currentIsCorrectMeaning = false;
    }
    verdictHint.style.display = 'block';
    verdictHint.textContent   = 'Nghĩa đúng hay sai? ⏱';
    backContent.innerHTML = `
      <strong>${k.kanji}</strong> · ${k.hanviet}<br>
      <span style="color:#a78bfa">On: ${k.on}</span> · <span style="color:#67e8f9">Kun: ${k.kun}</span><br>
      <span class="correct-meaning">${k.meaning}</span>`;
    startTimer();
  }
}

function answer(userSaysCorrect) {
  if (isAnimating) return;
  isAnimating = true;
  stopTimer();
  const isRight = userSaysCorrect === currentIsCorrectMeaning;
  cardEl.classList.remove('flash-correct','flash-incorrect');
  if (isRight) {
    correct++; streak++;
    cardEl.classList.add('flash-correct');
    feedbackEl.textContent = '✓'; feedbackEl.style.color = 'var(--correct)';
    verdictBadge.className = 'cb'; verdictBadge.textContent = '✓ Đúng!';
    verdictBadge.style.display = 'inline-block';
    verdictHint.style.display = 'none';
    playTone(880, 'sine', 0.15);
  } else {
    incorrect++; streak = 0;
    cardEl.classList.add('flash-incorrect');
    feedbackEl.textContent = '✗'; feedbackEl.style.color = 'var(--incorrect)';
    verdictBadge.className = 'wb'; verdictBadge.textContent = '✗ Sai!';
    verdictBadge.style.display = 'inline-block';
    verdictHint.style.display = 'none';
    playTone(220, 'sawtooth', 0.18);
  }
  feedbackEl.classList.add('show');
  setTimeout(() => feedbackEl.classList.remove('show'), 450);
  if (mode === 'hard' && !isRight) {
    setTimeout(() => { cardEl.classList.remove('flash-correct','flash-incorrect'); handleWrong(false); isAnimating = false; }, 500);
  } else {
    setTimeout(() => {
      cardEl.classList.remove('flash-correct','flash-incorrect');
      idx++; if (idx >= deck.length) showDone(); else renderCard();
      isAnimating = false;
    }, mode === 'easy' ? 600 : 400);
  }
}

function handleWrong(isTimeout = false) {
  stopTimer(); isAnimating = false;
  document.getElementById('modal-emoji').textContent  = isTimeout ? '⏱' : '💥';
  document.getElementById('modal-title').textContent  = isTimeout ? '⏱ Hết giờ!' : '💥 Sai rồi!';
  document.getElementById('modal-streak').textContent = `${streak}`;
  document.getElementById('modal-detail').innerHTML =
    `Bạn đã đúng <strong style="color:#22c55e">${streak}</strong> câu liên tiếp<br>
     <small style="opacity:.6">Trên ${idx + (isTimeout?1:0)} thẻ đã qua</small>`;
  document.getElementById('modal-overlay').classList.add('visible');
}

function flipCard() {
  isFlipped = !isFlipped;
  cardEl.classList.toggle('flipped', isFlipped);
  playTone(440, 'sine', 0.08);
}

function showDone() {
  const total = correct + incorrect;
  const pct = total ? Math.round((correct / total) * 100) : 0;
  document.getElementById('final-pct').textContent = `${pct}%`;
  document.getElementById('final-detail').textContent = `Đúng: ${correct}  ·  Sai: ${incorrect}  ·  Tổng: ${total} thẻ`;
  progressBar.style.width = '100%';
  doneScreen.classList.add('visible');
  playTone(880, 'triangle', 0.3);
}

function buildDeck() {
  stopTimer();
  if (mode === 'easy') {
    document.getElementById('btn-correct').style.visibility   = 'visible';
    document.getElementById('btn-incorrect').style.visibility = 'visible';
  }
  deck = shuffle(getFilteredDeck());
  idx = 0; correct = 0; incorrect = 0; streak = 0;
  isFlipped = false; isAnimating = false;
  doneScreen.classList.remove('visible');
  document.getElementById('modal-overlay').classList.remove('visible');
  renderCard();
}
function resetHard() {
  streak = 0; idx = 0; correct = 0; incorrect = 0;
  deck = shuffle(deck); isFlipped = false; isAnimating = false;
  document.getElementById('modal-overlay').classList.remove('visible');
  renderCard();
}
function applyModeUI() {
  if (mode === 'easy') {
    instruction.className = 'easy-inst';
    instruction.textContent = '← Đúng  |  Nghĩa đúng hay sai?  |  Sai →';
    document.querySelector('[data-mode="easy"]').className = 'mode-btn active-easy';
    document.querySelector('[data-mode="hard"]').className = 'mode-btn';
    document.getElementById('btn-correct').style.visibility   = 'visible';
    document.getElementById('btn-incorrect').style.visibility = 'visible';
  } else {
    instruction.className = 'hard-inst';
    instruction.textContent = '↩ Lật thẻ → xem nghĩa → tự đánh giá · Sai = reset';
    document.querySelector('[data-mode="easy"]').className = 'mode-btn';
    document.querySelector('[data-mode="hard"]').className = 'mode-btn active-hard';
    // Ẩn Đúng/Sai ban đầu
    document.getElementById('btn-correct').style.visibility   = 'hidden';
    document.getElementById('btn-incorrect').style.visibility = 'hidden';
  }
}

document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    mode = btn.dataset.mode;
    document.getElementById('timer-select-wrap').style.display = mode === 'hard' ? 'flex' : 'none';
    applyModeUI(); buildDeck();
  });
});
document.querySelectorAll('.timer-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.timer-btn').forEach(b => b.classList.remove('active-timer'));
    btn.classList.add('active-timer');
    TIME_LIMIT = parseInt(btn.dataset.sec) * 1000;
    buildDeck();
  });
});
document.getElementById('btn-correct').addEventListener('click',   () => answer(true));
document.getElementById('btn-incorrect').addEventListener('click', () => answer(false));
document.getElementById('btn-flip').addEventListener('click', flipCard);
document.getElementById('btn-shuffle').addEventListener('click', () => {
  stopTimer(); deck = shuffle(deck); idx = 0; correct = 0; incorrect = 0; streak = 0; renderCard();
});
document.getElementById('btn-restart').addEventListener('click', buildDeck);
document.getElementById('modal-btn').addEventListener('click', () => {
  if (mode === 'hard') resetHard(); else buildDeck();
});
document.addEventListener('keydown', e => {
  if (document.getElementById('flash-screen').classList.contains('active')) {
    if (e.key === 'ArrowLeft')  answer(true);
    if (e.key === 'ArrowRight') answer(false);
    if (e.key === ' ' || e.key === 'ArrowUp') { e.preventDefault(); flipCard(); }
  }
});
let touchX = 0, touchY = 0, touchT = 0;
cardEl.addEventListener('touchstart', e => {
  touchX = e.changedTouches[0].clientX;
  touchY = e.changedTouches[0].clientY;
  touchT = Date.now();
}, { passive: true });
cardEl.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchX;
  const dy = e.changedTouches[0].clientY - touchY;
  const dt = Date.now() - touchT;
  if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) answer(dx > 0);
  else if (Math.abs(dx) < 10 && Math.abs(dy) < 10 && dt < 300) flipCard();
}, { passive: true });

