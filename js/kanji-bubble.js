// ══════════════════════════════════════════
// ══ GAME 3: BUBBLE MATCH ══
// ══════════════════════════════════════════

// ── XP / Level system ──
const XP_PER_CORRECT   = 10;
const XP_STREAK_BONUS  = 5;   // extra XP per streak level
const XP_PER_LEVEL     = 100;

let bXP = 0, bLevel = 1, bStreak = 0, bCorrect = 0, bTotal = 0;
let bRound = 0, bKanjiPerRound = 3;
let bSelectedBubble = null;
let bTimerHandle = null, bRoundTime = 30;
let bTimeLeft = 30;
let bAnswering = false;
let bCurrentPairs = []; // [{kanji, reading, meaning, distractors:[]}]

// Load XP from localStorage
function loadBubbleProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem('kanji_bubble_xp') || '{}');
    bXP    = saved.xp    || 0;
    bLevel = saved.level || 1;
  } catch(e) { bXP = 0; bLevel = 1; }
}
function saveBubbleProgress() {
  try { localStorage.setItem('kanji_bubble_xp', JSON.stringify({xp:bXP, level:bLevel})); } catch(e){}
}
function addXP(amount, anchorEl) {
  bXP += amount;
  while (bXP >= XP_PER_LEVEL) { bXP -= XP_PER_LEVEL; bLevel++; }
  saveBubbleProgress();
  updateBubbleHUD();
  if (anchorEl) {
    const rect = anchorEl.getBoundingClientRect();
    const el = document.createElement('div');
    el.className = 'xp-float';
    el.style.color = '#fbbf24';
    el.style.left  = (rect.left + rect.width/2 - 20) + 'px';
    el.style.top   = (rect.top - 10) + 'px';
    el.textContent = `+${amount} XP`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 900);
  }
}

function updateBubbleHUD() {
  document.getElementById('bub-level-badge').textContent = `Lv.${bLevel}`;
  document.getElementById('bub-xp-bar').style.width = `${(bXP / XP_PER_LEVEL) * 100}%`;
  document.getElementById('bub-xp-text').textContent  = `${bXP}/${XP_PER_LEVEL}`;
  document.getElementById('bub-streak').textContent   = bStreak;
  document.getElementById('bub-correct').textContent  = bCorrect;
  const acc = bTotal > 0 ? Math.round((bCorrect/bTotal)*100) + '%' : '—';
  document.getElementById('bub-accuracy').textContent = acc;
}

// ── Timer ──
function stopBubbleTimer() { clearInterval(bTimerHandle); bTimerHandle = null; }
function startBubbleTimer(seconds, onDone) {
  stopBubbleTimer();
  bTimeLeft = seconds;
  document.getElementById('bub-timer').textContent = bTimeLeft + 's';
  bTimerHandle = setInterval(() => {
    bTimeLeft--;
    document.getElementById('bub-timer').textContent = bTimeLeft + 's';
    if (bTimeLeft <= 0) { stopBubbleTimer(); onDone(); }
  }, 1000);
}

function stopBubble() {
  stopBubbleTimer();
  bSelectedBubble = null; bAnswering = false;
  document.getElementById('bub-arena').innerHTML = '';
  document.getElementById('bub-meanings').innerHTML = '';
}

// ── Build pairs for a round ──
function buildBubblePairs() {
  const pool = shuffle(getFilteredDeck());
  const count = Math.min(bKanjiPerRound, pool.length);
  const chosen = pool.slice(0, count);
  // Build distractors: pick wrong meanings from rest of pool
  const rest = pool.slice(count);
  bCurrentPairs = chosen.map(k => {
    const dists = shuffle(rest).slice(0, 3).map(d => d.meaning);
    return {
      kanji:   k.kanji,
      reading: k.on && k.on !== '—' ? k.on : k.kun,
      meaning: k.meaning,
      hanviet: k.hanviet,
      distractors: dists,
    };
  });
}

// ── Spawn bubbles in arena ──
function spawnBubbles() {
  const arena = document.getElementById('bub-arena');
  arena.innerHTML = '';
  const W = arena.clientWidth  || window.innerWidth;
  const H = arena.clientHeight || 200;
  const SIZE = Math.min(Math.max(Math.floor(W / (bCurrentPairs.length + 1.2)), 72), 110);

  // Place bubbles without overlap using a simple grid-scatter
  const positions = [];
  bCurrentPairs.forEach((pair, i) => {
    let x, y, tries = 0;
    do {
      x = SIZE/2 + Math.random() * (W - SIZE);
      y = SIZE/2 + Math.random() * (H - SIZE);
      tries++;
    } while(tries < 40 && positions.some(p => Math.hypot(p.x-x, p.y-y) < SIZE * 1.1));
    positions.push({x, y});

    const el = document.createElement('div');
    el.className = 'bub-kanji';
    el.dataset.idx = i;
    el.style.width  = SIZE + 'px';
    el.style.height = SIZE + 'px';
    el.style.left   = (x - SIZE/2) + 'px';
    el.style.top    = (y - SIZE/2) + 'px';
    el.style.animationDuration = (3 + Math.random() * 3) + 's';
    el.style.animationDelay    = (-Math.random() * 3) + 's';
    el.style.animation = `bubbleSpawn .4s ease ${i*0.08}s both, bubbleFloat ${3+Math.random()*3}s ease-in-out ${-Math.random()*3}s infinite`;
    el.innerHTML = `<div class="bub-k-text">${pair.kanji}</div><div class="bub-k-read">${pair.reading || ''}</div>`;
    el.addEventListener('click', () => onBubbleTap(el, i));
    arena.appendChild(el);
  });
}

