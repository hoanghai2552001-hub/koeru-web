// ══════════════════════════════════════════
// ══ GAME 1: FLASHCARD ══
// ══════════════════════════════════════════
let deck = [], idx = 0, correct = 0, incorrect = 0;
let isAnimating = false, isFlipped = false;
let cardShownTime = 0;
let currentIsCorrectMeaning = true;
let mode = "easy", streak = 0;
let timerHandle = null, TIME_LIMIT = 6000;

// DOM refs — assigned in DOMContentLoaded below
let cardEl, kanjiEl, hanvietEl, hardReadingEl, shownMeaning;
let readingOn, readingKun, verdictBadge, verdictHint, meaningArea;
let backKanjiEl, backContent, progressText, progressBar;
let timerWrap, timerBar, sCorrect, sIncorrect, feedbackEl;
let doneScreen, streakBadge, instruction, kanjiArea;

// playTone() được dùng từ kanji-state.js (đã load trước)

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
  stopTimer(); isFlipped = false; cardShownTime = Date.now();
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
    const pool = deck.filter((x,i) => i !== idx && x.meaning !== k.meaning);
    const showCorrect = pool.length === 0 ? true : Math.random() > .45;
    currentIsCorrectMeaning = showCorrect;
    if (showCorrect) {
      shownMeaning.textContent = k.meaning;
      readingOn.textContent  = `On: ${k.on || '—'}`;
      readingKun.textContent = `Kun: ${k.kun || '—'}`;
    } else {
      const fake = pool[Math.floor(Math.random() * pool.length)];
      shownMeaning.textContent = fake.meaning;
      readingOn.textContent  = `On: ${k.on || '—'}`;
      readingKun.textContent = `Kun: ${k.kun || '—'}`;
    }
    const wordsHtml = filterWordsForLevel(k.words, selectedLevel).slice(0,3).map(w =>
      `<span class="back-word"><span class="bw-kanji">${w.w}</span><span class="bw-read">${w.r||''}</span><span class="bw-mean">${w.m||''}</span></span>`
    ).join('');
    backContent.innerHTML = `
      <div class="back-reading">
        <span class="back-on">On: ${k.on||'—'}</span>
        <span class="back-kun">Kun: ${k.kun||'—'}</span>
      </div>
      <div class="back-correct-meaning">${k.meaning}</div>
      ${wordsHtml ? `<div class="back-words">${wordsHtml}</div>` : ''}`;
  } else {
    kanjiArea.classList.add('hard-glow');
    hardReadingEl.style.display = 'none';
    readingOn.style.display = ''; readingKun.style.display = '';
    meaningArea.classList.remove('hidden');
    document.getElementById('btn-correct').style.visibility   = 'visible';
    document.getElementById('btn-incorrect').style.visibility = 'visible';
    const poolH = deck.filter((x,i) => i !== idx && x.meaning !== k.meaning);
    const showCorrect = poolH.length === 0 ? true : Math.random() > .45;
    currentIsCorrectMeaning = showCorrect;
    if (showCorrect) {
      shownMeaning.textContent = k.meaning;
      readingOn.textContent  = `On: ${k.on || '—'}`;
      readingKun.textContent = `Kun: ${k.kun || '—'}`;
    } else {
      const fake = poolH[Math.floor(Math.random() * poolH.length)];
      shownMeaning.textContent = fake.meaning;
      readingOn.textContent  = `On: ${k.on || '—'}`;
      readingKun.textContent = `Kun: ${k.kun || '—'}`;
    }
    verdictHint.style.display = 'block';
    verdictHint.textContent   = 'Nghĩa đúng hay sai? ⏱';
    const wordsHtmlH = filterWordsForLevel(k.words, selectedLevel).slice(0,3).map(w =>
      `<span class="back-word"><span class="bw-kanji">${w.w}</span><span class="bw-read">${w.r||''}</span><span class="bw-mean">${w.m||''}</span></span>`
    ).join('');
    backContent.innerHTML = `
      <div class="back-reading">
        <span class="back-on">On: ${k.on||'—'}</span>
        <span class="back-kun">Kun: ${k.kun||'—'}</span>
      </div>
      <div class="back-correct-meaning">${k.meaning}</div>
      ${wordsHtmlH ? `<div class="back-words">${wordsHtmlH}</div>` : ''}`;
    startTimer();
  }
}

