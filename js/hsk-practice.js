/* Game ngắn cho bài HSK hiện tại: mỗi lượt ghi riêng tiến độ kỹ năng. */
(function(){
  var active = false, timer = null;
  function escText(s){ return window.ZHText.esc(s || ''); }
  function shuffle(a){
    a = a.slice();
    for(var i = a.length - 1; i > 0; i--){ var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function cards(box, go){
    box.innerHTML =
      '<section class="zh-game-cluster"><div class="zh-game-cluster-head"><span>01</span><div><h2>Nhận diện</h2><p>Nhìn chữ và nối đúng nghĩa.</p></div></div><div class="zh-game-grid">' +
        '<button class="zh-game" data-tab="flash"><span lang="zh" aria-hidden="true">卡</span><b>Flashcard</b><small>Nhìn chữ, nhớ nghĩa rồi lật thẻ kiểm tra.</small><em>Lặp lại ngắt quãng</em></button>' +
        '<button class="zh-game" data-tab="practice" data-mode="match"><span lang="zh" aria-hidden="true">合</span><b>Ghép từ</b><small>Ghép chữ Hán với nghĩa Việt.</small><em>Liên kết hai chiều</em></button>' +
      '</div></section>' +
      '<section class="zh-game-cluster"><div class="zh-game-cluster-head"><span>02</span><div><h2>Nhớ chủ động</h2><p>Tự tạo đáp án, không chỉ nhìn và đoán.</p></div></div><div class="zh-game-grid">' +
        '<button class="zh-game" data-tab="practice" data-mode="pinyin"><span lang="zh" aria-hidden="true">音</span><b>Gõ pinyin</b><small>Nhập âm đọc bằng dấu hoặc số thanh.</small><em>Active recall</em></button>' +
        '<button class="zh-game" data-tab="quiz"><span lang="zh" aria-hidden="true">测</span><b>Quiz tổng hợp</b><small>Đổi chiều Hán tự, nghĩa và pinyin.</small><em>Kiểm tra xen kẽ</em></button>' +
      '</div></section>' +
      '<section class="zh-game-cluster"><div class="zh-game-cluster-head"><span>03</span><div><h2>Nghe &amp; phát âm</h2><p>Phân biệt âm, chữ và thanh điệu.</p></div></div><div class="zh-game-grid">' +
        '<button class="zh-game" data-tab="practice" data-mode="listen"><span lang="zh" aria-hidden="true">听</span><b>Nghe chọn từ</b><small>Nghe audio rồi nhận diện chữ Hán.</small><em>Nghe hiểu</em></button>' +
        '<button class="zh-game" data-tab="tone"><span lang="zh" aria-hidden="true">调</span><b>Thanh điệu</b><small>Nghe và chọn thanh đầu của từ.</small><em>Phân biệt thanh</em></button>' +
        '<a class="zh-game" href="pinyin.html"><span lang="zh" aria-hidden="true">拼</span><b>Pinyin Speed</b><small>Luyện nhanh âm đầu, vận mẫu và thanh điệu.</small><em>Mở phòng luyện riêng ↗</em></a>' +
      '</div></section>';
    box.querySelectorAll('button[data-tab]').forEach(function(b){
      b.onclick = function(){ go(b.dataset.tab, b.dataset.mode || ''); };
    });
  }
  function menu(l, box){
    box.innerHTML = '<h2>Chọn game cho ' + escText(l.title || ('bài ' + l.lesson)) + '</h2><p class="sub">Kết quả sẽ bổ sung vào lịch ôn của kỹ năng tương ứng.</p><div id="lessonGames"></div>';
    cards(box.querySelector('#lessonGames'), function(tab, mode){
      if(tab !== 'practice'){
        curTab = tab; document.querySelectorAll('.tab').forEach(function(b){ b.classList.toggle('on', b.dataset.tab === tab); }); renderTab(); return;
      }
      start(mode, l, box);
    });
  }
  function eligible(l, mode){
    var pool = l.vocab || [];
    if(mode === 'sentence') pool = pool.filter(function(v){ return v.ex_zh && (v.ex_zh.match(/[一-鿿]/g) || []).length >= 2; });
    return pool;
  }
  function start(mode, l, box){
    stop(); active = true;
    var pool = eligible(l, mode);
    if(!pool.length || ((mode === 'match' || mode === 'listen') && pool.length < 2)){ active = false; box.innerHTML = '<p class="sub">Bài này chưa đủ từ cho game đã chọn. Hãy chọn một bài khác hoặc luyện pinyin.</p>'; return; }
    if(mode === 'sentence' && !pool.length){ box.innerHTML = '<p class="sub">Bài này chưa có câu ví dụ để xếp câu.</p>'; return; }
    if(mode === 'match') match(l, box, pool); else if(mode === 'listen') listen(l, box, pool); else if(mode === 'pinyin') pinyin(l, box, pool); else sentence(l, box, pool);
  }
  function done(box, title, score, total){
    active = false;
    box.innerHTML = '<div class="zh-round"><span class="badge">HOÀN THÀNH</span><h2>' + title + '</h2><p class="sub">Kết quả: <b class="pct-ok">' + score + '/' + total + '</b>. Tiến độ kỹ năng đã được ghi lại trên thiết bị.</p><button class="btn btn-main" id="againGame">Chơi lại</button><button class="btn btn-ghost" id="backGames">Chọn game khác</button></div>';
    qs('againGame').onclick = function(){ start(box.dataset.mode, curLesson, box); };
    qs('backGames').onclick = function(){ menu(curLesson, box); };
  }
  function nextButton(box, callback){
    var b = document.createElement('button'); b.className = 'btn btn-main'; b.textContent = 'Câu tiếp →';
    b.onclick = function(){ if(!active) return; b.disabled = true; callback(); };
    box.querySelector('.zh-round').appendChild(b);
  }
  function match(l, box, pool){
    box.dataset.mode = 'match'; var deck = shuffle(pool).slice(0, Math.min(6, pool.length)), word = null, meaning = null, score = 0;
    box.innerHTML = '<div class="zh-round"><p class="zh-eyebrow">Ghép từ · ' + deck.length + ' cặp</p><h2>Chọn chữ Hán rồi chọn nghĩa tương ứng</h2><div class="zh-match"><div class="zh-options" id="matchWords"></div><div class="zh-options" id="matchMeans"></div></div><p class="zh-feedback" id="matchMsg" role="status">Chọn một chữ Hán để bắt đầu.</p></div>';
    var words = qs('matchWords'), means = qs('matchMeans'), msg = qs('matchMsg');
    words.innerHTML = shuffle(deck).map(function(v){ return '<button data-h="' + escText(v.h) + '">' + escText(v.h) + '</button>'; }).join('');
    means.innerHTML = shuffle(deck).map(function(v){ return '<button data-h="' + escText(v.h) + '">' + escText(v.m) + '</button>'; }).join('');
    function choose(){
      if(!word || !meaning) return;
      var ok = word.dataset.h === meaning.dataset.h, v = deck.filter(function(x){return x.h === word.dataset.h;})[0];
      mRecord(v.h, ok, 'match');
      if(ok){ score++; word.classList.add('matched'); meaning.classList.add('matched'); word.disabled = true; meaning.disabled = true; msg.className = 'zh-feedback good'; msg.textContent = 'Đúng: ' + v.h + ' — ' + v.m; word = meaning = null; if(score === deck.length) timer = setTimeout(function(){ done(box, 'Ghép từ xong rồi', score, deck.length); }, 500); }
      else { msg.className = 'zh-feedback retry'; msg.textContent = 'Chưa đúng. Thử lại một cặp khác.'; word.classList.remove('selected'); meaning.classList.remove('selected'); word = meaning = null; }
    }
    words.querySelectorAll('button').forEach(function(b){ b.onclick = function(){ words.querySelectorAll('.selected').forEach(function(x){x.classList.remove('selected');}); word=b; b.classList.add('selected'); choose(); }; });
    means.querySelectorAll('button').forEach(function(b){ b.onclick = function(){ means.querySelectorAll('.selected').forEach(function(x){x.classList.remove('selected');}); meaning=b; b.classList.add('selected'); choose(); }; });
  }
  function quizRound(mode, l, box, pool, prompt, optionText, skill){
    box.dataset.mode = mode; var deck = shuffle(pool).slice(0, Math.min(8, pool.length)), i = 0, score = 0;
    function render(){
      if(!active) return; if(i >= deck.length){ done(box, mode === 'listen' ? 'Luyện nghe xong rồi' : 'Luyện pinyin xong rồi', score, deck.length); return; }
      var v = deck[i], options = shuffle(shuffle(pool.filter(function(x){return x.h !== v.h;})).slice(0,3).concat([v]));
      box.innerHTML = '<div class="zh-round"><p class="zh-eyebrow">' + (i+1) + '/' + deck.length + ' · Đúng ' + score + '</p><h2>' + prompt(v) + '</h2><div class="zh-options">' + options.map(function(o){return '<button data-h="' + escText(o.h) + '">' + optionText(o) + '</button>';}).join('') + '</div><p class="zh-feedback" id="roundMsg" role="status"></p></div>';
      if(mode === 'listen'){ var play = document.createElement('button'); play.className='btn btn-ghost'; play.textContent='🔊 Nghe lại'; box.querySelector('.zh-round').insertBefore(play, box.querySelector('.zh-options')); play.onclick=function(){playAudio(null,v.h,v.p);}; playAudio(null,v.h,v.p); }
      box.querySelectorAll('.zh-options button').forEach(function(b){ b.onclick = function(){
        box.querySelectorAll('.zh-options button').forEach(function(x){x.disabled=true;}); var ok=b.dataset.h===v.h; mRecord(v.h,ok,skill); if(ok)score++; var msg=qs('roundMsg'); msg.className='zh-feedback '+(ok?'good':'retry'); msg.textContent=(ok?'Đúng rồi: ':'Đáp án: ')+v.h+' · '+v.p+' — '+v.m; nextButton(box,function(){i++;render();});
      }; });
    } render();
  }
  function listen(l,box,pool){ quizRound('listen',l,box,pool,function(){return 'Bạn nghe thấy từ nào?';},function(o){return escText(o.h);},'listen'); }
  function pinyin(l, box, pool){
    box.dataset.mode = 'pinyin'; var deck = shuffle(pool).slice(0, Math.min(8, pool.length)), i = 0, score = 0;
    function render(){
      if(!active) return; if(i >= deck.length){ done(box, 'Luyện pinyin xong rồi', score, deck.length); return; }
      var v = deck[i];
      box.innerHTML = '<div class="zh-round"><p class="zh-eyebrow">' + (i + 1) + '/' + deck.length + ' · Đúng ' + score + '</p><div class="zh-word">' + escText(v.h) + '</div><p class="sub">Gõ pinyin. Có thể dùng dấu: nǐ hǎo, hoặc số thanh: ni3 hao3.</p><input class="search" id="pyInput" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="Ví dụ: nǐ hǎo hoặc ni3 hao3"><button class="btn btn-main" id="checkPy">Kiểm tra</button><button class="btn btn-ghost" id="playPy">🔊 Nghe lại</button><p class="zh-feedback" id="pyMsg" role="status"></p></div>';
      function normalized(s){
        var marks = {a:'āáǎà',e:'ēéěè',i:'īíǐì',o:'ōóǒò',u:'ūúǔù','ü':'ǖǘǚǜ'};
        return (s || '').normalize('NFC').toLowerCase().replace(/u:|v/g,'ü')
          .replace(/([a-zü]+)([0-5])/g,function(_,syllable,tone){
            if(tone === '0' || tone === '5') return syllable;
            var index = syllable.indexOf('a');
            if(index < 0) index = syllable.indexOf('e');
            if(index < 0 && syllable.indexOf('ou') >= 0) index = syllable.indexOf('o');
            if(index < 0){ for(var j=syllable.length-1;j>=0;j--){ if(marks[syllable[j]]){index=j;break;} } }
            return index < 0 ? syllable + tone : syllable.slice(0,index) + marks[syllable[index]][Number(tone)-1] + syllable.slice(index+1);
          }).replace(/[\s·'’]+/g,'');
      }
      function check(){
        var input = qs('pyInput'); if(input.disabled) return;
        if(!input.value.trim()){ qs('pyMsg').textContent = 'Nhập pinyin trước khi kiểm tra nhé.'; input.focus(); return; }
        var accepted = v.p.split(/[()（）]/).filter(function(part){return part.trim();}).map(normalized);
        var ok = accepted.indexOf(normalized(input.value)) >= 0; mRecord(v.h, ok, 'pinyin'); if(ok) score++;
        input.disabled = true; qs('checkPy').disabled = true; var msg = qs('pyMsg'); msg.className = 'zh-feedback ' + (ok ? 'good' : 'retry'); msg.textContent = ok ? 'Đúng rồi: ' + v.p : 'Đáp án: ' + v.p;
        nextButton(box, function(){ i++; render(); });
      }
      qs('checkPy').onclick = check; qs('pyInput').onkeydown = function(e){ if(e.key === 'Enter') check(); }; qs('playPy').onclick = function(){ playAudio(null, v.h, v.p); }; qs('pyInput').focus();
    } render();
  }
  function sentence(l, box, pool){
    box.dataset.mode='sentence'; var deck=shuffle(pool).slice(0,Math.min(5,pool.length)),i=0,score=0;
    function render(){
      if(!active)return; if(i>=deck.length){done(box,'Xếp câu xong rồi',score,deck.length);return;}
      var v=deck[i], chars=(v.ex_zh.match(/[一-鿿]|[0-9]+|[A-Za-z]+/g)||[]), shuffled=shuffle(chars), answer=[];
      box.innerHTML='<div class="zh-round"><p class="zh-eyebrow">'+(i+1)+'/'+deck.length+' · Đúng '+score+'</p><h2>Xếp lại câu theo đúng thứ tự</h2><p class="sub">'+escText(v.ex_vi||v.m)+'</p><div class="zh-tokens" id="sentTokens">'+shuffled.map(function(c,n){return '<button class="zh-token" data-i="'+n+'">'+escText(c)+'</button>';}).join('')+'</div><div class="zh-answer" id="sentAnswer">Chạm từng chữ để xếp câu</div><button class="btn btn-main" id="checkSentence" disabled>Kiểm tra</button><p class="zh-feedback" id="sentMsg" role="status"></p></div>';
      var chosen = [], undo = document.createElement('button');
      undo.className = 'btn btn-ghost'; undo.textContent = 'Bỏ chữ cuối'; undo.disabled = true;
      qs('checkSentence').before(undo);
      undo.onclick = function(){ if(!chosen.length) return; chosen.pop().disabled = false; answer.pop(); qs('sentAnswer').textContent = answer.join('') || 'Chạm từng chữ để xếp câu'; qs('checkSentence').disabled = true; undo.disabled = !chosen.length; };
      qs('sentTokens').querySelectorAll('button').forEach(function(b){b.onclick=function(){answer.push(b.textContent);chosen.push(b);undo.disabled=false;b.disabled=true;qs('sentAnswer').textContent=answer.join('');qs('checkSentence').disabled=answer.length!==chars.length;};});
      qs('checkSentence').onclick=function(){if(this.disabled)return;var ok=answer.join('')===chars.join('');mRecord(v.h,ok,'sentence');if(ok)score++;this.disabled=true;undo.disabled=true;var msg=qs('sentMsg');msg.className='zh-feedback '+(ok?'good':'retry');msg.textContent=(ok?'Đúng rồi: ':'Đáp án: ')+v.ex_zh;nextButton(box,function(){i++;render();});};
    }render();
  }
  function stop(){ active=false; clearTimeout(timer); timer=null; }
  window.HSKPractice={cards:cards,menu:menu,start:start,stop:stop};
})();
