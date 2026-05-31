// ══════════════════════════════════════════
// ══ GAME 2: MATCH / NỐI TỪ ══
// ══════════════════════════════════════════

// ── Compound word data (2+ kanji) per level ──
const COMPOUND_WORDS = [
// N5
{kanji:"日本",reading:"にほん",meaning_vi:"Nhật Bản",meaning_ja:"Japan / Nhật Bản",level:"N5"},
{kanji:"学校",reading:"がっこう",meaning_vi:"trường học",meaning_ja:"gakkou / trường học",level:"N5"},
{kanji:"電車",reading:"でんしゃ",meaning_vi:"tàu điện",meaning_ja:"densha / tàu điện",level:"N5"},
{kanji:"水曜日",reading:"すいようび",meaning_vi:"thứ Tư",meaning_ja:"suiyoubi / thứ Tư",level:"N5"},
{kanji:"先生",reading:"せんせい",meaning_vi:"giáo viên",meaning_ja:"sensei / thầy cô",level:"N5"},
{kanji:"大学",reading:"だいがく",meaning_vi:"đại học",meaning_ja:"daigaku / đại học",level:"N5"},
{kanji:"友人",reading:"ゆうじん",meaning_vi:"bạn bè",meaning_ja:"yuujin / bạn bè",level:"N5"},
{kanji:"毎日",reading:"まいにち",meaning_vi:"mỗi ngày",meaning_ja:"mainichi / hàng ngày",level:"N5"},
{kanji:"今日",reading:"きょう",meaning_vi:"hôm nay",meaning_ja:"kyou / hôm nay",level:"N5"},
{kanji:"食事",reading:"しょくじ",meaning_vi:"bữa ăn",meaning_ja:"shokuji / bữa ăn",level:"N5"},
{kanji:"日曜日",reading:"にちようび",meaning_vi:"Chủ nhật",meaning_ja:"nichiyoubi / Chủ nhật",level:"N5"},
{kanji:"東京",reading:"とうきょう",meaning_vi:"Tokyo",meaning_ja:"Toukyou / Tokyo",level:"N5"},
// N4
{kanji:"運動",reading:"うんどう",meaning_vi:"vận động, thể dục",meaning_ja:"undou / vận động",level:"N4"},
{kanji:"旅行",reading:"りょこう",meaning_vi:"du lịch",meaning_ja:"ryokou / du lịch",level:"N4"},
{kanji:"練習",reading:"れんしゅう",meaning_vi:"luyện tập",meaning_ja:"renshuu / luyện tập",level:"N4"},
{kanji:"便利",reading:"べんり",meaning_vi:"tiện lợi",meaning_ja:"benri / tiện lợi",level:"N4"},
{kanji:"大切",reading:"たいせつ",meaning_vi:"quan trọng",meaning_ja:"taisetsu / quan trọng",level:"N4"},
{kanji:"用意",reading:"ようい",meaning_vi:"chuẩn bị",meaning_ja:"youi / chuẩn bị",level:"N4"},
{kanji:"意見",reading:"いけん",meaning_vi:"ý kiến",meaning_ja:"iken / ý kiến",level:"N4"},
{kanji:"以上",reading:"いじょう",meaning_vi:"trở lên, hơn",meaning_ja:"ijou / trở lên",level:"N4"},
{kanji:"安全",reading:"あんぜん",meaning_vi:"an toàn",meaning_ja:"anzen / an toàn",level:"N4"},
{kanji:"関係",reading:"かんけい",meaning_vi:"quan hệ",meaning_ja:"kankei / quan hệ",level:"N4"},
{kanji:"記念",reading:"きねん",meaning_vi:"kỷ niệm",meaning_ja:"kinen / kỷ niệm",level:"N4"},
{kanji:"工場",reading:"こうじょう",meaning_vi:"nhà máy",meaning_ja:"koujou / nhà máy",level:"N4"},
// N3
{kanji:"経済",reading:"けいざい",meaning_vi:"kinh tế",meaning_ja:"keizai / kinh tế",level:"N3"},
{kanji:"政治",reading:"せいじ",meaning_vi:"chính trị",meaning_ja:"seiji / chính trị",level:"N3"},
{kanji:"環境",reading:"かんきょう",meaning_vi:"môi trường",meaning_ja:"kankyou / môi trường",level:"N3"},
{kanji:"技術",reading:"ぎじゅつ",meaning_vi:"kỹ thuật",meaning_ja:"gijutsu / kỹ thuật",level:"N3"},
{kanji:"情報",reading:"じょうほう",meaning_vi:"thông tin",meaning_ja:"jouhou / thông tin",level:"N3"},
{kanji:"問題",reading:"もんだい",meaning_vi:"vấn đề",meaning_ja:"mondai / vấn đề",level:"N3"},
{kanji:"場合",reading:"ばあい",meaning_vi:"trường hợp",meaning_ja:"baai / trường hợp",level:"N3"},
{kanji:"必要",reading:"ひつよう",meaning_vi:"cần thiết",meaning_ja:"hitsuyou / cần thiết",level:"N3"},
{kanji:"自然",reading:"しぜん",meaning_vi:"tự nhiên",meaning_ja:"shizen / tự nhiên",level:"N3"},
{kanji:"文化",reading:"ぶんか",meaning_vi:"văn hóa",meaning_ja:"bunka / văn hóa",level:"N3"},
{kanji:"社会",reading:"しゃかい",meaning_vi:"xã hội",meaning_ja:"shakai / xã hội",level:"N3"},
{kanji:"目的",reading:"もくてき",meaning_vi:"mục đích",meaning_ja:"mokuteki / mục đích",level:"N3"},
{kanji:"原因",reading:"げんいん",meaning_vi:"nguyên nhân",meaning_ja:"gen-in / nguyên nhân",level:"N3"},
{kanji:"結果",reading:"けっか",meaning_vi:"kết quả",meaning_ja:"kekka / kết quả",level:"N3"},
// N2
{kanji:"可能性",reading:"かのうせい",meaning_vi:"khả năng, tiềm năng",meaning_ja:"kanousei / khả năng",level:"N2"},
{kanji:"責任",reading:"せきにん",meaning_vi:"trách nhiệm",meaning_ja:"sekinin / trách nhiệm",level:"N2"},
{kanji:"影響",reading:"えいきょう",meaning_vi:"ảnh hưởng",meaning_ja:"eikyou / ảnh hưởng",level:"N2"},
{kanji:"判断",reading:"はんだん",meaning_vi:"phán đoán",meaning_ja:"handan / phán đoán",level:"N2"},
{kanji:"状況",reading:"じょうきょう",meaning_vi:"tình trạng",meaning_ja:"joukyou / tình trạng",level:"N2"},
{kanji:"手続き",reading:"てつづき",meaning_vi:"thủ tục",meaning_ja:"tetsuzuki / thủ tục",level:"N2"},
{kanji:"申込み",reading:"もうしこみ",meaning_vi:"đơn đăng ký",meaning_ja:"moushikomi / đăng ký",level:"N2"},
{kanji:"取り組む",reading:"とりくむ",meaning_vi:"nỗ lực giải quyết",meaning_ja:"torikumu / nỗ lực",level:"N2"},
{kanji:"待ち合わせ",reading:"まちあわせ",meaning_vi:"hẹn gặp",meaning_ja:"machiawase / hẹn gặp",level:"N2"},
{kanji:"売り上げ",reading:"うりあげ",meaning_vi:"doanh thu",meaning_ja:"uriage / doanh thu",level:"N2"},
{kanji:"見直し",reading:"みなおし",meaning_vi:"xem xét lại",meaning_ja:"minaoshi / xem lại",level:"N2"},
{kanji:"使い方",reading:"つかいかた",meaning_vi:"cách sử dụng",meaning_ja:"tsukaikata / cách dùng",level:"N2"},
// N1
{kanji:"矛盾",reading:"むじゅん",meaning_vi:"mâu thuẫn",meaning_ja:"mujun / mâu thuẫn",level:"N1"},
{kanji:"根拠",reading:"こんきょ",meaning_vi:"căn cứ, cơ sở",meaning_ja:"konkyo / căn cứ",level:"N1"},
{kanji:"概念",reading:"がいねん",meaning_vi:"khái niệm",meaning_ja:"gainen / khái niệm",level:"N1"},
{kanji:"認識",reading:"にんしき",meaning_vi:"nhận thức",meaning_ja:"ninshiki / nhận thức",level:"N1"},
{kanji:"妥協",reading:"だきょう",meaning_vi:"thỏa hiệp",meaning_ja:"dakyou / thỏa hiệp",level:"N1"},
{kanji:"主張",reading:"しゅちょう",meaning_vi:"chủ trương, lập luận",meaning_ja:"shuchou / chủ trương",level:"N1"},
{kanji:"論理",reading:"ろんり",meaning_vi:"logic, lý luận",meaning_ja:"ronri / lý luận",level:"N1"},
{kanji:"前提",reading:"ぜんてい",meaning_vi:"tiền đề",meaning_ja:"zentei / tiền đề",level:"N1"},
{kanji:"抽象",reading:"ちゅうしょう",meaning_vi:"trừu tượng",meaning_ja:"chuushou / trừu tượng",level:"N1"},
{kanji:"具体的",reading:"ぐたいてき",meaning_vi:"cụ thể",meaning_ja:"gutaiteki / cụ thể",level:"N1"},
{kanji:"一方的",reading:"いっぽうてき",meaning_vi:"một chiều, phiến diện",meaning_ja:"ippoouteki / một chiều",level:"N1"},
{kanji:"積極的",reading:"せっきょくてき",meaning_vi:"tích cực, chủ động",meaning_ja:"sekkyokuteki / tích cực",level:"N1"},
{kanji:"消極的",reading:"しょうきょくてき",meaning_vi:"tiêu cực, thụ động",meaning_ja:"shoukyokuteki / tiêu cực",level:"N1"},
{kanji:"自己中心",reading:"じこちゅうしん",meaning_vi:"ích kỷ, tự cao",meaning_ja:"jikochuushin / ích kỷ",level:"N1"},
];

