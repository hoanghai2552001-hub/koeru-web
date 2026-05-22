// ══════════════════════════════════════════
// ══ GAME 3: BUBBLE — On/Kun Reading ══
// ══════════════════════════════════════════

// ── Constants ──
const XP_PER_CORRECT  = 10;
const XP_STREAK_BONUS = 5;
const XP_PER_LEVEL    = 100;
const DAILY_GOAL      = 10;
const MASTERY_MAX     = 5;

// ── State ──
let bXP = 0, bLevel = 1, bStreak = 0, bCorrect = 0, bTotal = 0;
let bRound = 0, bKanjiPerRound = 3;
let bSelectedBubble = null;
let bTimerHandle = null, bRoundTime = 30;
let bTimeLeft = 30;
let bAnswering = false;
let bCurrentPairs  = [];
let bWrongThisRound = [];  // [{kanji, correctReading, readingType, meaning}]

// ══════════════════════════════════════════
// MASTERY per kanji (localStorage)
// ══════════════════════════════════════════
let masteryData = {};  // { '食': { m: 0-5, seen: timestamp } }

function loadMastery() {
  try { masteryData = JSON.parse(localStorage.getItem('bubble_mastery') || '{}'); }
  catch(e) { masteryData = {}; }
}
function saveMastery() {
  try { localStorage.setItem('bubble_mastery', JSON.stringify(masteryData)); } catch(e){}
}
function getMastery(kanji) { return masteryData[kanji]?.m ?? 0; }
function updateMastery(kanji, correct) {
  if (!masteryData[kanji]) masteryData[kanji] = { m: 0 };
  masteryData[kanji].m = correct
    ? Math.min(MASTERY_MAX, masteryData[kanji].m + 1)
    : Math.max(0, masteryData[kanji].m - 1);
  masteryData[kanji].seen = Date.now();
  saveMastery();
}

// ══════════════════════════════════════════
// DAILY GOAL & STREAK
// ══════════════════════════════════════════
let dailyData = { date: '', count: 0, streak: 0 };

function loadDaily() {
  try { dailyData = { date:'', count:0, streak:0, ...JSON.parse(localStorage.getItem('bubble_daily') || '{}') }; }
  catch(e) { dailyData = { date:'', count:0, streak:0 }; }
}
function saveDaily() {
  try { localStorage.setItem('bubble_daily', JSON.stringify(dailyData)); } catch(e){}
}
function checkAndResetDaily() {
  const today     = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();
  if (dailyData.date === today) return;
  // Kept streak nếu hoàn thành goal hôm qua
  if (dailyData.date === yesterday && dailyData.count >= DAILY_GOAL) {
    dailyData.streak = (dailyData.streak || 0) + 1;
  } else if (dailyData.date !== today) {
    dailyData.streak = 0;
  }
  dailyData.date  = today;
  dailyData.count = 0;
  saveDaily();
}
function incrementDaily() {
  dailyData.count++;
  saveDaily();
  updateDailyWidget();
  if (dailyData.count === DAILY_GOAL) showGoalComplete();
}
function updateDailyWidget() {
  const pct = Math.min(100, (dailyData.count / DAILY_GOAL) * 100);
  const bar  = document.getElementById('bub-daily-bar');
  const txt  = document.getElementById('bub-daily-text');
  const str  = document.getElementById('bub-daily-streak');
  if (bar) bar.style.width  = pct + '%';
  if (txt) txt.textContent  = `${dailyData.count}/${DAILY_GOAL}`;
  if (str) str.textContent  = `🔥${dailyData.streak}`;
}
function showGoalComplete() {
  const wrap = document.getElementById('bub-daily-wrap');
  if (!wrap) return;
  wrap.classList.add('goal-done');
  setTimeout(() => wrap.classList.remove('goal-done'), 2500);
}

