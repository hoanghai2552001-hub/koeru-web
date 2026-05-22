// ══════════════════════════════════════════
// INIT
// ══════════════════════════════════════════
applyModeUI();

// ══════════════════════════════════════════
// SPEED KANJI
// ══════════════════════════════════════════

// showScreen extended for SP screens
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  ['s-sph','s-speed','s-spr'].forEach(s=>document.getElementById(s)?.classList.remove('on'));
  const spScreens = ['s-sph','s-speed','s-spr'];
  if(spScreens.includes(id)) {
    document.getElementById(id).classList.add('on');
  } else {
    const el = document.getElementById(id);
    if(el) el.classList.add('active');
  }
}


// ══════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════
const SESSION_DURATION = 5 * 60; // 5 minutes
const BASE_ANSWER_TIME = 6000;   // ms per question start
const MIN_ANSWER_TIME  = 1800;
const COMBO_THRESHOLDS = [3, 6, 10, 15]; // combo levels
const SP_XP_LVL = 150;
const FEVER_COMBO  = 10; // combo needed for fever

// ══════════════════════════════════════════
// STATE
// ══════════════════════════════════════════
let spLvl = 'ALL';
let spDeck = [], spUsed = new Set();
let spCard = null;
let spStr = 0, spMaxStr = 0;
let spCmb = 1, spMaxCmb = 1;
let spSc = 0, spOk = 0, spTot = 0;
let sessionTimeLeft = SESSION_DURATION;
let answerTimeLeft  = BASE_ANSWER_TIME;
let answerStart = 0;
let sessionHandle = null, speedHandle = null;
let isFever = false;
let spAns = false;
let spXpG = 0;

// SRS: track wrong answers this session
let spWrong = []; // [{kanji, meaning, count}]

// Persistent
let pStreak = 0, pBest = 0, pTotal = 0, pXP = 0, pLevel = 1, pDayStreak = 0;

function loadProgress() {
  try {
    const d = JSON.parse(localStorage.getItem('sp_v1') || '{}');
    pBest = d.best || 0; pTotal = d.total || 0;
    pXP = d.xp || 0; pLevel = d.level || 1;
    pDayStreak = d.dayStreak || 0; pStreak = d.streak || 0;
  } catch(e){}
}
function saveProgress() {
  try {
    localStorage.setItem('sp_v1', JSON.stringify({
      best:pBest, total:pTotal, xp:pXP, level:pLevel,
      dayStreak:pDayStreak, streak:pStreak
    }));
  } catch(e){}
}

function ripple(x, y, color) {
  const el=document.createElement('div');
  el.className='ripple';
  el.style.cssText=`left:${x-24}px;top:${y-24}px;width:48px;height:48px;background:${color};`;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(),500);
}
function floatScore(text, color, x, y) {
  const el=document.createElement('div');
  el.className='score-float';
  el.style.cssText=`color:${color};left:${x-20}px;top:${y-10}px;`;
  el.textContent=text;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(),800);
}

// ══════════════════════════════════════════
// BACKGROUND PARTICLES
// ══════════════════════════════════════════
let spCanvas=null, spCtx=null;
let particles = [];
function initCanvas() {
  spCanvas=document.getElementById('sp-canvas');
  if(!spCanvas)return;
  spCtx=spCanvas.getContext('2d');
  spCanvas.width=window.innerWidth;
  spCanvas.height=window.innerHeight;
  particles = Array.from({length:30},()=>({
    x:Math.random()*(spCanvas?.width||300), y:Math.random()*(spCanvas?.height||600),
    r:Math.random()*2+.5, vx:(Math.random()-.5)*.3, vy:(Math.random()-.5)*.3,
    a:Math.random()*.4+.1,
    color:Math.random()>.5?'129,140,248':'244,114,182'
  }));
}
function drawParticles() {
  if(!spCtx||!spCanvas)return;
  spCtx.clearRect(0,0,spCanvas.width,spCanvas.height);
  particles.forEach(p=>{
    spCtx.beginPath();spCtx.arc(p.x,p.y,p.r,0,Math.PI*2);
    spCtx.fillStyle=`rgba(${p.color},${p.a})`;spCtx.fill();
    p.x+=p.vx;p.y+=p.vy;
    if(p.x<0||p.x>(spCanvas?.width||300))p.vx*=-1;
    if(p.y<0||p.y>(spCanvas?.height||600))p.vy*=-1;
  });
  requestAnimationFrame(drawParticles);
}
// canvas deferred to startGame