function answer(userSaysCorrect) {
  if (isAnimating) return;
  if (Date.now() - cardShownTime < 500) return;
  isAnimating = true;
  stopTimer();
  const isRight = userSaysCorrect === currentIsCorrectMeaning;

  // ── Ghi nhận vào unified mastery store ──
  if (deck[idx] && window.koeruMastery) {
    window.koeruMastery.record(deck[idx].kanji, isRight, 'flash');
  }

  cardEl.classList.remove('flash-correct','flash-incorrect');
  const prevStreak = streak; // lưu trước khi reset — dùng cho modal
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
    setTimeout(() => { cardEl.classList.remove('flash-correct','flash-incorrect'); handleWrong(false, prevStreak); isAnimating = false; }, 500);
  } else {
    setTimeout(() => {
      cardEl.classList.remove('flash-correct','flash-incorrect');
      idx++; if (idx >= deck.length) showDone(); else renderCard();
      isAnimating = false;
    }, mode === 'easy' ? 600 : 400);
  }
}

// displayStreak: streak tại thời điểm mắc lỗi (trước khi bị reset về 0)
function handleWrong(isTimeout = false, displayStreak = streak) {
  stopTimer(); isAnimating = false;
  document.getElementById('modal-emoji').textContent  = isTimeout ? '⏱' : '💥';
  document.getElementById('modal-title').textContent  = isTimeout ? '⏱ Hết giờ!' : '💥 Sai rồi!';
  document.getElementById('modal-streak').textContent = `${displayStreak}`;
  document.getElementById('modal-detail').innerHTML =
    `Bạn đã đúng <strong style="color:#22c55e">${displayStreak}</strong> câu liên tiếp<br>
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
  // SRS: ưu tiên thẻ đến hạn ôn, sau đó mới random phần còn lại
  const allCards = getFilteredDeck();
  if (window.koeruMastery) {
    deck = window.koeruMastery.sortDeckByPriority(allCards);
  } else {
    deck = shuffle(allCards);
  }
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

// ── DOM init + event binding ──────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Assign DOM refs
  cardEl       = document.getElementById('card');
  kanjiEl      = document.getElementById('kanji');
  hanvietEl    = document.getElementById('han-viet');
  hardReadingEl= document.getElementById('hard-reading');
  shownMeaning = document.getElementById('shown-meaning');
  readingOn    = document.getElementById('reading-on');
  readingKun   = document.getElementById('reading-kun');
  verdictBadge = document.getElementById('verdict-badge');
  verdictHint  = document.getElementById('verdict-hint');
  meaningArea  = document.getElementById('meaning-area');
  backKanjiEl  = document.getElementById('back-kanji');
  backContent  = document.getElementById('back-content');
  progressText = document.getElementById('progress-text');
  progressBar  = document.getElementById('progress-bar');
  timerWrap    = document.getElementById('timer-wrap');
  timerBar     = document.getElementById('timer-bar');
  sCorrect     = document.getElementById('s-correct');
  sIncorrect   = document.getElementById('s-incorrect');
  feedbackEl   = document.getElementById('feedback');
  doneScreen   = document.getElementById('done-screen');
  streakBadge  = document.getElementById('streak-badge');
  instruction  = document.getElementById('instruction');
  kanjiArea    = document.getElementById('kanji-area');

  // Guard: không bind nếu đây không phải trang kanji.html
  if (!cardEl) return;

  // Mode buttons
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      mode = btn.dataset.mode;
      document.getElementById('timer-select-wrap').style.display = mode === 'hard' ? 'flex' : 'none';
      applyModeUI(); buildDeck();
    });
  });

  // Timer buttons
  document.querySelectorAll('.timer-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.timer-btn').forEach(b => b.classList.remove('active-timer'));
      btn.classList.add('active-timer');
      TIME_LIMIT = parseInt(btn.dataset.sec) * 1000;
      buildDeck();
    });
  });

  // Action buttons
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

  // Keyboard shortcuts
  document.addEventListener('keydown', e => {
    if (document.getElementById('flash-screen').classList.contains('active')) {
      if (e.key === 'ArrowLeft')  answer(true);
      if (e.key === 'ArrowRight') answer(false);
      if (e.key === ' ' || e.key === 'ArrowUp') { e.preventDefault(); flipCard(); }
    }
  });

  // Touch swipe on card
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
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) answer(dx < 0);
    else if (Math.abs(dx) < 10 && Math.abs(dy) < 10 && dt < 300) flipCard();
  }, { passive: true });
});