// ══════════════════════════════════════════
// XP / LEVEL
// ══════════════════════════════════════════
function loadBubbleProgress() {
  try {
    const d = JSON.parse(localStorage.getItem('kanji_bubble_xp') || '{}');
    bXP = d.xp || 0; bLevel = d.level || 1;
  } catch(e) { bXP = 0; bLevel = 1; }
}
function saveBubbleProgress() {
  try { localStorage.setItem('kanji_bubble_xp', JSON.stringify({ xp:bXP, level:bLevel })); } catch(e){}
}
function addXP(amount, anchorEl) {
  bXP += amount;
  while (bXP >= XP_PER_LEVEL) { bXP -= XP_PER_LEVEL; bLevel++; }
  saveBubbleProgress();
  updateBubbleHUD();
  if (anchorEl) {
    const rect = anchorEl.getBoundingClientRect();
    const el   = document.createElement('div');
    el.className = 'xp-float';
    el.style.cssText = `color:#fbbf24;left:${rect.left + rect.width/2 - 20}px;top:${rect.top - 10}px;`;
    el.textContent   = `+${amount} XP`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 900);
  }
}
function updateBubbleHUD() {
  document.getElementById('bub-level-badge').textContent = `Lv.${bLevel}`;
  document.getElementById('bub-xp-bar').style.width      = `${(bXP / XP_PER_LEVEL) * 100}%`;
  document.getElementById('bub-xp-text').textContent     = `${bXP}/${XP_PER_LEVEL}`;
  document.getElementById('bub-streak').textContent      = bStreak;
  document.getElementById('bub-correct').textContent     = bCorrect;
  const acc = bTotal > 0 ? Math.round((bCorrect/bTotal)*100) + '%' : '—';
  document.getElementById('bub-accuracy').textContent = acc;
}

// ══════════════════════════════════════════
// TIMER
// ══════════════════════════════════════════
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

// ══════════════════════════════════════════
// AUDIO — Web Speech API (Japanese)
// ══════════════════════════════════════════
function speakJP(text) {
  if (!window.speechSynthesis) return;
  speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang  = 'ja-JP';
  utter.rate  = 0.85;
  utter.pitch = 1.0;
  const speak = () => {
    const voices   = speechSynthesis.getVoices().filter(v => v.lang === 'ja-JP');
    const prefNames = ['Haruka','Sayaka','Ayumi','Ichiro'];
    let picked = null;
    for (const n of prefNames) { picked = voices.find(v => v.name.includes(n)); if (picked) break; }
    if (!picked && voices.length) picked = voices[0];
    if (picked) utter.voice = picked;
    setTimeout(() => speechSynthesis.speak(utter), 50);
  };
  if (speechSynthesis.getVoices().length) speak();
  else speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
}

// ══════════════════════════════════════════
// SRS POOL — ưu tiên mastery thấp
// ══════════════════════════════════════════
function getWeightedPool() {
  const deck = getFilteredDeck();
  const shuffled = shuffle([...deck]);
  return shuffled.sort((a, b) => getMastery(a.kanji) - getMastery(b.kanji));
}

// ══════════════════════════════════════════
// READING HELPERS
// ══════════════════════════════════════════
function getReadingsForKanji(k) {
  const ons  = (k.on  && k.on  !== '—') ? k.on.split('、').map(r => r.trim()).filter(Boolean) : [];
  const kuns = (k.kun && k.kun !== '—')
    ? k.kun.split('、').map(r => r.replace(/[（）()]/g, '').trim()).filter(Boolean)
    : [];
  return { ons, kuns, all: [...ons, ...kuns] };
}
function getTargetReading(k) {
  const { ons, kuns, all } = getReadingsForKanji(k);
  if (ons.length)  return { reading: ons[0],  type: 'on',  valid: ons };
  if (kuns.length) return { reading: kuns[0], type: 'kun', valid: kuns };
  // fallback — dùng on field raw
  const raw = k.on !== '—' ? k.on : k.kun;
  return { reading: raw, type: 'on', valid: [raw] };
}