// ══════════════════════════════════════════
// HOME UI
// ══════════════════════════════════════════
function updateHomeUI() {
  document.getElementById('sp-hs').textContent   = pStreak;
  document.getElementById('sp-hb').textContent     = pBest;
  document.getElementById('sp-ht').textContent    = pTotal;
  document.getElementById('sp-lvlbdg').textContent = `Lv.${pLevel}`;
  document.getElementById('sp-xpf2').style.width = `${(pXP/SP_XP_LVL)*100}%`;
  document.getElementById('sp-xptxt').textContent = `${pXP} / ${SP_XP_LVL} XP`;
}

document.querySelectorAll('.sp-lb').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.sp-lb').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    spLvl = btn.dataset.lvl;
  });
});

document.getElementById('sp-pbtn').addEventListener('click', startGame);
document.getElementById('sp-back').addEventListener('click', ()=>{
  stopGame(); showScreen('home-screen'); updateHomeUI();
});
document.getElementById('sr-retry').addEventListener('click', startGame);
document.getElementById('sr-home').addEventListener('click', ()=>{
  showScreen('home-screen'); updateHomeUI();
});

// ══════════════════════════════════════════
// GAME LOGIC
// ══════════════════════════════════════════
function spGetDeck() {
  return spLvl==='ALL' ? ALL_KANJI : ALL_KANJI.filter(k=>k.level===spLvl);
}

function getAnswerTime() {
  // Decreases as combo increases, floor at MIN
  const reduction = Math.min(spCmb - 1, 12) * 200;
  return Math.max(BASE_ANSWER_TIME - reduction, MIN_ANSWER_TIME);
}

// Chế độ đáp án: 'vn' = tiếng Việt, 'jp' = tiếng Nhật
let spAnswerMode = 'vn';

function startGame() {
  if(!spCanvas){initCanvas();if(spCanvas)drawParticles();}
  stopGame();
  showScreen('s-speed');
  spDeck = shuffle(spGetDeck());
  spUsed.clear(); spWrong = [];
  spStr=0; spMaxStr=0; spCmb=1; spMaxCmb=1;
  spSc=0; spOk=0; spTot=0; sessionXpGained=0;
  isFever=false; isAnswering=false;
  sessionTimeLeft = SESSION_DURATION;
  setFever(false);
  updateHUD();
  // Session countdown
  sessionHandle = setInterval(()=>{
    sessionTimeLeft--;
    updateSessionBar();
    if(sessionTimeLeft<=0){ clearInterval(sessionHandle); endGame(); }
  },1000);
  nextCard();
}

function stopGame() {
  clearInterval(sessionHandle); clearTimeout(speedHandle);
  sessionHandle=null; speedHandle=null;
}

function updateHUD() {
  document.getElementById('sp-sv').textContent = spStr;
  document.getElementById('sp-cv').textContent  = `×${spCmb}`;
  document.getElementById('sp-scv').textContent  = spSc;
  const m=Math.floor(sessionTimeLeft/60), s=sessionTimeLeft%60;
  document.getElementById('sp-tv').textContent   = `${m}:${s.toString().padStart(2,'0')}`;
}
function updateSessionBar() {
  const ratio = sessionTimeLeft/SESSION_DURATION;
  document.getElementById('sp-ss').style.transform=`scaleX(${ratio})`;
  updateHUD();
}

