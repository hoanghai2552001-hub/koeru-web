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
  { range:[1,5],   spriteKey:'frog',   name:'Ếch Yêu Tinh', bg:'#061a0e', accent:'#4ade80' },
  { range:[6,10],  spriteKey:'fox',    name:'Cáo Thần',      bg:'#1a0e06', accent:'#fb923c' },
  { range:[11,15], spriteKey:'oni',    name:'Quỷ Oni',        bg:'#1a0612', accent:'#f472b6' },
  { range:[16,20], spriteKey:'dragon', name:'Rồng Xanh',     bg:'#060e1a', accent:'#60a5fa' },
  { range:[21,99], spriteKey:'alien',  name:'Ma Vương',       bg:'#0e061a', accent:'#a78bfa' },
];
const BOSS_THEME = { spriteKey:'boss', name:'⚠️ BOSS', bg:'#1a0606', accent:'#ef4444' };

// ── Pixel Art Sprites (SVG 16×16) ──
const PIXEL_SPRITES = {
  hero:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="6" y="0" width="4" height="1" fill="#7c3aed"/><rect x="5" y="1" width="6" height="3" fill="#7c3aed"/><rect x="6" y="1" width="1" height="2" fill="#a78bfa"/><rect x="3" y="4" width="10" height="1" fill="#5b21b6"/><rect x="5" y="5" width="6" height="4" fill="#fde68a"/><rect x="6" y="6" width="1" height="1" fill="#000"/><rect x="9" y="6" width="1" height="1" fill="#000"/><rect x="7" y="8" width="2" height="1" fill="#92400e"/><rect x="4" y="9" width="8" height="5" fill="#2563eb"/><rect x="3" y="9" width="2" height="4" fill="#1d4ed8"/><rect x="11" y="9" width="2" height="4" fill="#1d4ed8"/><rect x="4" y="11" width="8" height="1" fill="#d97706"/><rect x="5" y="14" width="2" height="2" fill="#1d4ed8"/><rect x="9" y="14" width="2" height="2" fill="#1d4ed8"/><rect x="5" y="15" width="2" height="1" fill="#78350f"/><rect x="9" y="15" width="2" height="1" fill="#78350f"/><rect x="13" y="5" width="1" height="8" fill="#d97706"/><rect x="12" y="3" width="3" height="3" fill="#fbbf24"/><rect x="13" y="2" width="1" height="2" fill="#f59e0b"/></svg>`,

  frog:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="5" y="0" width="1" height="3" fill="#fbbf24"/><rect x="7" y="0" width="2" height="2" fill="#fbbf24"/><rect x="10" y="0" width="1" height="3" fill="#fbbf24"/><rect x="5" y="2" width="6" height="1" fill="#f59e0b"/><rect x="3" y="3" width="4" height="4" fill="#22c55e"/><rect x="9" y="3" width="4" height="4" fill="#22c55e"/><rect x="3" y="4" width="3" height="2" fill="#fff"/><rect x="10" y="4" width="3" height="2" fill="#fff"/><rect x="3" y="4" width="1" height="1" fill="#000"/><rect x="12" y="4" width="1" height="1" fill="#000"/><rect x="2" y="5" width="12" height="8" fill="#22c55e"/><rect x="4" y="8" width="8" height="4" fill="#bbf7d0"/><rect x="4" y="10" width="8" height="1" fill="#166534"/><rect x="5" y="11" width="1" height="1" fill="#166534"/><rect x="10" y="11" width="1" height="1" fill="#166534"/><rect x="0" y="11" width="3" height="4" fill="#16a34a"/><rect x="13" y="11" width="3" height="4" fill="#16a34a"/><rect x="0" y="14" width="4" height="1" fill="#15803d"/><rect x="12" y="14" width="4" height="1" fill="#15803d"/></svg>`,

  fox:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="2" y="0" width="3" height="5" fill="#f97316"/><rect x="11" y="0" width="3" height="5" fill="#f97316"/><rect x="3" y="1" width="1" height="3" fill="#fde68a"/><rect x="12" y="1" width="1" height="3" fill="#fde68a"/><rect x="2" y="4" width="12" height="7" fill="#f97316"/><rect x="4" y="6" width="4" height="4" fill="#fde68a"/><rect x="8" y="6" width="4" height="4" fill="#fde68a"/><rect x="4" y="5" width="3" height="2" fill="#fff"/><rect x="9" y="5" width="3" height="2" fill="#fff"/><rect x="5" y="5" width="1" height="1" fill="#000"/><rect x="10" y="5" width="1" height="1" fill="#000"/><rect x="7" y="8" width="2" height="1" fill="#c2410c"/><rect x="3" y="11" width="10" height="5" fill="#f97316"/><rect x="12" y="9" width="4" height="5" fill="#f97316"/><rect x="13" y="8" width="3" height="2" fill="#fde68a"/><rect x="4" y="14" width="3" height="2" fill="#ea580c"/><rect x="9" y="14" width="3" height="2" fill="#ea580c"/></svg>`,

  oni:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="4" y="0" width="2" height="4" fill="#fbbf24"/><rect x="10" y="0" width="2" height="4" fill="#fbbf24"/><rect x="5" y="0" width="1" height="3" fill="#fde68a"/><rect x="10" y="0" width="1" height="3" fill="#fde68a"/><rect x="2" y="3" width="12" height="8" fill="#ef4444"/><rect x="3" y="5" width="4" height="1" fill="#dc2626"/><rect x="9" y="5" width="4" height="1" fill="#dc2626"/><rect x="3" y="6" width="4" height="2" fill="#fff"/><rect x="9" y="6" width="4" height="2" fill="#fff"/><rect x="4" y="6" width="1" height="1" fill="#000"/><rect x="11" y="6" width="1" height="1" fill="#000"/><rect x="4" y="9" width="8" height="2" fill="#7f1d1d"/><rect x="5" y="9" width="1" height="3" fill="#fff"/><rect x="7" y="9" width="2" height="2" fill="#fff"/><rect x="10" y="9" width="1" height="3" fill="#fff"/><rect x="3" y="11" width="10" height="5" fill="#dc2626"/><rect x="13" y="4" width="2" height="9" fill="#6b7280"/><rect x="12" y="3" width="4" height="2" fill="#9ca3af"/></svg>`,

  dragon:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="0" y="4" width="4" height="7" fill="#1d4ed8"/><rect x="12" y="4" width="4" height="7" fill="#1d4ed8"/><rect x="1" y="3" width="3" height="3" fill="#2563eb"/><rect x="12" y="3" width="3" height="3" fill="#2563eb"/><rect x="5" y="0" width="2" height="3" fill="#93c5fd"/><rect x="9" y="0" width="2" height="3" fill="#93c5fd"/><rect x="4" y="2" width="8" height="7" fill="#3b82f6"/><rect x="5" y="7" width="6" height="3" fill="#2563eb"/><rect x="5" y="4" width="2" height="2" fill="#fbbf24"/><rect x="9" y="4" width="2" height="2" fill="#fbbf24"/><rect x="6" y="4" width="1" height="1" fill="#000"/><rect x="10" y="4" width="1" height="1" fill="#000"/><rect x="6" y="9" width="1" height="1" fill="#1e40af"/><rect x="9" y="9" width="1" height="1" fill="#1e40af"/><rect x="5" y="9" width="6" height="7" fill="#3b82f6"/><rect x="6" y="10" width="4" height="5" fill="#bfdbfe"/><rect x="11" y="11" width="4" height="2" fill="#2563eb"/><rect x="13" y="13" width="2" height="1" fill="#1d4ed8"/><rect x="4" y="15" width="3" height="1" fill="#1d4ed8"/><rect x="9" y="15" width="3" height="1" fill="#1d4ed8"/></svg>`,

  alien:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="3" y="0" width="1" height="3" fill="#a78bfa"/><rect x="12" y="0" width="1" height="3" fill="#a78bfa"/><rect x="2" y="0" width="2" height="1" fill="#a78bfa"/><rect x="12" y="0" width="2" height="1" fill="#a78bfa"/><rect x="3" y="2" width="10" height="9" fill="#7c3aed"/><rect x="4" y="4" width="3" height="3" fill="#e0e7ff"/><rect x="9" y="4" width="3" height="3" fill="#e0e7ff"/><rect x="4" y="4" width="2" height="2" fill="#c4b5fd"/><rect x="9" y="4" width="2" height="2" fill="#c4b5fd"/><rect x="5" y="4" width="1" height="1" fill="#000"/><rect x="10" y="4" width="1" height="1" fill="#000"/><rect x="5" y="8" width="1" height="2" fill="#4c1d95"/><rect x="7" y="8" width="2" height="2" fill="#4c1d95"/><rect x="10" y="8" width="1" height="2" fill="#4c1d95"/><rect x="4" y="9" width="2" height="1" fill="#4c1d95"/><rect x="10" y="9" width="2" height="1" fill="#4c1d95"/><rect x="1" y="5" width="2" height="3" fill="#6d28d9"/><rect x="13" y="5" width="2" height="3" fill="#6d28d9"/><rect x="3" y="11" width="2" height="4" fill="#7c3aed"/><rect x="7" y="11" width="2" height="4" fill="#7c3aed"/><rect x="11" y="11" width="2" height="4" fill="#7c3aed"/><rect x="2" y="13" width="2" height="2" fill="#6d28d9"/><rect x="7" y="13" width="2" height="2" fill="#6d28d9"/><rect x="12" y="13" width="2" height="2" fill="#6d28d9"/></svg>`,

  boss:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="1" y="0" width="3" height="5" fill="#dc2626"/><rect x="12" y="0" width="3" height="5" fill="#dc2626"/><rect x="2" y="0" width="2" height="4" fill="#ef4444"/><rect x="12" y="0" width="2" height="4" fill="#ef4444"/><rect x="2" y="3" width="12" height="7" fill="#991b1b"/><rect x="4" y="3" width="8" height="2" fill="#7f1d1d"/><rect x="3" y="6" width="4" height="3" fill="#fbbf24"/><rect x="9" y="6" width="4" height="3" fill="#fbbf24"/><rect x="4" y="7" width="2" height="1" fill="#f59e0b"/><rect x="10" y="7" width="2" height="1" fill="#f59e0b"/><rect x="5" y="7" width="1" height="1" fill="#000"/><rect x="11" y="7" width="1" height="1" fill="#000"/><rect x="7" y="7" width="2" height="2" fill="#7f1d1d"/><rect x="3" y="9" width="10" height="3" fill="#450a0a"/><rect x="4" y="9" width="1" height="4" fill="#fff"/><rect x="6" y="9" width="2" height="3" fill="#fff"/><rect x="9" y="9" width="2" height="3" fill="#fff"/><rect x="12" y="9" width="1" height="4" fill="#fff"/><rect x="2" y="12" width="12" height="4" fill="#7f1d1d"/><rect x="0" y="11" width="3" height="5" fill="#991b1b"/><rect x="13" y="11" width="3" height="5" fill="#991b1b"/></svg>`
};

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
let dEnemyHP = 1; // enemy HP for visual bar (boss = 2)

// ══════════════════════════════════════════
// MASTERY (localStorage per kanji)
// ══════════════════════════════════════════
let masteryData = {};
// Mastery: đọc/ghi qua unified store (koeru-mastery.js).
// getMastery() và updateMastery() được định nghĩa trong koeru-mastery.js
// và dùng window.koeruMastery. masteryData ở đây chỉ là local cache cho UI.

function loadMastery() {
  // Sync local cache từ unified store để UI dungeon không bị lệch
  try {
    if (window.koeruMastery && typeof ALL_KANJI !== 'undefined') {
      masteryData = {};
      for (const k of ALL_KANJI) {
        const m = window.koeruMastery.getMasteryLevel(k.kanji);
        if (m > 0) masteryData[k.kanji] = { m, seen: Date.now() };
      }
    } else {
      // Fallback: đọc legacy key
      const raw    = localStorage.getItem('bubble_mastery');
      const parsed = JSON.parse(raw || '{}');
      masteryData  = (parsed && typeof parsed === 'object' && !Array.isArray(parsed))
        ? parsed : {};
    }
  } catch(e) { masteryData = {}; }
}
function saveMastery() {
  // Không cần ghi riêng — unified store đã được ghi trong updateMastery()
  // Giữ lại để tránh lỗi nếu code khác gọi saveMastery()
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
function dngLoadProgress() {
  try { dProgress = { maxFloor:1, ...JSON.parse(localStorage.getItem('dng_progress') || '{}') }; }
  catch(e) {}
}
function dngSaveProgress() {
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
  const set = (id, fn) => { const el = $(id); if (el) fn(el); };
  set('dng-floor-num',   el => el.textContent  = `Tầng ${dFloor}`);
  set('dng-lv-badge',    el => el.textContent  = `Lv.${dLevel}`);
  set('dng-xp-bar',      el => el.style.width  = `${(dXP / XP_PER_LEVEL) * 100}%`);
  set('dng-streak-val',  el => el.textContent  = dStreak);
  set('dng-correct-val', el => el.textContent  = dCorrect);
  // Hero HP
  const hp = $('dng-hero-hp');
  if (hp) hp.innerHTML =
    '❤️'.repeat(dHeroHP) +
    '<span style="opacity:.25;filter:grayscale(1)">❤️</span>'.repeat(HERO_MAX_HP - dHeroHP);
  // Daily bar
  const pct = Math.min(100, (dailyData.floors / DAILY_GOAL) * 100);
  const bar = $('dng-daily-bar');
  if (bar) bar.style.width = pct + '%';
  set('dng-daily-text', el => el.textContent =
    `📅 ${dailyData.floors}/${DAILY_GOAL} tầng · 🔥${dailyData.streak} ngày`);
}

// ══════════════════════════════════════════
// AUDIO
// ══════════════════════════════════════════
let dngSpeakId = 0; // guard against duplicate speaks
function speakJP(text) {
  if (!window.speechSynthesis) return;
  if (typeof soundEnabled !== 'undefined' && !soundEnabled) return;
  speechSynthesis.cancel();
  const id = ++dngSpeakId;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'ja-JP'; utter.rate = 0.85; utter.pitch = 1.0;
  const speak = () => {
    if (id !== dngSpeakId) return; // cancelled by newer call
    const voices = speechSynthesis.getVoices().filter(v => v.lang === 'ja-JP');
    const pref   = ['Haruka','Sayaka','Ayumi','Ichiro'];
    let picked   = null;
    for (const n of pref) { picked = voices.find(v => v.name.includes(n)); if (picked) break; }
    if (!picked && voices.length) picked = voices[0];
    if (picked) utter.voice = picked;
    speechSynthesis.speak(utter);
  };
  if (speechSynthesis.getVoices().length) speak();
  else speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
}

// ══════════════════════════════════════════
// KATAKANA → HIRAGANA
// ══════════════════════════════════════════
function toHiragana(str) {
  if (!str) return str;
  return str.replace(/[ァ-ヶ]/g, c => String.fromCharCode(c.charCodeAt(0) - 0x60));
}

// ══════════════════════════════════════════
// READING HELPERS
// ══════════════════════════════════════════
function getReadingsForKanji(k) {
  const ons  = (k.on  && k.on  !== '—')
    ? k.on.split('、').map(r => toHiragana(r.trim())).filter(Boolean) : [];
  const kuns = (k.kun && k.kun !== '—')
    ? k.kun.split('、').map(r => toHiragana(r.replace(/[（）().\-]/g,'').trim())).filter(Boolean) : [];
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
    on: k.on, kun: k.kun, words: k.words || null,
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
// TIMER (visual progress bar + text)
// ══════════════════════════════════════════
function stopDungeonTimer() { clearInterval(dTimerHandle); dTimerHandle = null; }
function startDungeonTimer() {
  stopDungeonTimer();
  dTimeLeft = ANSWER_TIME;
  renderTimer();
  dTimerHandle = setInterval(() => {
    dTimeLeft--;
    renderTimer();
    if (dTimeLeft <= 0) { stopDungeonTimer(); dngOnTimeout(); }
  }, 1000);
}
function renderTimer() {
  const el = document.getElementById('dng-timer-val');
  if (!el) return;
  el.textContent = dTimeLeft + 's';
  el.style.color = dTimeLeft <= 3 ? '#ef4444' : '';
  // Timer progress bar
  const bar = document.getElementById('dng-timer-bar');
  if (bar) {
    const pct = (dTimeLeft / ANSWER_TIME) * 100;
    bar.style.width = pct + '%';
    bar.style.background = dTimeLeft <= 3
      ? 'linear-gradient(90deg,#ef4444,#f97316)'
      : 'linear-gradient(90deg,var(--accent),var(--accent2))';
  }
}

// ══════════════════════════════════════════
// RENDER ENEMY + OPTIONS
// ══════════════════════════════════════════
// resetHP=true when showing a NEW enemy; false when re-rendering same enemy (boss 2nd hit)
function renderEnemy(card, resetHP = true) {
  if (!card) { console.error('[Dungeon] renderEnemy: card is null'); return; }
  const enemyWrap = document.getElementById('dng-enemy-wrap');
  if (!enemyWrap) { console.error('[Dungeon] dng-enemy-wrap not found - calling rebuildArena'); rebuildArena(); }
  const theme = getTheme(dFloor);
  const boss  = isBoss(dFloor);
  const m     = getMastery(card.kanji);
  const stars = '★'.repeat(m) + '☆'.repeat(MASTERY_MAX - m);

  // Only reset HP when it's a brand-new enemy (not boss re-render after 1st hit)
  if (resetHP) dEnemyHP = boss ? 2 : 1;

  // Arena background
  const arena = document.getElementById('dng-arena');
  arena.style.background = `linear-gradient(170deg, ${theme.bg} 0%, #080808 100%)`;

  // Enemy wrap — show current HP (boss may already have taken 1 hit)
  const hpPct = boss ? (dEnemyHP / 2 * 100) : 100;
  document.getElementById('dng-enemy-wrap').innerHTML = `
    <div class="dng-enemy-hp-wrap">
      <div class="dng-enemy-hp-bar" id="dng-e-hp-bar" style="width:${hpPct}%"></div>
    </div>
    <div id="dng-enemy-sprite" class="${boss ? 'dng-boss-sprite' : 'dng-enemy-sprite-el'}"
         style="color:${theme.accent}">${PIXEL_SPRITES[theme.spriteKey] || ''}</div>
    <div id="dng-enemy-kanji" style="color:${theme.accent};text-shadow:0 0 24px ${theme.accent}88">${card.kanji}</div>
    <div class="dng-enemy-meaning">${card.meaning}</div>
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
    <div class="dng-timer-bar-wrap"><div class="dng-timer-bar" id="dng-timer-bar"></div></div>
    <div id="dng-opts-grid"></div>
    <div id="dng-answer-reveal"></div>`;

  const grid = document.getElementById('dng-opts-grid');
  opts.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className   = 'dng-opt-btn';
    btn.style.animationDelay = (i * 0.06) + 's';
    btn.textContent = opt;
    btn.addEventListener('click', () => dngOnAnswer(btn, opt));
    grid.appendChild(btn);
  });

  // Speak kanji on appear
  setTimeout(() => speakJP(card.kanji), 250);
  startDungeonTimer();
}

