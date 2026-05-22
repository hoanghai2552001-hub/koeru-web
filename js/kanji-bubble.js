// ══════════════════════════════════════════
// ══ GAME 3: KANJI DUNGEON ══
// Luyện âm On/Kun theo cơ chế RPG
// ══════════════════════════════════════════

// ── Constants ──
const XP_PER_CORRECT   = 10;
const XP_STREAK_BONUS  = 5;
const XP_PER_LEVEL     = 100;
const DAILY_GOAL       = 3;   // tầng/ngày
const MASTERY_MAX      = 5;
const HERO_MAX_HP      = 3;
const ENEMIES_PER_FLOOR = 10;
const BOSS_EVERY       = 5;   // boss mỗi N tầng
const ANSWER_TIME      = 8;   // giây mỗi câu

// ── Floor themes ──
const FLOOR_THEMES = [
  { range:[1,5],   sprite:'🐸', name:'Ếch Yêu Tinh', bg:'#061a0e', accent:'#4ade80' },
  { range:[6,10],  sprite:'🦊', name:'Cáo Thần',      bg:'#1a0e06', accent:'#fb923c' },
  { range:[11,15], sprite:'👺', name:'Quỷ Oni',        bg:'#1a0612', accent:'#f472b6' },
  { range:[16,20], sprite:'🐉', name:'Rồng Xanh',     bg:'#060e1a', accent:'#60a5fa' },
  { range:[21,99], sprite:'👾', name:'Ma Vương',       bg:'#0e061a', accent:'#a78bfa' },
];
const BOSS_THEME = { sprite:'👹', name:'⚠️ BOSS', bg:'#1a0606', accent:'#ef4444' };

// ── State ──
let dFloor = 1;
let dEnemyIdx = 0;
let dHeroHP = HERO_MAX_HP;
let dStreak = 0, dCorrect = 0, dTotal = 0;
let dXP = 0, dLevel = 1;
let dTimerHandle = null, dTimeLeft = ANSWER_TIME;
let dAnswering = false;
let dCurrentCard = null;
let dPool = [], dUsedIdx = new Set();

// ══════════════════════════════════════════
// MASTERY (localStorage per kanji)
// ══════════════════════════════════════════
let masteryData = {};
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
// DAILY GOAL (3 tầng/ngày)
// ══════════════════════════════════════════
let dailyData = { date: '', floors: 0, streak: 0 };
function loadDaily() {
  try {
    dailyData = { date:'', floors:0, streak:0,
      ...JSON.parse(localStorage.getItem('dng_daily') || '{}') };
  } catch(e) {}
}
function saveDaily() {
  try { localStorage.setItem('dng_daily', JSON.stringify(dailyData)); } catch(e){}
}
function checkAndResetDaily() {
  const today     = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();
  if (dailyData.date === today) return;
  if (dailyData.date === yesterday && dailyData.floors >= DAILY_GOAL)
    dailyData.streak = (dailyData.streak || 0) + 1;
  else
    dailyData.streak = 0;
  dailyData.date   = today;
  dailyData.floors = 0;
  saveDaily();
}
function incrementDailyFloor() {
  dailyData.floors++;
  saveDaily();
  if (dailyData.floors === DAILY_GOAL) flashDailyGoal();
}
function flashDailyGoal() {
  const el = document.getElementById('dng-daily-text');
  if (!el) return;
  el.style.color = '#4ade80';
  el.textContent = `🎉 Mục tiêu hôm nay hoàn thành! 🔥${dailyData.streak} ngày`;
  setTimeout(() => updateDngHUD(), 3000);
}

// ══════════════════════════════════════════
// FLOOR PROGRESS (persistent)
// ══════════════════════════════════════════
let dProgress = { maxFloor: 1 };
function loadProgress() {
  try { dProgress = { maxFloor:1, ...JSON.parse(localStorage.getItem('dng_progress') || '{}') }; }
  catch(e) {}
}
function saveProgress() {
  try { localStorage.setItem('dng_progress', JSON.stringify(dProgress)); } catch(e){}
}

