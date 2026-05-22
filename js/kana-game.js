/* ════════════════════════════════
   KANA SPEED — Game Logic
   State · Home · Game Loop · Result
════════════════════════════════ */

/* ── State ── */
let selectedScript = 'hiragana';
let selectedLevel  = 1;
let queue          = [];
let currentIdx     = 0;
let currentItem    = null;
let correctAnswer  = '';
let choices        = [];
let scoreCorrect   = 0;
let scoreWrong     = 0;
let streak         = 0;
let maxStreak      = 0;
let missedItems    = [];
let answered       = false;
let timerInterval  = null;
let timerRemaining = 0;
let audioTimeout   = null;
let totalAnswered  = 0;
let uniqueWrongSet = new Set();
let lives          = 3;

const TIMER_SECS = 5;
const MAX_LIVES  = 3;

/* ── Screen switch ── */
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

/* ── Home ── */
function selectScript(s, btn) {
  selectedScript = s;
  document.querySelectorAll('.script-btn').forEach(b => b.classList.remove('active','active-h','active-k'));
  const cls = s === 'hiragana' ? 'active-h' : s === 'katakana' ? 'active-k' : 'active';
  btn.classList.add('active', cls);
  updateCounts();
}

function selectLevel(l) {
  selectedLevel = l;
  [1,2,3].forEach(n => document.getElementById('lvl'+n).classList.toggle('selected', l === n));
  const tabs = document.querySelector('.script-tabs');
  tabs.style.opacity      = l === 3 ? '.35' : '1';
  tabs.style.pointerEvents = l === 3 ? 'none' : '';
}

function getPool() {
  if (selectedLevel === 3) return VOCAB_MNN1;
  let pool = [];
  if (selectedScript === 'hiragana' || selectedScript === 'mixed') {
    pool = pool.concat(HIRAGANA_BASIC);
    if (selectedLevel === 2) pool = pool.concat(HIRAGANA_ADVANCED);
  }
  if (selectedScript === 'katakana' || selectedScript === 'mixed') {
    pool = pool.concat(KATAKANA_BASIC);
    if (selectedLevel === 2) pool = pool.concat(KATAKANA_ADVANCED);
  }
  return pool;
}

function updateCounts() {
  const base = selectedScript === 'mixed' ? 92 : 46;
  const adv  = selectedScript === 'mixed' ? 104 : 58;
  document.getElementById('count1').textContent = base;
  document.getElementById('count2').textContent = base + adv;
  document.getElementById('count3').textContent = VOCAB_MNN1.length + ' từ';
}

/* ── Game start ── */
function startGame() {
  const pool = getPool();
  queue = [...pool].sort(() => Math.random() - .5);

  scoreCorrect = 0; scoreWrong = 0; streak = 0; maxStreak = 0;
  missedItems = []; currentIdx = 0; answered = false;
  totalAnswered = 0; uniqueWrongSet = new Set();
  lives = MAX_LIVES;

  const label = selectedLevel === 3 ? 'Từ vựng MNN1'
    : selectedScript === 'hiragana' ? 'Hiragana'
    : selectedScript === 'katakana' ? 'Katakana' : 'Mixed';
  document.getElementById('g-title').textContent = `${label} · Trình độ ${selectedLevel}`;

  showScreen('game-screen');
  renderQuestion();
}

/* ── Render question ── */
function renderQuestion() {
  // Endless: tự nối thêm khi hết
  if (currentIdx >= queue.length) {
    queue = queue.concat([...getPool()].sort(() => Math.random() - .5));
  }

  answered    = false;
  currentItem = queue[currentIdx];
  correctAnswer = currentItem.r;

  const isVocab = selectedLevel === 3;
  const charEl  = document.getElementById('kana-char');
  const hintEl  = document.getElementById('vocab-hint');
  const badgeEl = document.getElementById('kana-type-badge');

  if (isVocab) {
    charEl.classList.add('vocab-mode');
    hintEl.style.display = 'block';
    hintEl.textContent   = currentItem.m || '';
    badgeEl.textContent  = 'TỪ VỰNG — MNN1';
  } else {
    charEl.classList.remove('vocab-mode');
    hintEl.style.display = 'none';
    badgeEl.textContent  = /[゠-ヿ]/.test(currentItem.k) ? 'KATAKANA' : 'HIRAGANA';
  }

  // Animate
  charEl.style.opacity = '0'; charEl.style.transform = 'scale(.7)';
  charEl.textContent = currentItem.k;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    charEl.style.transition = 'opacity .18s, transform .18s';
    charEl.style.opacity = '1'; charEl.style.transform = 'scale(1)';
    clearTimeout(audioTimeout);
    audioTimeout = setTimeout(() => playKanaAudio(currentItem.k), 2500);
  }));

  document.getElementById('g-progress-bar').style.width = '0%';
  document.getElementById('sc-correct').textContent     = scoreCorrect;
  document.getElementById('sc-lives').textContent       = '❤️'.repeat(lives) + '🖤'.repeat(MAX_LIVES - lives);
  document.getElementById('g-q-count').textContent      = `Câu ${totalAnswered + 1}`;

  const sb = document.getElementById('streak-badge');
  sb.style.display = streak >= 3 ? 'block' : 'none';
  if (streak >= 3) sb.textContent = `🔥 ${streak}`;

  // Build choices
  const pool = getPool();
  const wrongs = [...new Set(
    pool.filter(x => x.r !== correctAnswer)
        .sort(() => Math.random() - .5)
        .slice(0, 3)
        .map(x => x.r)
  )].slice(0, 3);
  while (wrongs.length < 3) wrongs.push('—');
  choices = [...wrongs, correctAnswer].sort(() => Math.random() - .5);

  for (let i = 0; i < 4; i++) {
    const btn = document.getElementById('ans' + i);
    btn.textContent = choices[i];
    btn.className   = 'ans-btn';
    btn.disabled    = false;
  }

  startTimer();
}