const ROUND_CONFIG = [
  { pairs: 4, time: 30 },
  { pairs: 4, time: 25 },
  { pairs: 6, time: 40 },
  { pairs: 6, time: 35 },
  { pairs: 8, time: 50 },
  { pairs: 8, time: 45 },
  { pairs: 8, time: 38 },
];
const MAX_LIVES = 3;

let mRound = 0, mStreak = 0, mLives = MAX_LIVES, mTotalPairs = 0;
let mRoundQueue = [], mPairsLeft = 0;
let mSelectedLeft = null, mSelectedRight = null;
let mTimerHandle = null, mTimerStart = 0, mTimeLimit = 30000;
let mMatchAnimating = false;
let mCompoundMode = false;

// DOM refs — gán trong DOMContentLoaded
let leftCol, rightCol, matchTimerBar, matchRoundText, matchPairsLeft;
let matchStreakDisp, matchLivesDisp, matchCombo, matchResult;

document.addEventListener('DOMContentLoaded', () => {
  leftCol        = document.getElementById('left-col');
  rightCol       = document.getElementById('right-col');
  matchTimerBar  = document.getElementById('match-timer-bar');
  matchRoundText = document.getElementById('match-round-text');
  matchPairsLeft = document.getElementById('match-pairs-left');
  matchStreakDisp = document.getElementById('match-streak-display');
  matchLivesDisp = document.getElementById('match-lives');
  matchCombo     = document.getElementById('match-combo-text');
  matchResult    = document.getElementById('match-result');

  // Toggle buttons
  document.getElementById('toggle-compound').addEventListener('click', () => {
    mCompoundMode = !mCompoundMode;
    document.getElementById('toggle-compound').classList.toggle('active', mCompoundMode);
    startMatchGame();
  });
}); // end DOMContentLoaded

