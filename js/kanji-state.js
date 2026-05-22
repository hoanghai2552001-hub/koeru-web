// ══════════════════════════════════════════
// SHARED STATE
// ══════════════════════════════════════════
let selectedLevel = "ALL";

function getFilteredDeck() {
  return selectedLevel === "ALL" ? ALL_KANJI : ALL_KANJI.filter(k => k.level === selectedLevel);
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
// showScreen defined below in SP section

// Home level buttons
document.querySelectorAll('.home-lvl-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.home-lvl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedLevel = btn.dataset.lvl;
  });
});

document.getElementById('go-flash').addEventListener('click', () => {
  showScreen('flash-screen');
  buildDeck();
});
document.getElementById('go-match').addEventListener('click', () => {
  showScreen('match-screen');
  startMatchGame();
});
document.getElementById('flash-back').addEventListener('click', () => {
  stopTimer();
  showScreen('home-screen');
});
document.getElementById('match-back').addEventListener('click', () => {
  stopMatchTimer();
  showScreen('home-screen');
});
document.getElementById('btn-home-from-done').addEventListener('click', () => {
  document.getElementById('done-screen').classList.remove('visible');
  showScreen('home-screen');
});

// Bubble game event listeners
document.getElementById('go-bubble').addEventListener('click', () => {
  showScreen('bubble-screen');
  startBubbleGame();
});
document.getElementById('bubble-back').addEventListener('click', () => {
  stopDungeonTimer();
  showScreen('home-screen');
});
document.getElementById('dng-btn-next').addEventListener('click', () => {
  startNextFloor();
});
document.getElementById('dng-btn-home').addEventListener('click', () => {
  stopDungeonTimer();
  document.getElementById('dng-overlay').classList.remove('visible');
  showScreen('home-screen');
});