// Speed bar countdown per question
function startSpeedBar() {
  clearTimeout(speedHandle);
  const limit = getAnswerTime();
  answerStart = Date.now();
  const bar = document.getElementById('sp-sb');
  bar.style.transition='none';
  bar.style.transform='scaleX(1)';
  function tick() {
    const elapsed = Date.now()-answerStart;
    const ratio = Math.max(0, 1-elapsed/limit);
    bar.style.transform=`scaleX(${ratio})`;
    if(ratio<=0){ onTimeout(); return; }
    speedHandle = setTimeout(tick, 30);
  }
  speedHandle = setTimeout(tick, 30);
}
function stopSpeedBar() { clearTimeout(speedHandle); }

function setFever(on) {
  isFever = on;
  document.getElementById('sp-fov').classList.toggle('active',on);
  document.getElementById('sp-ft').classList.toggle('visible',on);
  document.getElementById('sp-k').classList.toggle('fever-glow',on);
}

function nextCard() {
  spAns = true;
  // Refill deck if exhausted
  if(spUsed.size>=spDeck.length){ spUsed.clear(); spDeck=shuffle(spGetDeck()); }
  let idx;
  // Bias: 40% chance to replay a wrong card
  const wrongAvail = spWrong.filter(w=>w.count>0);
  if(wrongAvail.length>0 && Math.random()<.4) {
    const w = wrongAvail[Math.floor(Math.random()*wrongAvail.length)];
    idx = spDeck.findIndex(k=>k.kanji===w.kanji);
    if(idx===-1) idx = pickUnused();
  } else { idx = pickUnused(); }
  spUsed.add(idx);
  spCard = spDeck[idx];

  // Animate in
  const stage = document.getElementById('sp-stage');
  stage.style.animation='none'; stage.offsetHeight;
  stage.style.animation='stageIn .25s cubic-bezier(.34,1.56,.64,1)';

  document.getElementById('sp-k').textContent    = spCard.kanji;
  document.getElementById('sp-hv').textContent = spCard.hanviet;
  const reading = spCard.on!=='—'?spCard.on:spCard.kun;
  document.getElementById('sp-rd').textContent = reading;

  renderOptions();
  startSpeedBar();
}

function pickUnused() {
  let tries=0, idx;
  do { idx=Math.floor(Math.random()*spDeck.length); tries++; }
  while(spUsed.has(idx) && tries<spDeck.length);
  return idx;
}

function spGetAns(k) {
  if(spAnswerMode === 'jp') {
    // Ưu tiên Kun reading (hiragana), fallback On reading, cuối cùng meaning VN
    const kun = k.kun && k.kun !== '—' ? k.kun : '';
    const on  = k.on  && k.on  !== '—' ? k.on  : '';
    return kun || on || k.meaning;
  }
  return k.meaning;
}

function renderOptions() {
  const grid = document.getElementById('sp-opts');
  grid.innerHTML='';
  // 1 correct + 3 wrong
  const wrong = shuffle(spDeck.filter(k=>k.kanji!==spCard.kanji)).slice(0,3).map(k=>spGetAns(k));
  const opts   = shuffle([spGetAns(spCard),...wrong]);
  // JP mode: hiện gợi ý nghĩa VN nhỏ bên dưới kanji
  const hint = document.getElementById('sp-jp-hint');
  if(hint) hint.textContent = spAnswerMode==='jp' ? spCard.meaning : '';
  // 2-col grid always
  grid.style.gridTemplateColumns = '1fr 1fr';
  opts.forEach((opt,i)=>{
    const btn=document.createElement('button');
    btn.className=`opt-btn appear-${i+1}`;
    btn.textContent=opt;
    btn.addEventListener('click',(e)=>onAnswer(btn, opt, e));
    grid.appendChild(btn);
  });
}