// ══════════════════════════════════════════
// XP / LEVEL
// ══════════════════════════════════════════
function loadDungeonXP() {
  try {
    const d = JSON.parse(localStorage.getItem('dng_xp') || '{}');
    dXP = d.xp || 0; dLevel = d.level || 1;
  } catch(e) {}
}
function saveDungeonXP() {
  try { localStorage.setItem('dng_xp', JSON.stringify({ xp:dXP, level:dLevel })); } catch(e){}
}
function addDungeonXP(amount, anchorEl) {
  dXP += amount;
  while (dXP >= XP_PER_LEVEL) { dXP -= XP_PER_LEVEL; dLevel++; }
  saveDungeonXP();
  updateDngHUD();
  if (!anchorEl) return;
  const rect = anchorEl.getBoundingClientRect();
  const el   = document.createElement('div');
  el.className = 'xp-float';
  el.style.cssText = `color:#fbbf24;left:${rect.left+rect.width/2-20}px;top:${rect.top-10}px;`;
  el.textContent   = `+${amount} XP`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 900);
}

// ══════════════════════════════════════════
// HUD
// ══════════════════════════════════════════
function updateDngHUD() {
  const $ = id => document.getElementById(id);
  $('dng-floor-num').textContent   = `Tầng ${dFloor}`;
  $('dng-lv-badge').textContent    = `Lv.${dLevel}`;
  $('dng-xp-bar').style.width      = `${(dXP / XP_PER_LEVEL) * 100}%`;
  $('dng-streak-val').textContent  = dStreak;
  $('dng-correct-val').textContent = dCorrect;
  // Hero HP
  const hp = $('dng-hero-hp');
  if (hp) hp.innerHTML =
    '❤️'.repeat(dHeroHP) +
    '<span style="opacity:.25;filter:grayscale(1)">❤️</span>'.repeat(HERO_MAX_HP - dHeroHP);
  // Daily bar
  const pct = Math.min(100, (dailyData.floors / DAILY_GOAL) * 100);
  const bar = $('dng-daily-bar');
  if (bar) bar.style.width = pct + '%';
  $('dng-daily-text').textContent =
    `📅 ${dailyData.floors}/${DAILY_GOAL} tầng · 🔥${dailyData.streak} ngày`;
}

// ══════════════════════════════════════════
// AUDIO
// ══════════════════════════════════════════
function speakJP(text) {
  if (!window.speechSynthesis) return;
  speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'ja-JP'; utter.rate = 0.85; utter.pitch = 1.0;
  const speak = () => {
    const voices = speechSynthesis.getVoices().filter(v => v.lang === 'ja-JP');
    const pref   = ['Haruka','Sayaka','Ayumi','Ichiro'];
    let picked   = null;
    for (const n of pref) { picked = voices.find(v => v.name.includes(n)); if (picked) break; }
    if (!picked && voices.length) picked = voices[0];
    if (picked) utter.voice = picked;
    setTimeout(() => speechSynthesis.speak(utter), 50);
  };
  if (speechSynthesis.getVoices().length) speak();
  else speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
}

// ══════════════════════════════════════════
// READING HELPERS
// ══════════════════════════════════════════
function getReadingsForKanji(k) {
  const ons  = (k.on  && k.on  !== '—')
    ? k.on.split('、').map(r => r.trim()).filter(Boolean) : [];
  const kuns = (k.kun && k.kun !== '—')
    ? k.kun.split('、').map(r => r.replace(/[（）()]/g,'').trim()).filter(Boolean) : [];
  return { ons, kuns, all: [...ons, ...kuns] };
}
function getTargetReading(k) {
  const { ons, kuns } = getReadingsForKanji(k);
  if (ons.length)  return { reading: ons[0],  type: 'on',  valid: ons };
  if (kuns.length) return { reading: kuns[0], type: 'kun', valid: kuns };
  const raw = k.on !== '—' ? k.on : k.kun;
  return { reading: raw, type: 'on', valid: [raw] };
}

// ══════════════════════════════════════════
// SRS POOL
// ══════════════════════════════════════════
function getWeightedPool() {
  return shuffle([...getFilteredDeck()])
    .sort((a, b) => getMastery(a.kanji) - getMastery(b.kanji));
}