// ══════════════════════════════════════════
// BUILD PAIRS
// ══════════════════════════════════════════
const PADDING_READINGS = ['ざい','ろく','てん','きく','もの','はな','さく','ふじ','なみ','いわ'];
function buildBubblePairs() {
  const pool   = getWeightedPool();
  const count  = Math.min(bKanjiPerRound, pool.length);
  const chosen = pool.slice(0, count);
  const rest   = shuffle(pool.slice(count));

  bCurrentPairs = chosen.map(k => {
    const { reading, type, valid } = getTargetReading(k);

    // Distractors: đọc thật của kanji khác, không trùng valid
    const dists = [];
    for (const d of rest) {
      const { all } = getReadingsForKanji(d);
      for (const r of all) {
        if (!valid.includes(r) && !dists.includes(r)) { dists.push(r); break; }
      }
      if (dists.length >= 3) break;
    }
    // Pad nếu thiếu
    let pi = 0;
    while (dists.length < 3) {
      const p = PADDING_READINGS[pi++ % PADDING_READINGS.length];
      if (!dists.includes(p) && !valid.includes(p)) dists.push(p);
    }
    return {
      kanji:          k.kanji,
      hanviet:        k.hanviet,
      meaning:        k.meaning,
      correctReading: reading,
      validReadings:  valid,
      readingType:    type,
      distractors:    dists.slice(0, 3),
    };
  });
}

// ══════════════════════════════════════════
// SPAWN BUBBLES
// ══════════════════════════════════════════
function spawnBubbles() {
  const arena = document.getElementById('bub-arena');
  arena.innerHTML = '';
  const W    = arena.clientWidth  || window.innerWidth;
  const H    = arena.clientHeight || 200;
  const SIZE = Math.min(Math.max(Math.floor(W / (bCurrentPairs.length + 1.2)), 76), 116);

  const positions = [];
  bCurrentPairs.forEach((pair, i) => {
    let x, y, tries = 0;
    do {
      x = SIZE/2 + Math.random() * (W - SIZE);
      y = SIZE/2 + Math.random() * (H - SIZE);
      tries++;
    } while(tries < 40 && positions.some(p => Math.hypot(p.x - x, p.y - y) < SIZE * 1.1));
    positions.push({ x, y });

    // Mastery stars
    const m     = getMastery(pair.kanji);
    const stars = '★'.repeat(m) + '☆'.repeat(MASTERY_MAX - m);

    const el = document.createElement('div');
    el.className   = 'bub-kanji';
    el.dataset.idx = i;
    el.style.width  = SIZE + 'px';
    el.style.height = SIZE + 'px';
    el.style.left   = (x - SIZE/2) + 'px';
    el.style.top    = (y - SIZE/2) + 'px';
    el.style.animation = `bubbleSpawn .4s ease ${i*0.08}s both, bubbleFloat ${3+Math.random()*3}s ease-in-out ${-Math.random()*3}s infinite`;
    el.innerHTML = `
      <div class="bub-k-text">${pair.kanji}</div>
      <div class="bub-k-hanviet">${pair.hanviet}</div>
      <div class="bub-k-stars">${stars}</div>`;
    el.addEventListener('click', () => onBubbleTap(el, i));
    arena.appendChild(el);
  });
}

// ══════════════════════════════════════════
// RENDER READING OPTIONS
// ══════════════════════════════════════════
function renderReadings(pairIdx) {
  const panel = document.getElementById('bub-meanings');
  const pair  = bCurrentPairs[pairIdx];
  const opts  = shuffle([pair.correctReading, ...pair.distractors]);

  panel.innerHTML = `
    <div id="bub-question-label">
      <div id="bub-q-left">
        <span class="bub-q-kanji">${pair.kanji}</span>
        <span class="bub-q-hanviet">${pair.hanviet}</span>
      </div>
      <div id="bub-q-right">
        <span class="bub-q-meaning">${pair.meaning}</span>
        <span class="bub-reading-badge ${pair.readingType === 'on' ? 'badge-on' : 'badge-kun'}">
          ${pair.readingType === 'on' ? '音読み' : '訓読み'}
        </span>
      </div>
    </div>
    <div id="bub-options-grid"></div>`;

  const grid = document.getElementById('bub-options-grid');
  opts.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'bub-meaning-btn';
    btn.innerHTML = `<span class="bub-opt-kana">${opt}</span>`;
    btn.addEventListener('click', () => onReadingTap(btn, opt, pair, pairIdx));
    btn.addEventListener('mouseenter', () => speakJP(opt));
    grid.appendChild(btn);
  });
}