/* ── Timer ── */
function startTimer() {
  clearInterval(timerInterval);
  timerRemaining = TIMER_SECS;
  const bar = document.getElementById('g-timer-bar');
  bar.style.transition = 'none';
  bar.style.transform  = 'scaleX(1)';
  requestAnimationFrame(() => requestAnimationFrame(() => {
    bar.style.transition = `transform ${TIMER_SECS}s linear`;
    bar.style.transform  = 'scaleX(0)';
  }));
  timerInterval = setInterval(() => {
    if (--timerRemaining <= 0) { clearInterval(timerInterval); if (!answered) timeOut(); }
  }, 1000);
}

/* ── Answer handlers ── */
function answer(idx) {
  if (answered) return;
  answered = true;
  clearInterval(timerInterval);
  clearTimeout(audioTimeout);
  speechSynthesis.cancel();

  const btn    = document.getElementById('ans' + idx);
  const chosen = choices[idx];
  totalAnswered++;

  if (chosen === correctAnswer) {
    btn.classList.add('correct');
    scoreCorrect++;
    streak++;
    if (streak > maxStreak) maxStreak = streak;
    showFeedback('✅');
    setTimeout(nextQuestion, 600);
  } else {
    btn.classList.add('wrong');
    scoreWrong++;
    streak = 0;
    missedItems.push(currentItem);
    uniqueWrongSet.add(currentItem.k);
    queue.push(currentItem); // spaced repetition
    revealAnswer();
    showFeedback('❌');
    loseLife();
    if (lives > 0) setTimeout(nextQuestion, 1200);
  }
}

function timeOut() {
  answered = true;
  clearTimeout(audioTimeout);
  speechSynthesis.cancel();
  scoreWrong++;
  totalAnswered++;
  streak = 0;
  missedItems.push(currentItem);
  uniqueWrongSet.add(currentItem.k);
  revealAnswer();
  showFeedback('⏱️');
  loseLife();
  if (lives > 0) setTimeout(nextQuestion, 1200);
}

function loseLife() {
  lives--;
  if (lives <= 0) { revealAnswer(); showFeedback('💀'); setTimeout(showResult, 1200); }
}

function revealAnswer() {
  for (let i = 0; i < 4; i++) {
    const btn = document.getElementById('ans' + i);
    btn.disabled = true;
    if (choices[i] === correctAnswer) btn.classList.add('reveal');
  }
}

function nextQuestion() { currentIdx++; renderQuestion(); }

function showFeedback(emoji) {
  const el = document.getElementById('g-feedback');
  el.textContent = emoji;
  el.classList.remove('show');
  void el.offsetWidth;
  el.classList.add('show');
}

/* ── Result ── */
function showResult() {
  const total = scoreCorrect + scoreWrong;
  const acc   = total > 0 ? Math.round((scoreCorrect / total) * 100) : 0;

  document.getElementById('res-correct').textContent = scoreCorrect;
  document.getElementById('res-wrong').textContent   = uniqueWrongSet.size;
  document.getElementById('res-acc').textContent     = acc + '%';
  document.getElementById('res-streak').textContent  = maxStreak;

  const emoji = acc >= 90 ? '🏆' : acc >= 70 ? '🎉' : acc >= 50 ? '😊' : '📚';
  const title = acc >= 90 ? 'Xuất sắc!' : acc >= 70 ? 'Tốt lắm!' : acc >= 50 ? 'Khá ổn!' : 'Cần luyện thêm!';
  document.getElementById('res-emoji').textContent = emoji;
  document.getElementById('res-title').textContent = title;
  document.getElementById('res-sub').textContent   = `${totalAnswered} câu · ${scoreCorrect} đúng · ${uniqueWrongSet.size} từ cần ôn`;

  // Missed list
  const unique = [...new Map(missedItems.map(x => [x.k, x])).values()];
  const ms = document.getElementById('missed-section');
  const mg = document.getElementById('missed-grid');
  if (unique.length > 0) {
    ms.style.display = 'block';
    mg.innerHTML = unique.map(x =>
      `<div class="missed-chip"><span class="missed-kana">${x.k}</span><span class="missed-romaji">${x.r}</span></div>`
    ).join('');
  } else {
    ms.style.display = 'none';
  }

  // Save score (Supabase)
  scoreSaved = false;
  document.getElementById('save-score-section').classList.add('show');
  document.getElementById('save-status').textContent = '';
  document.getElementById('nickname-input').value    = localStorage.getItem('kana_nickname') || '';
  document.getElementById('save-btn').disabled       = false;

  showScreen('result-screen');
}

function restartGame() { startGame(); }

function goHome() {
  if (document.getElementById('game-screen').classList.contains('active') && totalAnswered > 0) {
    if (!confirm(`Bỏ qua? Bạn đã trả lời ${totalAnswered} câu (${scoreCorrect} đúng).`)) return;
  }
  clearInterval(timerInterval);
  clearTimeout(audioTimeout);
  speechSynthesis.cancel();
  showScreen('home-screen');
}

// Init counts on load
updateCounts();