// ── Render meaning choices ──
function renderMeanings(activePairIdx) {
  const meanings = document.getElementById('bub-meanings');
  meanings.innerHTML = '';
  const pair = bCurrentPairs[activePairIdx];
  // Mix correct + distractors + distractors from other pairs
  const otherMeanings = bCurrentPairs
    .filter((_,i) => i !== activePairIdx)
    .map(p => p.meaning);
  const allWrong = shuffle([...pair.distractors, ...otherMeanings]).slice(0, 3);
  const options  = shuffle([pair.meaning, ...allWrong]);

  // 2-column grid for ≤4 options
  meanings.style.gridTemplateColumns = options.length <= 2 ? '1fr' : '1fr 1fr';

  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'bub-meaning-btn';
    btn.textContent = opt;
    btn.addEventListener('click', () => onMeaningTap(btn, opt, pair, activePairIdx));
    meanings.appendChild(btn);
  });
}

// ── Tap bubble ──
function onBubbleTap(el, idx) {
  if (bAnswering) return;
  // Deselect previous
  document.querySelectorAll('.bub-kanji.selected').forEach(b => b.classList.remove('selected'));
  document.querySelectorAll('.bub-meaning-btn').forEach(b => {
    b.classList.remove('selected-ans','correct-ans','wrong-ans');
  });
  bSelectedBubble = { el, idx };
  el.classList.add('selected');
  renderMeanings(idx);
  stopBubbleTimer();
  startBubbleTimer(bRoundTime, () => {
    // Time out on this bubble
    bStreak = 0; bTotal++;
    el.classList.remove('selected');
    el.classList.add('wrong-flash');
    playTone(180, 'sawtooth', 0.15);
    updateBubbleHUD();
    setTimeout(() => {
      el.classList.remove('wrong-flash');
      bAnswering = false;
      checkRoundComplete();
    }, 500);
  });
}

// ── Tap meaning ──
function onMeaningTap(btn, chosen, pair, pairIdx) {
  if (bAnswering || !bSelectedBubble || bSelectedBubble.idx !== pairIdx) return;
  bAnswering = true;
  stopBubbleTimer();
  bTotal++;

  const isCorrect = (chosen === pair.meaning);
  const bubbleEl  = bSelectedBubble.el;
  bSelectedBubble = null;

  if (isCorrect) {
    bCorrect++; bStreak++;
    const xpGain = XP_PER_CORRECT + Math.min(bStreak - 1, 5) * XP_STREAK_BONUS;
    btn.classList.add('correct-ans');
    bubbleEl.classList.remove('selected');
    bubbleEl.classList.add('correct-flash');
    playTone(880, 'sine', 0.12);
    addXP(xpGain, bubbleEl);
    setTimeout(() => {
      bubbleEl.remove();
      document.getElementById('bub-meanings').innerHTML = '';
      bAnswering = false;
      checkRoundComplete();
    }, 500);
  } else {
    bStreak = 0;
    btn.classList.add('wrong-ans');
    bubbleEl.classList.remove('selected');
    bubbleEl.classList.add('wrong-flash');
    playTone(200, 'sawtooth', 0.15);
    updateBubbleHUD();
    setTimeout(() => {
      btn.classList.remove('wrong-ans');
      bubbleEl.classList.remove('wrong-flash');
      bAnswering = false;
      // Keep bubble alive, player retries
    }, 400);
  }
  updateBubbleHUD();
}

// ── Check if round done ──
function checkRoundComplete() {
  const remaining = document.querySelectorAll('#bub-arena .bub-kanji').length;
  if (remaining === 0) {
    stopBubbleTimer();
    bRound++;
    // Increase difficulty
    if (bRound % 2 === 0) bKanjiPerRound = Math.min(bKanjiPerRound + 1, 6);
    if (bRound % 3 === 0) bRoundTime = Math.max(bRoundTime - 2, 12);
    showBubbleRoundResult();
  }
}

function showBubbleRoundResult() {
  const acc = bTotal > 0 ? Math.round((bCorrect/bTotal)*100) : 0;
  const emoji = acc >= 90 ? '🔥' : acc >= 70 ? '✨' : '💪';
  document.getElementById('bub-overlay-emoji').textContent = emoji;
  document.getElementById('bub-overlay-title').textContent = `Vòng ${bRound} xong!`;
  document.getElementById('bub-overlay-detail').innerHTML =
    `🎯 Accuracy: <strong style="color:#22c55e">${acc}%</strong><br>
     🔥 Streak: <strong style="color:#fb923c">${bStreak}</strong><br>
     ✨ XP: <strong style="color:#fbbf24">${bXP}/${XP_PER_LEVEL}</strong> · Lv.${bLevel}<br>
     <small style="opacity:.6">Vòng tiếp: ${bKanjiPerRound} kanji · ${bRoundTime}s</small>`;
  document.getElementById('bub-overlay').classList.add('visible');
}

function nextBubbleRound() {
  bAnswering = false; bSelectedBubble = null;
  document.getElementById('bub-meanings').innerHTML = '';
  buildBubblePairs();
  spawnBubbles();
  document.getElementById('bub-timer').textContent = '—';
}

function startBubbleGame() {
  loadBubbleProgress();
  bStreak = 0; bCorrect = 0; bTotal = 0; bRound = 0;
  bKanjiPerRound = 3; bRoundTime = 30;
  bSelectedBubble = null; bAnswering = false;
  document.getElementById('bub-overlay').classList.remove('visible');
  document.getElementById('bub-meanings').innerHTML = '';
  updateBubbleHUD();
  buildBubblePairs();
  // Wait for screen to be visible so dimensions are correct
  requestAnimationFrame(() => requestAnimationFrame(() => spawnBubbles()));
}

