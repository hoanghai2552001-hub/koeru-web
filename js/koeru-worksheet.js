// KOERU — phần dùng chung của phiếu kiểm tra (BTVN): chấm điểm, lưu lịch sử, gửi giáo viên.
// Không phụ thuộc ngôn ngữ — dùng được cho cả bản tiếng Nhật lẫn tiếng Trung.
// window.KoeruWorksheet
(function(){
  // Web App Google Apps Script nhận kết quả (dùng chung mọi môn — phân biệt bằng payload.subject)
  var RESULTS_ENDPOINT = 'https://script.google.com/macros/s/AKfycbyQ6-8R83K5begoutA_uWEN7-eE8DRBqc9jG7mTnm_WOGOpWjgieMtFSFjm5rpJEGAb7g/exec';

  function store(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function load(k, d){ try{ var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }catch(e){ return d; } }

  // So khớp nghĩa: bỏ hoa/thường và khoảng trắng thừa, chấp nhận trả lời là một phần của đáp án
  function normMeaning(s){ return (s || '').trim().toLowerCase().replace(/\s+/g, ' '); }
  function meaningMatch(answer, correct){
    var a = normMeaning(answer), c = normMeaning(correct);
    if(!a) return false;
    if(c.indexOf(a) >= 0 || a.indexOf(c) >= 0) return true;
    // đáp án nhiều nét nghĩa ngăn bằng ";" hoặc "," — đúng một nét là được
    return c.split(/[;,]/).some(function(part){
      part = part.trim();
      return part && (part === a || part.indexOf(a) >= 0 || a.indexOf(part) >= 0);
    });
  }

  function send(payload){
    if(!RESULTS_ENDPOINT) return Promise.resolve(false);
    return fetch(RESULTS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload)
    }).then(function(){ return true; }).catch(function(){ return false; });
  }

  // Gắn dòng trạng thái "đang gửi / đã gửi / thất bại" vào một phần tử có sẵn
  function sendWithStatus(payload, hostEl){
    var el = document.createElement('span');
    el.className = 'ws-send-status';
    el.textContent = ' · Đang gửi cho giáo viên…';
    if(hostEl) hostEl.appendChild(el);
    return send(payload).then(function(ok){
      el.textContent = ok
        ? ' · ✓ Đã gửi cho giáo viên'
        : ' · ✗ Gửi thất bại (kiểm tra mạng, giáo viên sẽ không thấy kết quả này)';
      el.style.color = ok ? 'var(--gold)' : '#e05252';
      return ok;
    });
  }

  function pushHistory(key, rec, max){
    var hist = load(key, []);
    hist.push(rec);
    max = max || 50;
    if(hist.length > max) hist = hist.slice(hist.length - max);
    store(key, hist);
    return hist;
  }
  function getHistory(key){ return load(key, []); }

  function formatDate(iso){
    try{
      var d = new Date(iso);
      var p = function(n){ return (n < 10 ? '0' : '') + n; };
      return p(d.getDate()) + '/' + p(d.getMonth() + 1) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
    }catch(e){ return iso; }
  }

  window.KoeruWorksheet = {
    endpoint: RESULTS_ENDPOINT,
    send: send,
    sendWithStatus: sendWithStatus,
    normMeaning: normMeaning,
    meaningMatch: meaningMatch,
    pushHistory: pushHistory,
    getHistory: getHistory,
    formatDate: formatDate
  };
})();