// ══════════════════════════════════════════
// BUILD CARD
// ══════════════════════════════════════════
const PAD_READINGS = ['ざい','ろく','てん','きく','もの','はな','さく','ふじ','なみ','いわ'];
function buildCard() {
  // Find next unused kanji from pool
  const available = dPool.filter((_, i) => !dUsedIdx.has(i));
  if (!available.length) return null;
  const k = available[0];
  dUsedIdx.add(dPool.indexOf(k));

  const { reading, type, valid } = getTargetReading(k);
  const rest = shuffle(dPool.filter(x => x.kanji !== k.kanji));
  const dists = [];
  for (const d of rest) {
    const { all } = getReadingsForKanji(d);
    for (const r of all) {
      if (!valid.includes(r) && !dists.includes(r)) { dists.push(r); break; }
    }
    if (dists.length >= 3) break;
  }
  let pi = 0;
  while (dists.length < 3) {
    const p = PAD_READINGS[pi++ % PAD_READINGS.length];
    if (!dists.includes(p) && !valid.includes(p)) dists.push(p);
  }
  return {
    kanji: k.kanji, hanviet: k.hanviet, meaning: k.meaning,
    correctReading: reading, validReadings: valid,
    readingType: type, distractors: dists.slice(0, 3),
  };
}

// ══════════════════════════════════════════
// THEME
// ══════════════════════════════════════════
function getTheme(floor) {
  if (floor % BOSS_EVERY === 0) return BOSS_THEME;
  return FLOOR_THEMES.find(t => floor >= t.range[0] && floor <= t.range[1])
    || FLOOR_THEMES[FLOOR_THEMES.length - 1];
}
function isBoss(floor) { return floor % BOSS_EVERY === 0; }

// ══════════════════════════════════════════
// TIMER
// ══════════════════════════════════════════
function stopDungeonTimer() { clearInterval(dTimerHandle); dTimerHandle = null; }
function startDungeonTimer() {
  stopDungeonTimer();
  dTimeLeft = ANSWER_TIME;
  renderTimer();
  dTimerHandle = setInterval(() => {
    dTimeLeft--;
    renderTimer();
    if (dTimeLeft <= 0) { stopDungeonTimer(); onTimeout(); }
  }, 1000);
}
function renderTimer() {
  const el = document.getElementById('dng-timer-val');
  if (!el) return;
  el.textContent = dTimeLeft + 's';
  el.style.color = dTimeLeft <= 3 ? '#ef4444' : '';
}

// ══════════════════════════════════════════
// RENDER ENEMY + OPTIONS
// ══════════════════════════════════════════
function renderEnemy(card) {
  const theme = getTheme(dFloor);
  const boss  = isBoss(dFloor);
  const m     = getMastery(card.kanji);
  const stars = '★'.repeat(m) + '☆'.repeat(MASTERY_MAX - m);

  // Arena background
  const arena = document.getElementById('dng-arena');
  arena.style.background = `linear-gradient(170deg, ${theme.bg} 0%, #080808 100%)`;

  // Enemy wrap
  document.getElementById('dng-enemy-wrap').innerHTML = `
    <div class="dng-enemy-hp-wrap">
      <div class="dng-enemy-hp-bar" id="dng-e-hp-bar"></div>
    </div>
    <div id="dng-enemy-sprite" class="${boss ? 'dng-boss-sprite' : 'dng-enemy-sprite-el'}"
         style="color:${theme.accent}">${theme.sprite}</div>
    <div id="dng-enemy-kanji" style="color:${theme.accent};text-shadow:0 0 24px ${theme.accent}88">${card.kanji}</div>
    <div class="dng-enemy-meta">
      <span class="dng-mastery-stars">${stars}</span>
      <span class="dng-enemy-count">${dEnemyIdx + 1}/${ENEMIES_PER_FLOOR}</span>
    </div>`;

  // Options
  const panel = document.getElementById('dng-options');
  const opts  = shuffle([card.correctReading, ...card.distractors]);
  panel.innerHTML = `
    <div class="dng-card-hint">
      <span class="dng-hint-kanji">${card.kanji}</span>
      <span class="dng-hint-sep">·</span>
      <span class="dng-hint-hanviet">${card.hanviet}</span>
      <span class="dng-reading-badge ${card.readingType === 'on' ? 'badge-on' : 'badge-kun'}">
        ${card.readingType === 'on' ? '音読み' : '訓読み'}
      </span>
    </div>
    <div id="dng-opts-grid"></div>`;

  const grid = document.getElementById('dng-opts-grid');
  opts.forEach(opt => {
    const btn = document.createElement('button');
    btn.className   = 'dng-opt-btn';
    btn.textContent = opt;
    btn.addEventListener('click',      () => onAnswer(btn, opt));
    btn.addEventListener('mouseenter', () => speakJP(opt));
    grid.appendChild(btn);
  });

  // Speak kanji
  setTimeout(() => speakJP(card.kanji), 250);
  startDungeonTimer();
}

