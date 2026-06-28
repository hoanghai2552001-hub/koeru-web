// ── QUIZ MODULE ─────────────────────────────────────────
(function(){
  let qPool=[], qList=[], qIdx=0, qScore=0, qLv='N5', qAnswers=[];

  function buildPool(lv){
    const data=window.KANJI_DATA||window.ALL_KANJI||[];
    return data.filter(k=>(lv==='ALL'?['N5','N4'].includes(k.level):k.level===lv)&&k.words&&k.words.length>=2);
  }

  function shuffle(a){return [...a].sort(()=>Math.random()-.5)}

  function makeQ(entry,pool,index){
    const types=['A','B','C'];
    const t=types[index%3];
    if(t==='A'){
      const ws=shuffle(pool.filter(e=>e.kanji!==entry.kanji)).slice(0,3).map(e=>e.meaning);
      return{type:'A',badge:'Nghĩa là gì?',label:'Kanji → Nghĩa',entry,opts:shuffle([entry.meaning,...ws]),ans:entry.meaning};
    }
    if(t==='B'){
      const ws=shuffle(pool.filter(e=>e.kanji!==entry.kanji)).slice(0,3).map(e=>e.kanji);
      return{type:'B',badge:'Chọn kanji đúng',label:'Nghĩa → Kanji',entry,question:entry.meaning,opts:shuffle([entry.kanji,...ws]),ans:entry.kanji};
    }
    const w=entry.words[Math.floor(Math.random()*Math.min(entry.words.length,3))];
    const ws2=shuffle(pool.filter(e=>e.kanji!==entry.kanji).flatMap(e=>e.words||[]).filter(x=>x.m!==w.m)).slice(0,3).map(x=>x.m);
    return{type:'C',badge:'Từ vựng → Nghĩa',label:'Từ vựng',entry,word:w,opts:shuffle([w.m,...ws2]),ans:w.m};
  }

  function startQuiz(){
    qPool=buildPool(qLv);
    if(qPool.length<10)return;
    const sample=shuffle(qPool).slice(0,10);
    qList=sample.map((e,i)=>makeQ(e,qPool,i));
    qIdx=0;qScore=0;qAnswers=[];
    document.getElementById('quiz-home').style.display='none';
    document.getElementById('quiz-result').style.display='none';
    document.getElementById('quiz-play').style.display='block';
    renderQ();
  }

  function renderQ(){
    const q=qList[qIdx];
    const pct=(qIdx/qList.length)*100;
    document.getElementById('quiz-prog-bar').style.width=pct+'%';
    document.getElementById('quiz-prog-text').textContent=`Câu ${qIdx+1}/10`;
    document.getElementById('quiz-q-label').textContent=`Câu ${qIdx+1} — ${q.label}`;
    document.getElementById('quiz-badge').textContent=q.badge;
    document.getElementById('quiz-feedback').style.display='none';
    document.getElementById('quiz-next-btn').style.display='none';

    const isB=q.type==='B', isC=q.type==='C';
    document.getElementById('quiz-word-wrap').style.display=isC?'block':'none';
    document.getElementById('quiz-kanji').style.display=isC?'none':'block';
    document.getElementById('quiz-hv').style.display=isC?'none':'block';
    if(isB){
      document.getElementById('quiz-kanji').style.fontSize='1.2rem';
      document.getElementById('quiz-kanji').textContent=q.question;
      document.getElementById('quiz-hv').textContent='';
    } else if(!isC){
      document.getElementById('quiz-kanji').style.fontSize='4.5rem';
      document.getElementById('quiz-kanji').textContent=q.entry.kanji;
      document.getElementById('quiz-hv').textContent=q.entry.hanviet||'';
    } else {
      document.getElementById('quiz-word').textContent=q.word.w;
      document.getElementById('quiz-word-r').textContent=q.word.r;
    }

    const grid=document.getElementById('quiz-opts');
    grid.innerHTML='';
    q.opts.forEach(opt=>{
      const btn=document.createElement('button');
      if(isB){btn.style.fontFamily="'Noto Sans JP',sans-serif";btn.style.fontSize='1.5rem';}
      btn.textContent=opt;
      btn.onclick=()=>checkQ(opt,q);
      grid.appendChild(btn);
    });
  }

  function checkQ(chosen,q){
    const ok=chosen===q.ans;
    if(ok)qScore++;
    document.querySelectorAll('#quiz-opts button').forEach(btn=>{
      btn.disabled=true;
      if(btn.textContent===q.ans)btn.classList.add('q-correct');
      else if(btn.textContent===chosen&&!ok)btn.classList.add('q-wrong');
    });
    const fb=document.getElementById('quiz-feedback');
    fb.style.borderColor=ok?'#22c55e':'#f43f5e';
    fb.style.background=ok?'rgba(34,197,94,.08)':'rgba(244,63,94,.06)';
    document.getElementById('quiz-fb-title').textContent=ok?'✓ Chính xác!':'✗ Chưa đúng — '+q.entry.meaning;
    document.getElementById('quiz-fb-words').innerHTML=(q.entry.words||[]).slice(0,2).map(w=>
      `<span style="color:#f5c842;font-family:'Noto Sans JP',sans-serif">${w.w}</span> <span style="font-size:.72rem;color:rgba(255,255,255,.4)">${w.r}</span> <span style="font-size:.78rem;color:rgba(255,255,255,.6)">— ${w.m}</span>`
    ).join('<br>');
    fb.style.display='block';
    document.getElementById('quiz-next-btn').style.display='block';
    qAnswers.push({k:q.entry.kanji,m:q.entry.meaning,ok,chosen,ans:q.ans});
  }

  function nextQ(){
    qIdx++;
    if(qIdx>=qList.length)showResult();
    else renderQ();
  }

  function showResult(){
    document.getElementById('quiz-prog-bar').style.width='100%';
    document.getElementById('quiz-play').style.display='none';
    document.getElementById('quiz-result').style.display='block';
    const pct=Math.round(qScore/qList.length*100);
    document.getElementById('quiz-score-num').textContent=`${qScore}/10`;
    const missed=qAnswers.filter(a=>!a.ok);
    const [emoji,title,sub]=pct>=80?['🏆','Xuất sắc!',`${pct}% — trình độ rất tốt!`]:
                              pct>=50?['💪','Khá tốt!',`${pct}% — còn cải thiện được!`]:
                                      ['🌱','Cần luyện thêm!',`${pct}% — ôn lại và thử lại nhé!`];
    document.getElementById('quiz-res-emoji').textContent=emoji;
    document.getElementById('quiz-res-title').textContent=title;
    document.getElementById('quiz-res-sub').textContent=sub;
    if(missed.length){
      document.getElementById('quiz-missed-wrap').style.display='block';
      document.getElementById('quiz-missed-list').innerHTML=missed.map(a=>
        `<span style="background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);border-radius:6px;padding:4px 10px;font-size:.8rem;display:flex;align-items:center;gap:5px"><span style="font-family:'Noto Sans JP',sans-serif;font-size:1rem;color:#f87171">${a.k}</span><span style="color:rgba(255,255,255,.4);font-size:.7rem">${a.m}</span></span>`
      ).join('');
    }
    window._quizScore={pct,score:qScore,level:qLv,missed:missed.map(a=>a.k)};
  }

  document.addEventListener('DOMContentLoaded',()=>{
    const goQuiz=document.getElementById('go-quiz');
    if(goQuiz) goQuiz.addEventListener('click',()=>{
      showScreen('quiz-screen');
      document.getElementById('quiz-home').style.display='block';
      document.getElementById('quiz-play').style.display='none';
      document.getElementById('quiz-result').style.display='none';
    });

    const quizBack=document.getElementById('quiz-back');
    if(quizBack) quizBack.addEventListener('click',()=>{showScreen('home-screen');updateHomeProgress();});

    document.querySelectorAll('.quiz-lvl-btn').forEach(btn=>{
      btn.addEventListener('click',()=>{
        document.querySelectorAll('.quiz-lvl-btn').forEach(b=>b.classList.remove('active'));
        btn.classList.add('active');
        qLv=btn.dataset.lv;
      });
    });

    const startBtn=document.getElementById('quiz-start-btn');
    if(startBtn) startBtn.addEventListener('click',startQuiz);

    const nextBtn=document.getElementById('quiz-next-btn');
    if(nextBtn) nextBtn.addEventListener('click',nextQ);

    const againBtn=document.getElementById('quiz-again-btn');
    if(againBtn) againBtn.addEventListener('click',()=>{
      document.getElementById('quiz-result').style.display='none';
      document.getElementById('quiz-missed-wrap').style.display='none';
      document.getElementById('quiz-home').style.display='block';
    });
  });
})();