function onAnswer(btn, chosen, e) {
  if(!spAns) return;
  isAnswering=false;
  stopSpeedBar();
  spTot++;
  const isRight = chosen===spGetAns(spCard);
  const rect=btn.getBoundingClientRect();
  const cx=(rect.left+rect.right)/2, cy=(rect.top+rect.bottom)/2;

  if(isRight) {
    spOk++; spStr++; spMaxStr=Math.max(spMaxStr,spStr);
    spCmb = Math.min(spCmb+1,20); spMaxCmb=Math.max(spMaxCmb,spCmb);
    // Score: base * combo * (speed bonus)
    const elapsed=Date.now()-answerStart;
    const speedBonus=Math.max(1, Math.round(3*(1-elapsed/getAnswerTime())));
    const pts = 10 * spCmb * speedBonus;
    spSc+=pts; spXpG+=Math.max(5, Math.floor(pts/4));

    btn.classList.add('correct');
    ripple(cx,cy,'rgba(16,185,129,.4)');
    floatScore(`+${pts}`, '#6ee7b7', cx, cy-40);
    playTone(660+spCmb*30,'sine',.1);

    // Combo display
    if(spCmb>=3) showComboText();
    // Fever
    if(spCmb>=FEVER_COMBO && !isFever) setFever(true);

    // Remove from wrong list
    const wi=spWrong.findIndex(w=>w.kanji===spCard.kanji);
    if(wi>-1){ spWrong[wi].count=Math.max(0,spWrong[wi].count-1); }

    setTimeout(()=>{ btn.classList.remove('correct'); nextCard(); }, 300);
  } else {
    spStr=0; spCmb=Math.max(1,spCmb-2);
    if(isFever) setFever(false);

    btn.classList.add('wrong');
    // Reveal correct
    document.querySelectorAll('.opt-btn').forEach(b=>{
      if(b.textContent===spGetAns(spCard)) b.classList.add('reveal');
    });
    ripple(cx,cy,'rgba(244,63,94,.4)');
    playTone(200,'sawtooth',.12);

    // Stage shake
    const stage=document.getElementById('sp-stage');
    stage.classList.add('wrong-shake');
    setTimeout(()=>stage.classList.remove('wrong-shake'),400);

    // Add to SRS wrong list
    const wi=spWrong.findIndex(w=>w.kanji===spCard.kanji);
    if(wi>-1) spWrong[wi].count++;
    else spWrong.push({kanji:spCard.kanji,meaning:spCard.meaning,count:2});

    setTimeout(()=>{
      btn.classList.remove('wrong');
      document.querySelectorAll('.opt-btn.reveal').forEach(b=>b.classList.remove('reveal'));
      nextCard();
    }, 700);
  }
  updateHUD();
}

function onTimeout() {
  if(!spAns) return;
  isAnswering=false;
  spTot++; spStr=0; spCmb=Math.max(1,spCmb-1);
  if(isFever) setFever(false);
  // Flash all options briefly
  document.querySelectorAll('.opt-btn').forEach(b=>{
    if(b.textContent===spGetAns(spCard)) b.classList.add('reveal');
  });
  playTone(180,'sawtooth',.1);
  const wi=spWrong.findIndex(w=>w.kanji===spCard.kanji);
  if(wi>-1) spWrong[wi].count++;
  else spWrong.push({kanji:spCard.kanji,meaning:spCard.meaning,count:2});
  setTimeout(()=>{
    document.querySelectorAll('.opt-btn.reveal').forEach(b=>b.classList.remove('reveal'));
    nextCard();
  }, 600);
  updateHUD();
}

function showComboText() {
  const el=document.getElementById('sp-cp');
  const labels={3:'🔥 COMBO!',6:'⚡ SUPER!',10:'💥 FEVER!',15:'🌟 GODLIKE!'};
  const key=COMBO_THRESHOLDS.filter(t=>spCmb>=t).pop()||3;
  const colors={3:'#f472b6',6:'#818cf8',10:'#f59e0b',15:'#10b981'};
  el.textContent=labels[key]||`×${spCmb}`;
  el.style.color=colors[key]||'#f472b6';
  el.classList.remove('show'); el.offsetHeight; el.classList.add('show');
  setTimeout(()=>el.classList.remove('show'),600);
}