// ══════════════════════════════════════════
// DISABLE / ENABLE OPTIONS
// ══════════════════════════════════════════
function disableAllOptions() {
  document.querySelectorAll('.dng-opt-btn').forEach(b => {
    b.style.pointerEvents = 'none';
  });
}

// ══════════════════════════════════════════
// SHOW ANSWER DETAIL (after wrong/timeout)
// ══════════════════════════════════════════
function showAnswerReveal(card) {
  const el = document.getElementById('dng-answer-reveal');
  if (!el) return;
  el.innerHTML = `
    <div class="dng-reveal-row">
      <span class="dng-reveal-kanji">${card.kanji}</span>
      <span class="dng-reveal-reading">${card.correctReading}</span>
    </div>
    <div class="dng-reveal-detail">
      On: ${toHiragana(card.on) || '—'} · Kun: ${toHiragana(card.kun) || '—'}
    </div>`;
  el.classList.add('visible');
}

// ══════════════════════════════════════════
// ANSWER
// ══════════════════════════════════════════
function dngOnAnswer(btn, chosen) {
  if (dAnswering) return;
  dAnswering = true;
  stopDungeonTimer();
  disableAllOptions();
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

    // Reduce enemy HP bar
    dEnemyHP = Math.max(0, dEnemyHP - 1);
    const hpBar = document.getElementById('dng-e-hp-bar');
    if (hpBar) {
      const boss = isBoss(dFloor);
      hpBar.style.width = boss ? (dEnemyHP / 2 * 100) + '%' : '0%';
      if (dEnemyHP <= 0) hpBar.style.background = 'transparent';
    }

    updateDngHUD();

    // Boss needs 2 correct hits — re-render same card, do NOT reset HP
    if (dEnemyHP > 0) {
      setTimeout(() => { dAnswering = false; renderEnemy(dCurrentCard, false); }, 700);
    } else {
      // Show compound words popup before next enemy
      showCompoundPopup(dCurrentCard, () => { dAnswering = false; nextEnemy(); });
    }

  } else {
    dStreak = 0;
    updateMastery(dCurrentCard.kanji, false);
    btn.classList.add('dng-opt-wrong');
    speakJP(dCurrentCard.correctReading);
    playTone(200, 'sawtooth', 0.15);
    // Reveal correct button
    document.querySelectorAll('.dng-opt-btn').forEach(b => {
      if (b.textContent === dCurrentCard.correctReading) b.classList.add('dng-opt-correct');
    });
    // Show answer detail
    showAnswerReveal(dCurrentCard);
    animateHeroHit();
    updateDngHUD();
    setTimeout(() => {
      dAnswering = false;
      const reveal = document.getElementById('dng-answer-reveal');
      if (reveal) reveal.classList.remove('visible');
      if (dHeroHP <= 0) showGameOver();
      else {
        // Re-render same enemy for retry
        renderEnemy(dCurrentCard);
      }
    }, 1600);
  }
}