// ══════════════════════════════════════════
// ANSWER
// ══════════════════════════════════════════
function onAnswer(btn, chosen) {
  if (dAnswering) return;
  dAnswering = true;
  stopDungeonTimer();
  dTotal++;

  const isCorrect = chosen === dCurrentCard.correctReading;
  const isPartial = !isCorrect && dCurrentCard.validReadings.includes(chosen);

  if (isCorrect || isPartial) {
    dCorrect++; dStreak++;
    updateMastery(dCurrentCard.kanji, true);
    btn.classList.add('dng-opt-correct');
    speakJP(dCurrentCard.correctReading);
    playTone(880, 'sine', 0.12);
    const xp = isCorrect
      ? XP_PER_CORRECT + Math.min(dStreak - 1, 5) * XP_STREAK_BONUS
      : Math.floor(XP_PER_CORRECT / 2);
    addDungeonXP(xp, btn);
    animateEnemyHit();
    updateDngHUD();
    setTimeout(() => { dAnswering = false; nextEnemy(); }, 650);

  } else {
    dStreak = 0;
    updateMastery(dCurrentCard.kanji, false);
    btn.classList.add('dng-opt-wrong');
    speakJP(dCurrentCard.correctReading);
    playTone(200, 'sawtooth', 0.15);
    // Reveal correct
    document.querySelectorAll('.dng-opt-btn').forEach(b => {
      if (b.textContent === dCurrentCard.correctReading) b.classList.add('dng-opt-correct');
    });
    animateHeroHit();
    updateDngHUD();
    setTimeout(() => {
      btn.classList.remove('dng-opt-wrong');
      dAnswering = false;
      if (dHeroHP <= 0) showGameOver();
      else startDungeonTimer(); // retry same enemy
    }, 950);
  }
}

function onTimeout() {
  if (dAnswering) return;
  dAnswering = true;
  dTotal++; dStreak = 0;
  updateMastery(dCurrentCard.kanji, false);
  document.querySelectorAll('.dng-opt-btn').forEach(b => {
    if (b.textContent === dCurrentCard.correctReading) b.classList.add('dng-opt-correct');
  });
  speakJP(dCurrentCard.correctReading);
  playTone(180, 'sawtooth', 0.15);
  animateHeroHit();
  updateDngHUD();
  setTimeout(() => {
    dAnswering = false;
    if (dHeroHP <= 0) showGameOver();
    else startDungeonTimer();
  }, 950);
}

// ══════════════════════════════════════════
// ANIMATIONS
// ══════════════════════════════════════════
function animateEnemyHit() {
  const sprite = document.getElementById('dng-enemy-sprite');
  if (sprite) { sprite.classList.add('hit-anim'); setTimeout(() => sprite.classList.remove('hit-anim'), 400); }
  // Damage float
  const wrap = document.getElementById('dng-enemy-wrap');
  if (wrap) {
    const el = document.createElement('div');
    el.className   = 'dng-dmg-float';
    el.textContent = '⚔️';
    wrap.appendChild(el);
    setTimeout(() => el.remove(), 600);
  }
}
function animateHeroHit() {
  dHeroHP = Math.max(0, dHeroHP - 1);
  const hero  = document.getElementById('dng-hero-sprite');
  const arena = document.getElementById('dng-arena');
  if (hero)  { hero.classList.add('hero-hit');   setTimeout(() => hero.classList.remove('hero-hit'),   400); }
  if (arena) { arena.classList.add('dmg-flash'); setTimeout(() => arena.classList.remove('dmg-flash'), 300); }
}

// ══════════════════════════════════════════
// FLOOR FLOW
// ══════════════════════════════════════════
function nextEnemy() {
  dEnemyIdx++;
  if (dEnemyIdx >= ENEMIES_PER_FLOOR) { showFloorComplete(); return; }
  dCurrentCard = buildCard();
  if (!dCurrentCard) { showFloorComplete(); return; }
  renderEnemy(dCurrentCard);
}

