// ══════════════════════════════════════════
// SHARED STATE
// ══════════════════════════════════════════

// ── Sound toggle (shared across all games) ──
let soundEnabled = localStorage.getItem('kanji_sound') !== 'off';

function updateSoundBtns() {
  const icon = soundEnabled ? '🔊' : '🔇';
  ['sound-toggle', 'dng-sound-btn'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.textContent = icon;
  });
}

function toggleSound() {
  soundEnabled = !soundEnabled;
  localStorage.setItem('kanji_sound', soundEnabled ? 'on' : 'off');
  updateSoundBtns();
  if (!soundEnabled && window.speechSynthesis) speechSynthesis.cancel();
}

// ── Home progress bar ──
function updateHomeProgress() {
  const fill    = document.getElementById('home-progress-bar-fill');
  const text    = document.getElementById('home-progress-text');
  const dueEl   = document.getElementById('home-due-count');
  if (!fill || !text) return;

  const total   = typeof ALL_KANJI !== 'undefined' ? ALL_KANJI.length : 1765;
  const ms      = window.koeruMastery;
  const seen    = ms ? ms.countSeen() : 0;
  const stats   = ms ? ms.getStats()  : { due: 0, learned: 0 };
  const pct     = Math.min(100, (seen / total) * 100);

  fill.style.width  = pct + '%';
  text.textContent  = `${seen.toLocaleString()} / ${total.toLocaleString()} kanji đã gặp · ✅ ${stats.learned} thuộc`;

  if (dueEl) {
    if (stats.due > 0) {
      dueEl.textContent = `🔔 ${stats.due} kanji đến hạn ôn tập`;
      dueEl.style.display = 'block';
    } else {
      dueEl.style.display = 'none';
    }
  }
}

// ── Onboarding (hiện lần đầu) ──
function initOnboarding() {
  const overlay = document.getElementById('onboarding-overlay');
  if (!overlay) return;

  // Đã từng vào → không hiện nữa
  if (localStorage.getItem('kanji_visited')) {
    overlay.style.display = 'none';
    return;
  }

  // Chọn N5 + vào Flashcard
  document.getElementById('ob-start-btn').addEventListener('click', () => {
    localStorage.setItem('kanji_visited', '1');
    overlay.style.display = 'none';
    // Chọn level N5
    document.querySelectorAll('.home-lvl-btn').forEach(b => b.classList.remove('active'));
    const n5btn = document.querySelector('.home-lvl-btn[data-lvl="N5"]');
    if (n5btn) { n5btn.classList.add('active'); selectedLevel = 'N5'; }
    // Vào Flashcard
    showScreen('flash-screen');
    buildDeck();
  });

  document.getElementById('ob-skip-btn').addEventListener('click', () => {
    localStorage.setItem('kanji_visited', '1');
    overlay.classList.add('ob-fade-out');
    setTimeout(() => { overlay.style.display = 'none'; }, 300);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  updateSoundBtns();
  ['sound-toggle', 'dng-sound-btn'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.addEventListener('click', toggleSound);
  });
  updateHomeProgress();
  initOnboarding();
});

// ── Level-aware word filtering ──
const LEVEL_RANK = { N5:1, N4:2, N3:3, N2:4, N1:5 };
let _kanjiLevelMap = null;

function getKanjiLevelMap() {
  if (_kanjiLevelMap) return _kanjiLevelMap;
  _kanjiLevelMap = {};
  for (const k of ALL_KANJI) {
    if (k.kanji && k.level) _kanjiLevelMap[k.kanji] = LEVEL_RANK[k.level] || 6;
  }
  return _kanjiLevelMap;
}

/**
 * Lọc words[] theo level đang chọn.
 * Ẩn từ ghép chứa kanji khó hơn level hiện tại.
 * Nếu lọc hết thì giữ lại 2 từ đầu để không bị trống.
 */
function filterWordsForLevel(words, level) {
  if (!words || !words.length) return [];
  if (!level || level === 'ALL') return words;
  const maxRank = LEVEL_RANK[level] || 5;
  const map = getKanjiLevelMap();
  const filtered = words.filter(w => {
    for (const ch of (w.w || '')) {
      if (/[一-鿿]/.test(ch)) {
        const rank = map[ch];
        if (rank && rank > maxRank) return false;
      }
    }
    return true;
  });
  return filtered.length > 0 ? filtered : words.slice(0, 2);
}

// ── Audio tone generator (Web Audio API) ──
function playTone(freq = 440, type = 'sine', vol = 0.1, dur = 0.15) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc  = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + dur);
  } catch(e) { /* AudioContext not available — silent fail */ }
}
let selectedLevel = "ALL";

const ENABLED_LEVELS = new Set(['N5','N4','N3','N2']);
function getFilteredDeck() {
  const base = ALL_KANJI.filter(k => ENABLED_LEVELS.has(k.level));
  return selectedLevel === "ALL" ? base : base.filter(k => k.level === selectedLevel);
}
function shuffle(a) {
  const b = [...a];
  for (let i = b.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}

// ══════════════════════════════════════════
// SCREEN NAVIGATION
// ══════════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  ['s-sph','s-speed','s-spr'].forEach(s => document.getElementById(s)?.classList.remove('on'));
  if (['s-sph','s-speed','s-spr'].includes(id)) {
    document.getElementById(id)?.classList.add('on');
  } else {
    document.getElementById(id)?.classList.add('active');
  }
}

// ── DOM Event Listeners ──────────────────
// Wrapped in DOMContentLoaded để đảm bảo DOM luôn sẵn sàng
document.addEventListener('DOMContentLoaded', () => {

  // Home level buttons
  document.querySelectorAll('.home-lvl-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.home-lvl-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedLevel = btn.dataset.lvl;
      if (typeof gtag !== 'undefined') gtag('event', 'level_select', { level: selectedLevel, source: 'kanji_lab' });
    });
  });

  document.getElementById('go-flash').addEventListener('click', () => {
    showScreen('flash-screen');
    if (typeof gtag !== 'undefined') gtag('event', 'game_start', { game_name: 'Flashcard', level: selectedLevel });
    buildDeck();
  });
  document.getElementById('go-match').addEventListener('click', () => {
    showScreen('match-screen');
    if (typeof gtag !== 'undefined') gtag('event', 'game_start', { game_name: 'Match', level: selectedLevel });
    startMatchGame();
  });
  document.getElementById('flash-back').addEventListener('click', () => {
    stopTimer();
    showScreen('home-screen');
    updateHomeProgress();
  });
  document.getElementById('match-back').addEventListener('click', () => {
    stopMatchTimer();
    showScreen('home-screen');
    updateHomeProgress();
  });
  document.getElementById('btn-home-from-done').addEventListener('click', () => {
    document.getElementById('done-screen').classList.remove('visible');
    showScreen('home-screen');
  });

  // Bubble game event listeners
  document.getElementById('go-bubble').addEventListener('click', () => {
    showScreen('bubble-screen');
    if (typeof gtag !== 'undefined') gtag('event', 'game_start', { game_name: 'Bubble', level: selectedLevel });
    startBubbleGame();
  });
  document.getElementById('bubble-back').addEventListener('click', () => {
    stopDungeonTimer();
    showScreen('home-screen');
    updateHomeProgress();
  });
  document.getElementById('dng-btn-next').addEventListener('click', () => {
    startNextFloor();
  });
  document.getElementById('dng-btn-home').addEventListener('click', () => {
    stopDungeonTimer();
    document.getElementById('dng-overlay').classList.remove('visible');
    showScreen('home-screen');
  });

}); // end DOMContentLoaded