function dngOnTimeout() {
  if (dAnswering) return;
  dAnswering = true;
  disableAllOptions();
  dTotal++; dStreak = 0;
  updateMastery(dCurrentCard.kanji, false);
  document.querySelectorAll('.dng-opt-btn').forEach(b => {
    if (b.textContent === dCurrentCard.correctReading) b.classList.add('dng-opt-correct');
  });
  showAnswerReveal(dCurrentCard);
  speakJP(dCurrentCard.correctReading);
  playTone(180, 'sawtooth', 0.15);
  animateHeroHit();
  updateDngHUD();
  setTimeout(() => {
    dAnswering = false;
    const reveal = document.getElementById('dng-answer-reveal');
    if (reveal) reveal.classList.remove('visible');
    if (dHeroHP <= 0) showGameOver();
    else renderEnemy(dCurrentCard);
  }, 1600);
}

// ══════════════════════════════════════════
// COMPOUND WORDS POPUP
// ══════════════════════════════════════════
// Detect if string is Vietnamese (contains at least one diacritic or đ/Đ)
function isVietnamese(str) {
  return str && /[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]/.test(str);
}

function showCompoundPopup(card, cb) {
  const words = filterWordsForLevel(card.words, selectedLevel); // array [{w,r,m}] or undefined
  // If no compound data, skip straight to next
  if (!words || !words.length) { setTimeout(cb, 200); return; }

  const panel = document.getElementById('dng-options');
  const reveal = document.getElementById('dng-answer-reveal');
  if (reveal) reveal.classList.remove('visible');

  // Build popup HTML — only show meaning if it's Vietnamese
  const items = words.map(w => {
    const meaning = isVietnamese(w.m) ? `<span class="cmp-meaning">${w.m}</span>` : '';
    return `<div class="cmp-item">
      <span class="cmp-word">${w.w}</span>
      <span class="cmp-reading">${toHiragana(w.r)}</span>
      ${meaning}
    </div>`;
  }).join('');

  panel.innerHTML = `
    <div id="dng-compound-popup">
      <div class="cmp-header">
        <span class="cmp-kanji">${card.kanji}</span>
        <span class="cmp-label">📦 Từ ghép thường gặp</span>
      </div>
      <div class="cmp-list">${items}</div>
      <div class="cmp-footer">Tự động tiếp tục...</div>
    </div>`;

  // Speak first compound
  setTimeout(() => speakJP(words[0].w), 200);

  setTimeout(cb, 2200);
}

