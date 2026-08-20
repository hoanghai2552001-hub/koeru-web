// Engine luyện nói dùng chung: nghe mẫu -> xem chữ -> ghi âm -> nghe lại. Không chấm điểm, không upload.
(function(){
  var _state = null;

  function esc(s){ var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
  function rubyfy(s){ return esc(s).replace(/([一-鿿々]+)\[([ぁ-ゖー]+)\]/g,'<ruby>$1<rt>$2</rt></ruby>'); }
  function jpReading(s){ return (s || '').replace(/[一-鿿々]+\[([ぁ-ゖー]+)\]/g, '$1').replace(/\[[ぁ-ゖー]+\]/g,''); }

  var SAVE_KEY = 'koeru_sp_saved';
  function loadSaved(){ try { return JSON.parse(localStorage.getItem(SAVE_KEY)) || []; } catch(e){ return []; } }
  function storeSaved(list){ localStorage.setItem(SAVE_KEY, JSON.stringify(list)); }
  function itemKey(item){ return (item.jp || item.word || '') + '|' + (item.meaning || ''); }
  function isSaved(item){ return loadSaved().some(function(s){ return itemKey(s) === itemKey(item); }); }
  function toggleSaved(item){
    var list = loadSaved();
    var k = itemKey(item);
    var idx = list.findIndex(function(s){ return itemKey(s) === k; });
    if(idx >= 0){ list.splice(idx, 1); } else { list.push(item); }
    storeSaved(list);
    return idx < 0;
  }

  function ensureUI(){
    if(document.getElementById('sp-overlay')) return;
    var style = document.createElement('style');
    style.id = 'sp-style';
    style.textContent =
      '#sp-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;display:flex;' +
      'align-items:center;justify-content:center;padding:16px}' +
      '#sp-overlay.hidden{display:none}' +
      '.sp-card{background:var(--bg,#0a0d14);color:var(--text,#eef1f6);border:1px solid var(--line,rgba(255,255,255,.08));' +
      'border-radius:var(--radius-md,12px);max-width:420px;width:100%;padding:18px;font-family:inherit}' +
      '.sp-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}' +
      '.sp-progress{font-size:.78rem;color:var(--muted,#8a93a6);font-weight:700}' +
      '.sp-close{background:none;border:none;color:var(--muted,#8a93a6);font-size:1.2rem;cursor:pointer;line-height:1;padding:4px}' +
      '.sp-save{background:none;border:none;color:var(--muted,#8a93a6);font-size:1.1rem;cursor:pointer;line-height:1;padding:4px}' +
      '.sp-save.on{color:var(--gold,#f5c842)}' +
      '.sp-word{text-align:center;padding:18px 8px;background:var(--card2,#1a2230);border-radius:10px;margin-bottom:12px}' +
      '.sp-word .spk{font-size:.72rem;font-weight:800;color:var(--accent,#e8845a);margin-bottom:6px}' +
      '.sp-word .jp{font-size:1.6rem}.sp-word .jp rt{font-size:.5em;color:var(--muted,#8a93a6)}' +
      '.sp-word .jp.sentence{font-size:1.15rem;line-height:1.7}' +
      '.sp-word .meaning{color:var(--muted,#8a93a6);font-size:.9rem;margin-top:6px}' +
      '.sp-row{display:flex;gap:8px;margin-bottom:10px}' +
      '.sp-btn{flex:1;border:1px solid var(--line,rgba(255,255,255,.08));background:var(--card,#121820);' +
      'color:var(--text,#eef1f6);border-radius:10px;padding:11px;font-weight:700;font-size:.88rem;cursor:pointer;font-family:inherit}' +
      '.sp-btn.sp-accent{background:linear-gradient(135deg,var(--accent,#e8845a),var(--accent2,#d4703f));color:#fff;border:none}' +
      '.sp-btn.sp-rec.recording{background:#c0392b;color:#fff;border:none}' +
      '.sp-msg{font-size:.8rem;color:var(--gold,#f5c842);text-align:center;margin:6px 0;min-height:1.1em}' +
      '.sp-playback{width:100%;margin-bottom:10px;display:none}' +
      '.sp-nav{display:flex;gap:8px;justify-content:space-between}' +
      '.sp-nav button{flex:1;border:1px solid var(--line,rgba(255,255,255,.08));background:var(--card,#121820);' +
      'color:var(--text,#eef1f6);border-radius:10px;padding:10px;font-weight:700;cursor:pointer;font-family:inherit}' +
      '.sp-nav button:disabled{opacity:.4;cursor:default}';
    document.head.appendChild(style);

    var overlay = document.createElement('div');
    overlay.id = 'sp-overlay';
    overlay.className = 'sp-overlay hidden';
    overlay.innerHTML =
      '<div class="sp-card">' +
        '<div class="sp-head"><span class="sp-progress" id="spProgress"></span>' +
          '<span><button class="sp-save" id="spSave" data-action="save">☆</button>' +
          '<button class="sp-close" id="spClose" data-action="close">✕</button></span></div>' +
        '<div class="sp-word" id="spWord"></div>' +
        '<div class="sp-row"><button class="sp-btn sp-accent" data-action="sample">🔊 Nghe mẫu</button></div>' +
        '<div class="sp-row"><button class="sp-btn sp-rec" data-action="record">🎙 Ghi âm</button></div>' +
        '<div class="sp-msg" id="spMsg"></div>' +
        '<audio class="sp-playback" id="spPlayback" controls></audio>' +
        '<div class="sp-nav"><button data-action="prev">◀ Trước</button><button data-action="next">Tiếp ▶</button></div>' +
      '</div>';
    document.body.appendChild(overlay);

    overlay.addEventListener('click', function(e){
      if(e.target === overlay){ close(); return; }
      var el = e.target.closest('[data-action]');
      if(!el) return;
      var a = el.dataset.action;
      if(a === 'close') close();
      else if(a === 'sample') playSample();
      else if(a === 'record') toggleRecord();
      else if(a === 'prev') go(-1);
      else if(a === 'next') go(1);
      else if(a === 'save') toggleSaveCurrent();
    });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && _state && !document.getElementById('sp-overlay').classList.contains('hidden')) close();
    });
  }

  function speakJP(text, done){
    if(!window.speechSynthesis){ if(done) done(); return; }
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = 'ja-JP';
    var voices = window.speechSynthesis.getVoices();
    var jp = voices.filter(function(v){ return v.lang === 'ja-JP'; });
    if(jp.length) u.voice = jp[0];
    if(done) u.onend = done;
    if(!voices.length){
      window.speechSynthesis.onvoiceschanged = function(){
        var vs = window.speechSynthesis.getVoices().filter(function(v){ return v.lang === 'ja-JP'; });
        if(vs.length) u.voice = vs[0];
        window.speechSynthesis.speak(u);
      };
    } else {
      window.speechSynthesis.speak(u);
    }
  }

  function fallbackText(item){ return item.jp ? jpReading(item.jp) : item.word; }

  function playSample(){
    var item = _state.items[_state.idx];
    if(!item) return;
    if(item.mp3){
      var a = new Audio(item.mp3);
      a.oncanplaythrough = function(){ a.play().catch(function(){ speakJP(fallbackText(item)); }); };
      a.onerror = function(){ speakJP(fallbackText(item)); };
      a.load();
    } else {
      speakJP(fallbackText(item));
    }
  }

  function toggleSaveCurrent(){
    var item = _state.items[_state.idx];
    if(!item) return;
    var nowSaved = toggleSaved(item);
    var btn = document.getElementById('spSave');
    btn.textContent = nowSaved ? '★' : '☆';
    btn.classList.toggle('on', nowSaved);
  }

  function setMsg(text){
    document.getElementById('spMsg').textContent = text || '';
  }

  function stopStream(){
    if(_state.stream){
      _state.stream.getTracks().forEach(function(t){ t.stop(); });
      _state.stream = null;
    }
  }

  function toggleRecord(){
    var btn = document.querySelector('#sp-overlay [data-action="record"]');
    if(_state.recorder && _state.recorder.state === 'recording'){
      _state.recorder.stop();
      return;
    }
    if(!navigator.mediaDevices || !window.MediaRecorder){
      setMsg('Trình duyệt không hỗ trợ ghi âm.');
      return;
    }
    setMsg('');
    navigator.mediaDevices.getUserMedia({ audio:true }).then(function(stream){
      _state.stream = stream;
      var opts = {};
      if(window.MediaRecorder.isTypeSupported && window.MediaRecorder.isTypeSupported('audio/webm')){
        opts.mimeType = 'audio/webm';
      }
      var rec;
      try { rec = new MediaRecorder(stream, opts); }
      catch(e){ rec = new MediaRecorder(stream); }
      _state.recorder = rec;
      _state.chunks = [];
      rec.ondataavailable = function(e){ if(e.data && e.data.size) _state.chunks.push(e.data); };
      rec.onstop = function(){
        stopStream();
        if(_state.recordedUrl) URL.revokeObjectURL(_state.recordedUrl);
        var blob = new Blob(_state.chunks, { type: rec.mimeType || 'audio/webm' });
        _state.recordedUrl = URL.createObjectURL(blob);
        var pb = document.getElementById('spPlayback');
        pb.src = _state.recordedUrl;
        pb.style.display = 'block';
        btn.textContent = '🎙 Ghi lại';
        btn.classList.remove('recording');
      };
      rec.start();
      btn.textContent = '⏺ Đang ghi... (bấm để dừng)';
      btn.classList.add('recording');
    }).catch(function(err){
      if(err && (err.name === 'NotAllowedError' || err.name === 'NotFoundError')){
        setMsg('Cần cấp quyền micro trong trình duyệt để ghi âm.');
      } else {
        setMsg('Không thể truy cập micro.');
      }
    });
  }

  function render(){
    var item = _state.items[_state.idx];
    document.getElementById('spProgress').textContent = (_state.idx + 1) + '/' + _state.items.length +
      (_state.opts.title ? ' · ' + _state.opts.title : '');
    var isSentence = !!item.jp;
    var jpHtml = isSentence ? rubyfy(item.jp) :
      (item.reading ? '<ruby>' + esc(item.word) + '<rt>' + esc(item.reading) + '</rt></ruby>' : esc(item.word));
    document.getElementById('spWord').innerHTML =
      (item.spk ? '<div class="spk">' + rubyfy(item.spk) + '</div>' : '') +
      '<div class="jp' + (isSentence ? ' sentence' : '') + '">' + jpHtml + '</div>' +
      (item.meaning ? '<div class="meaning">' + esc(item.meaning) + '</div>' : '');
    var saveBtn = document.getElementById('spSave');
    var saved = isSaved(item);
    saveBtn.textContent = saved ? '★' : '☆';
    saveBtn.classList.toggle('on', saved);
    var btn = document.querySelector('#sp-overlay [data-action="record"]');
    btn.textContent = '🎙 Ghi âm';
    btn.classList.remove('recording');
    var pb = document.getElementById('spPlayback');
    pb.style.display = 'none';
    pb.removeAttribute('src');
    if(_state.recordedUrl){ URL.revokeObjectURL(_state.recordedUrl); _state.recordedUrl = null; }
    setMsg('');
    var nav = document.querySelectorAll('#sp-overlay .sp-nav button');
    nav[0].disabled = _state.idx === 0;
    nav[1].disabled = _state.idx === _state.items.length - 1;
  }

  function go(delta){
    if(_state.recorder && _state.recorder.state === 'recording') _state.recorder.stop();
    var next = _state.idx + delta;
    if(next < 0 || next >= _state.items.length) return;
    _state.idx = next;
    render();
  }

  function close(){
    if(!_state) return;
    if(_state.recorder && _state.recorder.state === 'recording') _state.recorder.stop();
    stopStream();
    if(_state.recordedUrl) URL.revokeObjectURL(_state.recordedUrl);
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    document.getElementById('sp-overlay').classList.add('hidden');
    var onClose = _state.opts.onClose;
    _state = null;
    if(onClose) onClose();
  }

  function open(items, opts){
    if(!items || !items.length){ console.warn('SpeakPractice.open: empty items'); return; }
    ensureUI();
    _state = { items: items, idx: 0, opts: opts || {}, stream: null, recorder: null, chunks: [], recordedUrl: null };
    document.getElementById('sp-overlay').classList.remove('hidden');
    render();
  }

  function openSaved(opts){
    var items = loadSaved();
    if(!items.length){ alert('Chưa có từ/câu nào được lưu. Bấm ☆ khi đang luyện nói để lưu lại.'); return; }
    open(items, Object.assign({ title: 'Đã lưu' }, opts || {}));
  }

  function savedCount(){ return loadSaved().length; }

  window.SpeakPractice = { open: open, close: close, openSaved: openSaved, savedCount: savedCount };
})();