// ══════════════════════════════════════════
// END GAME / RESULT
// ══════════════════════════════════════════
function endGame() {
  stopGame(); isAnswering=false; setFever(false);
  const acc = spTot>0 ? Math.round((spOk/spTot)*100) : 0;
  // Grade
  const grade = acc>=95&&maxCombo>=10?'S':acc>=85?'A':acc>=70?'B':acc>=55?'C':'D';
  const emojis={S:'🏆',A:'🔥',B:'✨',C:'👍',D:'💪'};
  const titles={S:'Xuất sắc!',A:'Tuyệt vời!',B:'Không tệ!',C:'Cố lên!',D:'Luyện thêm nhé!'};

  // Update persistent stats
  pBest = Math.max(pBest, spSc);
  pTotal += spOk;
  pStreak= spMaxStr;
  // XP
  const xpGain = sessionXpGained;
  pXP += xpGain;
  while(pXP>=SP_XP_LVL){ pXP-=SP_XP_LVL; pLevel++; }
  saveProgress();

  document.getElementById('sr-e').textContent  = emojis[grade];
  document.getElementById('sr-t').textContent  = titles[grade];
  document.getElementById('sr-g').textContent  = grade;
  document.getElementById('sr-stk').textContent  = maxStreak;
  document.getElementById('sr-cmb').textContent   = `×${spMaxCmb}`;
  document.getElementById('sr-acc').textContent     = acc+'%';
  document.getElementById('sr-xp').textContent      = '+'+xpGain;

  // SRS feedback
  const srsEl=document.getElementById('sr-srs-list');
  const hardCards=spWrong.filter(w=>w.count>0).slice(0,5);
  if(hardCards.length===0){
    srsEl.innerHTML='<div class="srs-item" style="color:var(--ok)">✅ Không có từ nào cần ôn lại!</div>';
  } else {
    srsEl.innerHTML=hardCards.map(w=>`
      <div class="srs-item">
        <span class="kanji">${w.kanji}</span>
        <span class="srs-dot hard"></span>
        <span>${w.meaning}</span>
      </div>`).join('');
  }

  playTone(grade==='S'?1000:grade==='A'?880:660,'triangle',.2);
  showScreen('s-spr');
}

// ══════════════════════════════════════════
// INIT
// ══════════════════════════════════════════
loadProgress();
updateHomeUI();


// Speed Kanji navigation (deferred — elements are after script tag)
document.addEventListener('DOMContentLoaded', () => {
  // Level filter
  document.querySelectorAll('.sp-mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sp-mode-btn').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
      spAnswerMode = btn.dataset.mode;
      const sub = document.getElementById('sp-psub');
      if(sub) sub.textContent = spAnswerMode==='jp'
        ? 'chọn nghĩa tiếng Nhật · combo = nhiều XP'
        : 'tap đúng nghĩa · combo = nhiều XP';
    });
  });
  document.querySelectorAll('.sp-lb').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sp-lb').forEach(b=>b.classList.remove('on'));
      btn.classList.add('on');
      spLvl = btn.dataset.lvl;
    });
  });
  // Buttons
  ['sp-pbtn','sp-back','sr-retry','sr-home'].forEach(id => {
    const el = document.getElementById(id);
    if(!el) return;
    if(id==='sp-pbtn')    el.addEventListener('click', startGame);
    if(id==='sp-back')    el.addEventListener('click', ()=>{ stopGame(); showScreen('home-screen'); });
    if(id==='sr-retry')   el.addEventListener('click', startGame);
    if(id==='sr-home')    el.addEventListener('click', ()=>{ showScreen('home-screen'); spUpdateHome(); });
  });
  // go-speed from main home
  document.getElementById('go-speed')?.addEventListener('click', ()=>{
    showScreen('s-sph'); loadProgress(); spUpdateHome();
  });
  document.getElementById('spr-back')?.addEventListener('click', ()=>{ showScreen('s-sph'); spUpdateHome(); });
  // init display
  loadProgress(); spUpdateHome();
});

function spUpdateHome() {
  document.getElementById('sp-hs').textContent = pStreak;
  document.getElementById('sp-hb').textContent = pBest;
  document.getElementById('sp-ht').textContent = pTotal;
  document.getElementById('sp-lvlbdg').textContent = 'Lv.'+pLevel;
  document.getElementById('sp-xpf2').style.width = (pXP/SP_XP_LVL*100)+'%';
  document.getElementById('sp-xptxt').textContent = pXP+'/'+SP_XP_LVL+' XP';
}


