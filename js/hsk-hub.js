/* Trung tâm học tiếng Trung; giữ nguyên kho SRS và tiến độ bài học cũ. */
(function(){
  var view = 'today';
  function lastLesson(){
    var n = load(K('last_lesson'), 1);
    return DATA.some(function(l){ return l.lesson === n; }) ? n : (DATA[0] || {}).lesson;
  }
  function launch(tab, mode){
    var n = lastLesson();
    if(n === undefined) return;
    openLesson(n);
    curTab = tab;
    document.querySelectorAll('.tab').forEach(function(b){ b.classList.toggle('on', b.dataset.tab === tab); });
    renderTab();
    if(mode && tab === 'practice') HSKPractice.start(mode, curLesson, qs('tabContent'));
  }
  function show(next){
    view = ['today','lessons','practice','speak','progress'].indexOf(next) >= 0 ? next : 'today';
    document.querySelectorAll('[data-panel]').forEach(function(p){ p.classList.toggle('hidden', p.dataset.panel !== view); });
    document.querySelectorAll('[data-view]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.view === view)); });
    qs('hubContext').classList.toggle('hidden', view !== 'practice' && view !== 'speak');
    if(view === 'progress'){ renderProgress(); renderSkills(); }
  }
  function renderSkills(){
    var rows = [['match','Nhận diện nghĩa'],['listen','Nghe hiểu'],['pinyin','Nhớ pinyin'],['tone','Thanh điệu'],['write','Viết Hán tự'],['sentence','Dùng mẫu câu']];
    var data = SRS ? SRS.export() : {};
    qs('hubSkills').innerHTML = '<div class="card"><h2>Năng lực đã chứng minh</h2><p class="sub">Chỉ tính kết quả từ bài luyện có đáp án, không tính số lần đã xem thẻ.</p>' + rows.map(function(r){
      var keys = Object.keys(data).filter(function(k){ return k.indexOf('zh:skill:' + r[0] + ':') === 0; });
      var due = keys.filter(function(k){ return SRS.isDue(k); }).length;
      var total = keys.reduce(function(sum, k){ return sum + (data[k].m || 0); }, 0);
      var pct = keys.length ? Math.round(total / (keys.length * 5) * 100) : 0;
      return '<div class="zh-skill-row"><span><b>' + r[1] + '</b><small>' + keys.length + ' mục đã kiểm tra' + (due ? ' · ' + due + ' đến hạn' : '') + '</small></span><span class="zh-skill-meter"><i style="width:' + pct + '%"></i></span><strong>' + pct + '%</strong></div>';
    }).join('') + '<p class="zh-note">Mức phần trăm phản ánh kết quả luyện tập trên thiết bị này. Luyện nói hiện chưa chấm phát âm.</p></div>';
  }
  function render(){
    var all = allWords(), seen = all.filter(function(x){ return mSeen(x.v.h); }).length;
    var due = dueWords().length, last = lastLesson();
    var lesson = lessonOf(last), sample = lesson.vocab[0];
    qs('hubLessonSelect').innerHTML = DATA.map(function(l){ return '<option value="' + l.lesson + '"' + (l.lesson === last ? ' selected' : '') + '>' + lessonShort(l.lesson) + (l.title ? ' · ' + esc(l.title) : '') + ' · ' + l.vocab.length + ' từ</option>'; }).join('');
    qs('hubLessonSelect').onchange = function(){ store(K('last_lesson'), +this.value); render(); };
    var newCount = lesson.vocab.filter(function(v){ return !mSeen(v.h); }).length;
    var planReview = Math.min(8, due), planNew = Math.min(5, newCount);
    var planListen = Math.min(3, lesson.vocab.length), planSpeak = Math.min(2, lesson.vocab.length);
    var minutes = Math.max(8, Math.min(16, 4 + planReview + planNew));
    qs('hubToday').innerHTML = '<div class="zh-welcome"><p class="zh-eyebrow">HÔM NAY · HSK ' + curLevel + '</p><p class="zh-edition">Một lộ trình, học đến đâu rõ đến đó.</p></div><div class="zh-hero"><div><h1>Buổi học hôm nay.<br><em>Khoảng ' + minutes + ' phút.</em></h1><p class="zh-eyebrow">' + lessonShort(last) + (lesson.title ? ' · ' + esc(lesson.title) : '') + '</p><h2>' + (due ? due + ' từ đang đến hạn ôn' : 'Sẵn sàng học nội dung mới') + '</h2>' +
      '<p class="sub">Đi lần lượt qua ôn tập, từ mới, nghe, nói và một bài kiểm tra ngắn.</p><button class="btn btn-main" id="hubContinue">Bắt đầu buổi học <span aria-hidden="true">→</span></button><span class="zh-hero-caption">Tiến độ được lưu trên trình duyệt này</span></div>' +
      '<div class="zh-hero-art">' + (sample ? '<span class="zh-preview-label">TỪ TRONG BÀI</span><strong>' + esc(sample.h) + '</strong><span class="py-hide">' + esc(sample.p) + '</span><small>' + esc(sample.m) + '</small><button id="hubSample" class="play" aria-label="Nghe từ mẫu">♪ Nghe phát âm</button>' : '<strong>学</strong><small>Học từng bước</small>') + '</div></div>' +
      '<div class="zh-stats"><div class="zh-stat"><b>' + seen + '</b><span>Từ đã học</span></div><div class="zh-stat"><b>' + due + '</b><span>Từ đến hạn ôn</span></div><div class="zh-stat"><b>' + newCount + '</b><span>Từ mới trong bài</span></div></div>' +
      '<h2 class="zh-section-title">LỘ TRÌNH BUỔI HỌC</h2><ol class="zh-daily-plan">' +
      '<li><button id="hubReview"><span>01</span><b>Ôn từ đến hạn</b><small>' + (planReview ? planReview + ' từ ưu tiên' : 'Không có từ đến hạn') + '</small></button></li>' +
      '<li><button id="hubLearn"><span>02</span><b>Học từ mới</b><small>' + (planNew ? planNew + ' từ trong ' + lessonShort(last).toLowerCase() : 'Xem lại từ trong bài') + '</small></button></li>' +
      '<li><button id="hubListen"><span>03</span><b>Nghe và nhận diện</b><small>' + planListen + ' từ có đáp án</small></button></li>' +
      '<li><button id="hubTalk"><span>04</span><b>Nói thành tiếng</b><small>' + planSpeak + ' câu/từ để tự nghe lại</small></button></li>' +
      '<li><button id="hubQuiz"><span>05</span><b>Mini test</b><small>Gõ pinyin để kiểm tra trí nhớ chủ động</small></button></li></ol>' +
      '<div class="zh-practice-link"><button class="btn btn-ghost" id="hubPlay">Mở thư viện luyện tập</button><small>Tự chọn game khi muốn luyện thêm.</small></div>';
    qs('hubContinue').onclick = function(){ if(due) openReview('due'); else launch('vocab'); };
    if(sample) qs('hubSample').onclick = function(){ playAudio(this, sample.h, sample.p); };
    qs('hubReview').onclick = function(){ if(due) openReview('due'); else launch('flash'); };
    qs('hubLearn').onclick = function(){ show('lessons'); };
    qs('hubListen').onclick = function(){ launch('practice', 'listen'); };
    qs('hubPlay').onclick = function(){ show('practice'); };
    qs('hubTalk').onclick = function(){ show('speak'); };
    qs('hubQuiz').onclick = function(){ launch('practice', 'pinyin'); };
    qs('hubPractice').innerHTML = '<p class="zh-eyebrow">XƯỞNG THỰC HÀNH</p><h1>Hiểu rồi. Thử dùng nhé.</h1><p class="sub">Ba nhóm kỹ năng cốt lõi: nhận diện, nhớ chủ động, nghe và phát âm. Chọn bài phía trên để bắt đầu.</p><div id="hubGameMenu"></div>';
    HSKPractice.cards(qs('hubGameMenu'), function(tab, mode){ launch(tab, mode); });
    qs('hubSpeakStart').onclick = function(){ var l = lessonOf(lastLesson()); openSpeak(l.vocab, 'HSK ' + curLevel + ' · ' + lessonShort(l.lesson)); };
    qs('hubDialogue').onclick = function(){ launch('dialogue'); };
    renderSkills();
    show(view);
  }
  function backup(){
    var mastery = {}, data = SRS ? SRS.export() : {};
    Object.keys(data).forEach(function(k){ if(k.indexOf('zh:') === 0) mastery[k] = data[k]; });
    var blob = new Blob([JSON.stringify({ format:'koeru-chinese-progress', version:1, exportedAt:Date.now(), mastery:mastery }, null, 2)], {type:'application/json'});
    var url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = 'koeru-chinese-progress.json'; a.click();
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
  }
  async function restore(e){
    var file = e.target.files[0], msg = qs('hubImportStatus');
    if(!file) return;
    try{
      if(file.size > 2000000) throw new Error('Tệp quá lớn (tối đa 2 MB).');
      var d = JSON.parse(await file.text());
      if(d.format !== 'koeru-chinese-progress' || d.version !== 1 || !d.mastery || typeof d.mastery !== 'object' || Array.isArray(d.mastery)) throw new Error('Không đúng định dạng bản sao KOERU Chinese.');
      var current = SRS.export(), count = 0;
      Object.keys(d.mastery).forEach(function(k){
        var v = d.mastery[k];
        if(k.indexOf('zh:') !== 0 || k.length > 250 || !v || !['m','reps','interval','ease','due','seen'].every(function(f){return typeof v[f] === 'number' && Number.isFinite(v[f]) && v[f] >= 0;}) || v.m > 5 || v.ease < 1.3 || v.ease > 2.5 || v.reps > 100000 || v.interval > 100000 || v.seen > Date.now() + 86400000 || v.due > 8640000000000000) throw new Error('Bản sao chứa dữ liệu tiến độ không hợp lệ.');
        if(!current[k] || current[k].seen < v.seen){ current[k] = {m:v.m,reps:v.reps,interval:v.interval,ease:v.ease,due:v.due,seen:v.seen,source:'hsk'}; count++; }
      });
      SRS.import(current);
      renderHome();
      msg.textContent = 'Đã nhập ' + count + ' mục tiến độ. Dữ liệu các ngôn ngữ khác được giữ nguyên.';
    }catch(err){ msg.textContent = err.message || 'Không đọc được bản sao.'; }
    e.target.value = '';
  }
  function init(){
    document.querySelectorAll('[data-view]').forEach(function(b){ b.onclick = function(){ show(b.dataset.view); }; });
    qs('hubExport').onclick = backup;
    qs('hubImport').onchange = restore;
    show(new URLSearchParams(location.search).get('view') || 'today');
  }
  window.HSKHub = { render:render, init:init };
})();