function buildCompoundDeck() {
  const seen = new Set();
  const result = [];
  const _enabled = new Set(['N5','N4','N3']);
  const base = (selectedLevel === 'ALL' ? ALL_KANJI : ALL_KANJI.filter(k => k.level === selectedLevel)).filter(k => _enabled.has(k.level));
  for (const k of base) {
    const words = filterWordsForLevel(k.words, selectedLevel);
    for (const w of (words || [])) {
      if (!w.w || seen.has(w.w)) continue;
      if ([...w.w].filter(ch => /[一-鿿]/.test(ch)).length < 2) continue;
      seen.add(w.w);
      result.push({ kanji: w.w, reading: w.r || '', meaning_vi: w.m || '', level: k.level });
    }
  }
  return result.length >= 8 ? result : COMPOUND_WORDS;
}

function getMatchDeck() {
  if (mCompoundMode) return buildCompoundDeck();
  return getFilteredDeck();
}

function stopMatchTimer() {
  clearInterval(mTimerHandle); mTimerHandle = null;
}
function startMatchTimer(limitMs) {
  stopMatchTimer();
  mTimerStart = Date.now();
  mTimeLimit = limitMs;
  matchTimerBar.style.transition = 'none';
  matchTimerBar.style.transform = 'scaleX(1)';
  mTimerHandle = setInterval(() => {
    const elapsed = Date.now() - mTimerStart;
    const ratio = Math.max(0, 1 - elapsed / mTimeLimit);
    matchTimerBar.style.transform = `scaleX(${ratio})`;
    if (elapsed >= mTimeLimit) { stopMatchTimer(); matchTimerOut(); }
  }, 50);
}