// ══════════════════════════════════════════
// TAP BUBBLE
// ══════════════════════════════════════════
function onBubbleTap(el, idx) {
  if (bAnswering) return;
  document.querySelectorAll('.bub-kanji.selected').forEach(b => b.classList.remove('selected'));
  bSelectedBubble = { el, idx };
  el.classList.add('selected');
  speakJP(bCurrentPairs[idx].kanji);
  renderReadings(idx);
  stopBubbleTimer();
  startBubbleTimer(bRoundTime, () => {
    // Hết giờ = sai
    bAnswering = true; // Khóa tương tác trong lúc chạy animation
    bStreak = 0; bTotal++;
    const pair = bCurrentPairs[idx];
    updateMastery(pair.kanji, false);
    if (!bWrongThisRound.find(w => w.kanji === pair.kanji)) bWrongThisRound.push(pair);
    el.classList.remove('selected');
    el.classList.add('wrong-flash');
    speakJP(pair.correctReading);
    playTone(180, 'sawtooth', 0.15);
    updateBubbleHUD();
    bSelectedBubble = null;
    setTimeout(() => {
      el.classList.remove('wrong-flash');
      document.getElementById('bub-meanings').innerHTML = ''; // Xóa bảng đáp án
      bAnswering = false;
      checkRoundComplete();
    }, 600);
  });
}

// ══════════════════════════════════════════
// TAP READING OPTION
// ══════════════════════════════════════════
function onReadingTap(btn, chosen, pair, pairIdx) {
  if (bAnswering || !bSelectedBubble || bSelectedBubble.idx !== pairIdx) return;
  bAnswering = true;
  stopBubbleTimer();
  bTotal++;

  const isCorrect = chosen === pair.correctReading;
  const isPartial = !isCorrect && pair.validReadings.includes(chosen);
  const bubbleEl  = bSelectedBubble.el;
  bSelectedBubble = null;

  if (isCorrect || isPartial) {
    bCorrect++; bStreak++;
    updateMastery(pair.kanji, true);
    incrementDaily();
    const xpGain = isCorrect
      ? XP_PER_CORRECT + Math.min(bStreak - 1, 5) * XP_STREAK_BONUS
      : Math.floor(XP_PER_CORRECT / 2);
    btn.classList.add('correct-ans');
    bubbleEl.classList.remove('selected');
    bubbleEl.classList.add('correct-flash');
    speakJP(pair.correctReading);
    playTone(880, 'sine', 0.12);
    addXP(xpGain, bubbleEl);

    if (isPartial) {
      // Hiện đáp án chính xác nhất
      const note = document.createElement('div');
      note.className = 'bub-partial-note';
      note.textContent = `★ ${pair.correctReading}`;
      bubbleEl.appendChild(note);
    }
    setTimeout(() => {
      bubbleEl.remove();
      document.getElementById('bub-meanings').innerHTML = '';
      bAnswering = false;
      checkRoundComplete();
    }, isPartial ? 900 : 500);

  } else {
    // Sai
    bStreak = 0;
    updateMastery(pair.kanji, false);
    if (!bWrongThisRound.find(w => w.kanji === pair.kanji)) bWrongThisRound.push(pair);
    btn.classList.add('wrong-ans');
    bubbleEl.classList.remove('selected');
    bubbleEl.classList.add('wrong-flash');
    speakJP(pair.correctReading);
    playTone(200, 'sawtooth', 0.15);
    // Highlight đáp án đúng
    document.querySelectorAll('#bub-options-grid .bub-meaning-btn').forEach(b => {
      if (b.querySelector('.bub-opt-kana')?.textContent === pair.correctReading) {
        b.classList.add('correct-ans');
      }
    });
    updateBubbleHUD();
    setTimeout(() => {
      btn.classList.remove('wrong-ans');
      bubbleEl.classList.remove('wrong-flash');
      document.getElementById('bub-meanings').innerHTML = ''; // Xóa bảng đáp án để không bị đơ giao diện
      bAnswering = false;
    }, 900);
  }
  updateBubbleHUD();
}