// ══════════════════════════════════════════
// ANIMATIONS
// ══════════════════════════════════════════
function animateEnemyHit() {
  const sprite = document.getElementById('dng-enemy-sprite');
  if (sprite) { sprite.classList.add('hit-anim'); setTimeout(() => sprite.classList.remove('hit-anim'), 400); }
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
  if (dFloor > dProgress.maxFloor) { dProgress.maxFloor = dFloor; dngSaveProgress(); }
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
  if (!arena) { console.error('[Dungeon] dng-arena not found in showFloorIntro'); return; }
  arena.style.background = `linear-gradient(170deg, ${theme.bg} 0%, #080808 100%)`;
  arena.innerHTML = `
    <div id="dng-floor-intro">
      <div class="dfi-sprite">${PIXEL_SPRITES[theme.spriteKey] || ''}</div>
      <div class="dfi-title" style="color:${theme.accent}">
        ${boss ? '⚠️ BOSS FLOOR ⚠️' : `Tầng ${dFloor}`}
      </div>
      <div class="dfi-name">${theme.name}</div>
      ${boss ? '<div class="dfi-boss-hint">Boss cần 2 lần đúng để hạ!</div>' : ''}
    </div>`;
  const opts = document.getElementById('dng-options');
  if (opts) opts.innerHTML = '';
  setTimeout(() => {
    try {
      rebuildArena();
      cb();
    } catch(e) {
      console.error('[Dungeon] showFloorIntro callback error:', e);
      // Show error visibly in arena so it's diagnosable without DevTools
      const arenaEl = document.getElementById('dng-arena');
      if (arenaEl) arenaEl.innerHTML += `
        <div style="position:absolute;bottom:4px;left:4px;right:4px;background:rgba(220,0,0,.85);
          color:#fff;font-size:11px;padding:6px 8px;border-radius:4px;z-index:20;word-break:break-all;">
          ❌ ${e.message}</div>`;
    }
  }, 1300);
}