function updateMatchHUD() {
  matchStreakDisp.textContent = `🔥 ${mStreak}`;
  matchLivesDisp.textContent = '❤️'.repeat(mLives) + '🖤'.repeat(MAX_LIVES - mLives);
}

function startMatchGame() {
  mRound = 0; mStreak = 0; mLives = MAX_LIVES; mTotalPairs = 0;
  matchResult.classList.remove('visible');
  matchCombo.textContent = '';
  updateMatchHUD();
  loadMatchRound();
}

function loadMatchRound() {
  stopMatchTimer();
  mSelectedLeft = null; mSelectedRight = null; mMatchAnimating = false;
  leftCol.innerHTML = ''; rightCol.innerHTML = '';
  matchCombo.textContent = '';

  const cfg = ROUND_CONFIG[Math.min(mRound, ROUND_CONFIG.length - 1)];
  const pool = shuffle(getMatchDeck());
  // ensure enough items
  const src = pool.slice(0, Math.min(cfg.pairs, pool.length));
  if (src.length < 2) {
    matchRoundText.textContent = 'Không đủ từ vựng cho cấp độ này!';
    return;
  }
  const actualPairs = src.length;

  mRoundQueue = src.map(k => ({
    id: k.kanji,
    kanji: k.kanji,
    reading: k.reading || (k.on && k.on !== '—' ? k.on : k.kun),
    meaning_vi: k.meaning_vi || k.meaning,
    meaning_ja: k.meaning_ja || k.meaning,
  }));
  mPairsLeft = actualPairs;

  matchRoundText.textContent = `Vòng ${mRound + 1} · ${actualPairs} cặp`;
  matchPairsLeft.textContent = `Còn ${mPairsLeft} cặp`;

  const leftItems  = shuffle([...mRoundQueue]);
  const rightItems = shuffle([...mRoundQueue]);

  leftItems.forEach(item => {
    const el = document.createElement('div');
    el.className = 'match-item kanji-item';
    el.dataset.id = item.id;
    el.dataset.side = 'left';
    // Kanji + reading
    el.innerHTML = `<div class="item-kanji">${item.kanji}</div><div class="item-reading">${item.reading || ''}</div>`;
    el.addEventListener('click', () => onMatchTap(el, 'left'));
    leftCol.appendChild(el);
  });

  rightItems.forEach(item => {
    const el = document.createElement('div');
    el.className = 'match-item meaning-item';
    el.dataset.id = item.id;
    el.dataset.side = 'right';
    el.innerHTML = `<div class="item-meaning-vi">${item.meaning_vi}</div>`;
    el.addEventListener('click', () => onMatchTap(el, 'right'));
    rightCol.appendChild(el);
  });

  startMatchTimer(cfg.time * 1000);
}

function onMatchTap(el, side) {
  if (mMatchAnimating) return;
  if (el.classList.contains('matched') || el.classList.contains('empty')) return;
  if (side === 'left') {
    document.querySelectorAll('#left-col .match-item.selected').forEach(e => e.classList.remove('selected'));
    mSelectedLeft = el; el.classList.add('selected');
  } else {
    document.querySelectorAll('#right-col .match-item.selected').forEach(e => e.classList.remove('selected'));
    mSelectedRight = el; el.classList.add('selected');
  }
  if (mSelectedLeft && mSelectedRight) checkMatchPair();
}