// ══════════════════════════════════════════
// ROUND COMPLETE
// ══════════════════════════════════════════
function checkRoundComplete() {
  if (document.querySelectorAll('#bub-arena .bub-kanji').length === 0) {
    stopBubbleTimer();
    bRound++;
    if (bRound % 2 === 0) bKanjiPerRound = Math.min(bKanjiPerRound + 1, 6);
    if (bRound % 3 === 0) bRoundTime = Math.max(bRoundTime - 2, 12);
    showBubbleRoundResult();
  }
}

function showBubbleRoundResult() {
  const acc   = bTotal > 0 ? Math.round((bCorrect/bTotal)*100) : 0;
  const emoji = acc >= 90 ? '🔥' : acc >= 70 ? '✨' : '💪';
  const pct   = Math.min(100, (dailyData.count / DAILY_GOAL) * 100);

  // Review list
  let reviewHtml = '';
  if (bWrongThisRound.length > 0) {
    reviewHtml = `<div class="bub-review-title">📖 Cần ôn lại</div>
      <div class="bub-review-list">` +
      bWrongThisRound.map(p =>
        `<div class="bub-review-item" onclick="speakJP('${p.correctReading}')">
           <span class="bub-rev-kanji">${p.kanji}</span>
           <span class="bub-rev-arrow">→</span>
           <span class="bub-rev-reading">${p.correctReading}</span>
           <span class="bub-rev-badge ${p.readingType === 'on' ? 'badge-on' : 'badge-kun'}">${p.readingType === 'on' ? '音' : '訓'}</span>
           <span class="bub-rev-meaning">${p.meaning}</span>
         </div>`
      ).join('') +
      `</div>`;
  }

  document.getElementById('bub-overlay-emoji').textContent = emoji;
  document.getElementById('bub-overlay-title').textContent = `Vòng ${bRound} xong!`;
  document.getElementById('bub-overlay-detail').innerHTML = `
    <div class="bub-ov-stats">
      🎯 <strong style="color:#22c55e">${acc}%</strong> &nbsp;
      🔥 Streak <strong style="color:#fb923c">${bStreak}</strong> &nbsp;
      ✨ Lv.<strong style="color:#fbbf24">${bLevel}</strong>
    </div>
    <div class="bub-dp-wrap">
      <div class="bub-dp-label">📅 Hôm nay: <strong>${dailyData.count}/${DAILY_GOAL}</strong> kanji · 🔥${dailyData.streak} ngày liên tiếp</div>
      <div class="bub-dp-bar-wrap"><div class="bub-dp-bar" style="width:${pct}%"></div></div>
    </div>
    ${reviewHtml}
    <small style="opacity:.45;display:block;margin-top:8px">Vòng tiếp: ${bKanjiPerRound} kanji · ${bRoundTime}s</small>`;

  document.getElementById('bub-overlay').classList.add('visible');
  bWrongThisRound = [];
}

function nextBubbleRound() {
  bAnswering = false; bSelectedBubble = null;
  document.getElementById('bub-meanings').innerHTML = '';
  document.getElementById('bub-overlay').classList.remove('visible');
  buildBubblePairs();
  spawnBubbles();
  document.getElementById('bub-timer').textContent = '—';
}

function startBubbleGame() {
  loadBubbleProgress();
  loadMastery();
  loadDaily();
  checkAndResetDaily();
  bStreak = 0; bCorrect = 0; bTotal = 0; bRound = 0;
  bKanjiPerRound = 3; bRoundTime = 30;
  bSelectedBubble = null; bAnswering = false;
  bWrongThisRound = [];
  document.getElementById('bub-overlay').classList.remove('visible');
  document.getElementById('bub-meanings').innerHTML = '';
  updateBubbleHUD();
  updateDailyWidget();
  buildBubblePairs();
  requestAnimationFrame(() => requestAnimationFrame(() => spawnBubbles()));
}