function showFloorComplete() {
  stopDungeonTimer();
  if (dFloor > dProgress.maxFloor) { dProgress.maxFloor = dFloor; saveProgress(); }
  incrementDailyFloor();
  const acc  = dTotal > 0 ? Math.round((dCorrect / dTotal) * 100) : 0;
  const boss = isBoss(dFloor);
  dFloor++;

  const nextBoss = isBoss(dFloor);
  document.getElementById('dng-ov-emoji').textContent = boss ? '🏆' : acc >= 80 ? '🔥' : '✨';
  document.getElementById('dng-ov-title').textContent = boss ? 'Boss bị tiêu diệt!' : `Tầng ${dFloor - 1} hoàn thành!`;
  document.getElementById('dng-ov-detail').innerHTML  = `
    <div class="dng-ov-row">🎯 ${acc}% &nbsp; 🔥 Streak ${dStreak} &nbsp; ✨ Lv.${dLevel}</div>
    <div class="dng-ov-daily">📅 ${dailyData.floors}/${DAILY_GOAL} tầng hôm nay · 🔥${dailyData.streak} ngày liên tiếp</div>
    <div class="dng-ov-next">Tầng tiếp: ${dFloor} ${nextBoss ? '⚠️ BOSS!' : getTheme(dFloor).name}</div>`;
  document.getElementById('dng-btn-next').textContent = '▶ Tầng tiếp';
  document.getElementById('dng-overlay').classList.add('visible');
}

function showGameOver() {
  stopDungeonTimer();
  document.getElementById('dng-ov-emoji').textContent = '💀';
  document.getElementById('dng-ov-title').textContent = 'Thua rồi!';
  document.getElementById('dng-ov-detail').innerHTML  = `
    <div class="dng-ov-row">Qua được ${dEnemyIdx}/${ENEMIES_PER_FLOOR} kẻ địch</div>
    <div class="dng-ov-daily">✅ ${dCorrect} đúng · ❌ ${dTotal - dCorrect} sai</div>
    <div class="dng-ov-next">Thử lại từ đầu tầng ${dFloor}</div>`;
  document.getElementById('dng-btn-next').textContent = '↩ Thử lại';
  document.getElementById('dng-overlay').classList.add('visible');
}

// ══════════════════════════════════════════
// FLOOR INTRO + START
// ══════════════════════════════════════════
function showFloorIntro(cb) {
  const theme = getTheme(dFloor);
  const boss  = isBoss(dFloor);
  const arena = document.getElementById('dng-arena');
  arena.style.background = `linear-gradient(170deg, ${theme.bg} 0%, #080808 100%)`;
  arena.innerHTML = `
    <div id="dng-floor-intro">
      <div class="dfi-sprite">${theme.sprite}</div>
      <div class="dfi-title" style="color:${theme.accent}">
        ${boss ? '⚠️ BOSS FLOOR ⚠️' : `Tầng ${dFloor}`}
      </div>
      <div class="dfi-name">${theme.name}</div>
    </div>`;
  document.getElementById('dng-options').innerHTML = '';
  setTimeout(() => { rebuildArena(); cb(); }, 1300);
}

function rebuildArena() {
  document.getElementById('dng-arena').innerHTML = `
    <div id="dng-enemy-side"><div id="dng-enemy-wrap"></div></div>
    <div id="dng-hero-side">
      <div id="dng-hero-sprite">🧙</div>
      <div id="dng-hero-hp"></div>
    </div>`;
}

function startNextFloor() {
  dHeroHP    = HERO_MAX_HP;
  dEnemyIdx  = 0;
  dCorrect   = 0; dTotal = 0;
  dAnswering = false;
  dPool      = getWeightedPool();
  dUsedIdx   = new Set();
  dCurrentCard = buildCard();
  document.getElementById('dng-overlay').classList.remove('visible');
  showFloorIntro(() => {
    updateDngHUD();
    if (dCurrentCard) renderEnemy(dCurrentCard);
  });
}

// ── Entry point (giữ tên cũ để kanji-state.js gọi được) ──
function startBubbleGame() {
  loadDungeonXP();
  loadMastery();
  loadDaily();
  checkAndResetDaily();
  loadProgress();
  dFloor   = 1;
  dStreak  = 0;
  document.getElementById('dng-overlay').classList.remove('visible');
  rebuildArena();
  startNextFloor();
}