function checkMatchPair() {
  mMatchAnimating = true;
  const L = mSelectedLeft, R = mSelectedRight;
  mSelectedLeft = null; mSelectedRight = null;

  if (L.dataset.id === R.dataset.id) {
    mStreak++; mTotalPairs++; mPairsLeft--;
    L.classList.remove('selected'); R.classList.remove('selected');
    L.classList.add('matched'); R.classList.add('matched');
    playTone(660, 'sine', 0.12);
    // Ghi nhận đúng vào unified mastery
    if (window.koeruMastery) window.koeruMastery.record(L.dataset.id, true, 'match');
    // Phát âm kanji khi ghép đúng
    if (soundEnabled && window.speechSynthesis) {
      speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(L.dataset.id);
      utt.lang = 'ja-JP'; utt.rate = 0.9; utt.volume = 0.7;
      speechSynthesis.speak(utt);
    }
    if (mStreak > 1) {
      showComboFloat(`+${mStreak} 🔥`, L);
      matchCombo.textContent = `Combo ×${mStreak}!`;
    } else { matchCombo.textContent = ''; }
    updateMatchHUD();
    matchPairsLeft.textContent = `Còn ${mPairsLeft} cặp`;
    setTimeout(() => {
      L.classList.add('vanish'); R.classList.add('vanish');
      setTimeout(() => {
        L.remove();
        R.remove();
        mMatchAnimating = false;
        if (mPairsLeft === 0) { mRound++; setTimeout(loadMatchRound, 500); }
      }, 300);
    }, 350);
  } else {
    mStreak = 0; mLives--;
    L.classList.remove('selected'); R.classList.remove('selected');
    L.classList.add('wrong'); R.classList.add('wrong');
    matchCombo.textContent = '';
    playTone(180, 'sawtooth', 0.15);
    // Ghi nhận sai vào unified mastery (cả hai kanji bị nhầm)
    if (window.koeruMastery) {
      window.koeruMastery.record(L.dataset.id, false, 'match');
    }
    updateMatchHUD();
    mTimerStart -= 5000;
    setTimeout(() => {
      L.classList.remove('wrong'); R.classList.remove('wrong');
      mMatchAnimating = false;
      if (mLives <= 0) { stopMatchTimer(); showMatchResult(false); }
    }, 400);
  }
}

function matchTimerOut() {
  mLives--; updateMatchHUD(); playTone(180, 'sawtooth', 0.2);
  document.querySelectorAll('.match-item').forEach(el => {
    el.classList.add('wrong');
    setTimeout(() => el.classList.remove('wrong'), 400);
  });
  if (mLives <= 0) { setTimeout(() => showMatchResult(false), 500); }
  else {
    setTimeout(() => {
      const cfg = ROUND_CONFIG[Math.min(mRound, ROUND_CONFIG.length - 1)];
      startMatchTimer(Math.max(15000, cfg.time * 800));
    }, 500);
  }
}

function showMatchResult(win) {
  stopMatchTimer();
  const emoji = mTotalPairs > 15 ? '🏆' : mTotalPairs > 8 ? '👏' : '💪';
  const title = mTotalPairs > 15 ? 'Xuất sắc!' : mTotalPairs > 8 ? 'Không tệ!' : 'Cố lên!';
  document.getElementById('match-result-emoji').textContent = emoji;
  document.getElementById('match-result-title').textContent = title;
  document.getElementById('match-result-score').textContent = `${mTotalPairs} cặp`;
  document.getElementById('match-result-detail').innerHTML =
    `Nối đúng <strong style="color:#22c55e">${mTotalPairs}</strong> cặp · Vòng ${mRound + 1}<br>
     <small style="opacity:.6">Streak cao nhất: ${mStreak} · Chế độ: ${mCompoundMode?'Từ ghép':'Từ đơn'}</small>`;
  matchResult.classList.add('visible');
}

function showComboFloat(text, anchorEl) {
  const rect = anchorEl.getBoundingClientRect();
  const el = document.createElement('div');
  el.className = 'combo-float';
  el.textContent = text;
  el.style.left = (rect.left + rect.width / 2 - 30) + 'px';
  el.style.top  = (rect.top - 10) + 'px';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 800);
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-match-home').addEventListener('click', () => {
    stopMatchTimer();
    showScreen('home-screen');
  });
  document.getElementById('btn-match-home2').addEventListener('click', () => {
    matchResult.classList.remove('visible');
    showScreen('home-screen');
  });
  document.getElementById('btn-match-retry').addEventListener('click', () => {
    matchResult.classList.remove('visible');
    startMatchGame();
  });
});