function rebuildArena() {
  const arena = document.getElementById('dng-arena');
  if (!arena) { console.error('[Dungeon] rebuildArena: dng-arena not found'); return; }
  arena.innerHTML = `
    <div id="dng-enemy-side"><div id="dng-enemy-wrap"></div></div>
    <div id="dng-hero-side">
      <div id="dng-hero-sprite">${PIXEL_SPRITES.hero}</div>
      <div id="dng-hero-hp"></div>
    </div>`;
}

function startNextFloor() {
  dHeroHP    = HERO_MAX_HP;
  dEnemyIdx  = 0;
  dCorrect   = 0; dTotal = 0;
  dAnswering = false;

  // Build pool — only keep valid kanji objects (must have .kanji and .on or .kun)
  try {
    const rawPool = getWeightedPool();
    dPool = rawPool.filter(k => k && k.kanji && (k.on || k.kun));
    if (!dPool.length) dPool = rawPool; // fallback to unfiltered if all filtered out
  } catch(e) {
    console.error('[Dungeon] getWeightedPool error:', e);
    masteryData = {};
    dPool = [];
  }
  // Absolute fallback
  if (!dPool.length) {
    try { dPool = ALL_KANJI.filter(k => k && k.kanji); } catch(e2) { dPool = []; }
  }

  dUsedIdx   = new Set();
  dCurrentCard = buildCard();
  if (!dCurrentCard && dPool.length > 0) {
    dUsedIdx.clear();
    dCurrentCard = buildCard();
  }
  console.log('[Dungeon] startNextFloor: pool=', dPool.length, 'card=', dCurrentCard ? dCurrentCard.kanji : 'NULL');

  document.getElementById('dng-overlay').classList.remove('visible');
  showFloorIntro(() => {
    updateDngHUD();
    if (dCurrentCard) {
      renderEnemy(dCurrentCard);
    } else {
      console.error('[Dungeon] dCurrentCard is null, pool size:', dPool.length);
      // Show error in options area
      const opts = document.getElementById('dng-options');
      if (opts) opts.innerHTML = '<div style="color:#f87171;text-align:center;padding:20px">Lỗi: không tải được dữ liệu kanji. Vui lòng thử lại.</div>';
    }
  });
}

// ── Entry point ──
function startBubbleGame() {
  loadDungeonXP();
  loadMastery();
  loadDaily();
  checkAndResetDaily();
  dngLoadProgress();
  dFloor   = 1;
  dStreak  = 0;
  document.getElementById('dng-overlay').classList.remove('visible');
  rebuildArena();
  startNextFloor();
}
