// ══════════════════════════════════════
// FLOATING PANEL
// ══════════════════════════════════════
const FP_KEY = 'fp_v1';

function fpLoad() {
  try { return JSON.parse(localStorage.getItem(FP_KEY) || '{}'); } catch(e) { return {}; }
}
function fpSave(data) {
  try { localStorage.setItem(FP_KEY, JSON.stringify(data)); } catch(e) {}
}

// Toggle panel — guard: panel chỉ tồn tại trên trang có fp-toggle
const _fpToggleBtn = document.getElementById('fp-toggle');
const _fpPanel     = document.getElementById('fp-panel');
if (_fpToggleBtn && _fpPanel) {
  _fpToggleBtn.addEventListener('click', () => {
    _fpPanel.classList.toggle('open');
    if (_fpPanel.classList.contains('open')) fpRenderAll();
  });

  // Tabs
  document.querySelectorAll('.fp-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.fp-tab').forEach(t => t.classList.remove('on'));
      document.querySelectorAll('.fp-section').forEach(s => s.classList.remove('on'));
      tab.classList.add('on');
      document.getElementById('fp-' + tab.dataset.tab).classList.add('on');
    });
  });

  // Đóng khi click bên ngoài
  document.addEventListener('click', e => {
    if (_fpPanel.classList.contains('open') && !_fpPanel.contains(e.target) && !_fpToggleBtn.contains(e.target)) {
      _fpPanel.classList.remove('open');
    }
  });
}

// ── Mục tiêu ──
function fpSaveGoal() {
  const data = fpLoad();
  data.goal = document.getElementById('fp-goal-input').value;
  fpSave(data);
  const btn = document.querySelector('.fp-save-btn');
  if (btn) { btn.textContent = '✅ Đã lưu!'; setTimeout(() => btn.textContent = '💾 Lưu', 1500); }
}

function fpAddMilestone() {
  const inp = document.getElementById('fp-ml-inp');
  if (!inp.value.trim()) return;
  const data = fpLoad();
  if (!data.milestones) data.milestones = [];
  data.milestones.push({ text: inp.value.trim(), done: false, id: Date.now() });
  fpSave(data);
  inp.value = '';
  fpRenderGoal();
}

function fpToggleMilestone(id) {
  const data = fpLoad();
  const m = (data.milestones || []).find(m => m.id === id);
  if (m) m.done = !m.done;
  fpSave(data);
  fpRenderGoal();
}

function fpDelMilestone(id) {
  const data = fpLoad();
  data.milestones = (data.milestones || []).filter(m => m.id !== id);
  fpSave(data);
  fpRenderGoal();
}

function fpRenderGoal() {
  const data = fpLoad();
  document.getElementById('fp-goal-input').value = data.goal || '';
  const list = document.getElementById('fp-milestones');
  const items = data.milestones || [];
  if (!items.length) { list.innerHTML = ''; return; }
  list.innerHTML = items.map(m => `
    <div class="fp-ml-item">
      <input type="checkbox" ${m.done ? 'checked' : ''} onchange="fpToggleMilestone(${m.id})">
      <span style="${m.done ? 'text-decoration:line-through;opacity:.5' : ''}">${m.text}</span>
      <button class="fp-ml-del" onclick="fpDelMilestone(${m.id})">✕</button>
    </div>`).join('');
}

// ── Lịch sử ──
function fpLogResult(game, score, grade, detail) {
  const data = fpLoad();
  if (!data.history) data.history = [];
  data.history.unshift({
    game, score, grade, detail,
    date: new Date().toLocaleDateString('vi-VN'),
    time: new Date().toLocaleTimeString('vi-VN', {hour:'2-digit',minute:'2-digit'}),
    ts: Date.now()
  });
  if (data.history.length > 100) data.history = data.history.slice(0, 100);
  fpSave(data);
  // badge — guard: không crash nếu panel chưa mount
  const badge = document.getElementById('fp-badge');
  if (badge) {
    badge.textContent = '!';
    badge.classList.add('on');
    setTimeout(() => badge.classList.remove('on'), 4000);
  }
}

function fpRenderHistory() {
  const data = fpLoad();
  const list = document.getElementById('fp-hist-list');
  const items = data.history || [];
  if (!items.length) {
    list.innerHTML = '<div class="fp-hist-empty">Chưa có kết quả nào.<br>Chơi game để xem lịch sử!</div>';
    return;
  }
  const gradeColor = {S:'#f59e0b',A:'#818cf8',B:'#10b981',C:'#64748b',D:'#ef4444'};
  list.innerHTML = items.slice(0,30).map(h => `
    <div class="fp-hist-item">
      <div>
        <div class="fp-hist-game">${h.game}</div>
        <div class="fp-hist-date">${h.date} ${h.time}</div>
      </div>
      <span class="fp-hist-score">${h.score}</span>
      ${h.grade ? `<span class="fp-hist-grade" style="color:${gradeColor[h.grade]||'#818cf8'}">${h.grade}</span>` : ''}
    </div>`).join('');
}

function fpClearHistory() {
  if (!confirm('Xóa toàn bộ lịch sử kết quả?')) return;
  const data = fpLoad();
  data.history = [];
  fpSave(data);
  fpRenderHistory();
}

// ── Nhật ký ──
function fpAddDiary() {
  const inp = document.getElementById('fp-diary-inp');
  if (!inp.value.trim()) return;
  const data = fpLoad();
  if (!data.diary) data.diary = [];
  data.diary.unshift({
    text: inp.value.trim(),
    date: new Date().toLocaleDateString('vi-VN'),
    time: new Date().toLocaleTimeString('vi-VN', {hour:'2-digit',minute:'2-digit'}),
    ts: Date.now()
  });
  if (data.diary.length > 200) data.diary = data.diary.slice(0, 200);
  fpSave(data);
  inp.value = '';
  fpRenderDiary();
}

function fpRenderDiary() {
  const data = fpLoad();
  const list = document.getElementById('fp-diary-list');
  const items = data.diary || [];
  if (!items.length) {
    list.innerHTML = '<div class="fp-hist-empty">Chưa có ghi chú nào.</div>';
    return;
  }
  list.innerHTML = items.slice(0,50).map(d => `
    <div class="fp-diary-entry">
      <div class="fp-diary-dot"></div>
      <div>
        <div class="fp-diary-text">${d.text}</div>
        <div class="fp-diary-time">${d.date} ${d.time}</div>
      </div>
    </div>`).join('');
}

// ── Từ vựng: Export CSV ──
function fpExportCSV() {
  const headers = ['kanji','hanviet','on','kun','meaning','meaning_jp','level'];
  const rows = ALL_KANJI.map(k =>
    headers.map(h => (k[h]||'').replace(/"/g,'\"')).map(v => `"${v}"`).join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob(['﻿' + csv], {type:'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'kanji_' + new Date().toISOString().slice(0,10) + '.csv';
  a.click();
  fpVocabStat('✅ Đã xuất ' + ALL_KANJI.length + ' từ vựng ra file CSV');
}

// ── Từ vựng: Import CSV ──
function fpShowImport() {
  const data = `<div class="gs-title">Nhập từ vựng từ CSV</div>
    <div class="gs-sub">Mỗi hàng: kanji,hanviet,on,kun,meaning,meaning_jp,level<br>Hàng đầu là header, level = N5/N4/N3/N2/N1</div>
    <textarea class="gs-input" id="gs-csv-paste" rows="6" placeholder="Dán CSV vào đây hoặc..."></textarea>
    <input type="file" id="gs-file" accept=".csv" style="display:none" onchange="fpReadFile(this)">
    <div class="gs-btns">
      <button class="gs-btn primary" onclick="document.getElementById('gs-file').click()">📂 Chọn file CSV</button>
      <button class="gs-btn primary" onclick="fpImportCSV()">⬆ Nhập</button>
      <button class="gs-btn cancel" onclick="gsClose()">Đóng</button>
    </div>
    <div class="gs-status" id="gs-status"></div>`;
  document.getElementById('gs-title').textContent = '';
  document.getElementById('gs-sub').textContent = '';
  document.getElementById('gs-content').innerHTML = data;
  document.getElementById('gs-modal').classList.add('open');
}

function fpReadFile(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById('gs-csv-paste').value = e.target.result;
  };
  reader.readAsText(file, 'UTF-8');
}

// RFC-4180 CSV parser — xử lý đúng field có dấu phẩy bên trong dấu ngoặc kép
function _parseCSVRow(line) {
  const cols = []; let cur = '', inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') {
      if (inQ && line[i+1] === '"') { cur += '"'; i++; }
      else inQ = !inQ;
    } else if (c === ',' && !inQ) { cols.push(cur.trim()); cur = ''; }
    else cur += c;
  }
  cols.push(cur.trim());
  return cols;
}

function fpImportCSV() {
  const raw = document.getElementById('gs-csv-paste')?.value || '';
  if (!raw.trim()) { gsStatus('❌ Chưa có dữ liệu', true); return; }
  try {
    const lines = raw.trim().split(/\r?\n/);
    const headers = _parseCSVRow(lines[0]).map(h => h.toLowerCase().replace(/"/g,'').trim());
    const ki = headers.indexOf('kanji'), mi = headers.indexOf('meaning'), li = headers.indexOf('level');
    if (ki<0||mi<0||li<0) { gsStatus('❌ Thiếu cột kanji/meaning/level', true); return; }
    let added = 0, skipped = 0;
    for (let i=1;i<lines.length;i++) {
      const cols = _parseCSVRow(lines[i]);
      if (!cols[ki]) continue;
      const existing = ALL_KANJI.findIndex(k => k.kanji === cols[ki]);
      const entry = {
        kanji: cols[ki]||'',
        hanviet: cols[headers.indexOf('hanviet')]||'',
        on: cols[headers.indexOf('on')]||'—',
        kun: cols[headers.indexOf('kun')]||'—',
        meaning: cols[mi]||'',
        meaning_jp: cols[headers.indexOf('meaning_jp')]||'',
        level: cols[li]||'N5'
      };
      if (existing>=0) { ALL_KANJI[existing] = entry; skipped++; }
      else { ALL_KANJI.push(entry); added++; }
    }
    gsStatus('✅ Nhập ' + added + ' từ mới, cập nhật ' + skipped + ' từ');
  } catch(e) { gsStatus('❌ Lỗi: ' + e.message, true); }
}

// ── Google Sheet ──
let gsWebAppUrl = '', gsSheetName = 'Kanji';

function fpShowGSheet() {
  const data = fpLoad();
  document.getElementById('gs-title').textContent = 'Kết nối Google Sheet';
  document.getElementById('gs-content').innerHTML = `
    <div class="gs-label">Apps Script Web App URL</div>
    <input class="gs-input" id="gs-url" value="${data.gsUrl||''}" placeholder="https://script.google.com/macros/s/.../exec">
    <div class="gs-label">Tên sheet (mặc định: Kanji)</div>
    <input class="gs-input" id="gs-sheet" value="${data.gsSheet||'Kanji'}">
    <div class="gs-btns">
      <button class="gs-btn primary" onclick="gsTest()">🔍 Test</button>
      <button class="gs-btn primary" onclick="gsPull()">⬇ Kéo từ Sheet</button>
      <button class="gs-btn primary" onclick="gsPush()">⬆ Đẩy lên Sheet</button>
      <button class="gs-btn cancel" onclick="gsClose()">Đóng</button>
    </div>
    <div class="gs-status" id="gs-status"></div>
    <div class="fp-vocab-note" style="margin-top:12px;font-size:.67rem">
      <b>Hướng dẫn tạo Apps Script:</b><br>
      1. Mở Google Sheet → Extensions → Apps Script<br>
      2. Dán code từ <a href="#" onclick="fpShowScript()" style="color:var(--accent)">đây</a><br>
      3. Deploy → Web app → Anyone can access<br>
      4. Sao chép URL → Dán vào ô trên
    </div>`;
  document.getElementById('gs-modal').classList.add('open');
}

function gsGetUrl() {
  const url = document.getElementById('gs-url')?.value?.trim();
  const sheet = document.getElementById('gs-sheet')?.value?.trim() || 'Kanji';
  if (!url) { gsStatus('❌ Chưa nhập URL', true); return null; }
  const data = fpLoad(); data.gsUrl = url; data.gsSheet = sheet; fpSave(data);
  return { url, sheet };
}

async function gsTest() {
  const cfg = gsGetUrl(); if (!cfg) return;
  gsStatus('⏳ Đang kiểm tra...');
  try {
    const r = await fetch(cfg.url + '?action=ping&sheet=' + encodeURIComponent(cfg.sheet));
    const t = await r.text();
    gsStatus('✅ Kết nối OK: ' + t.slice(0,60));
  } catch(e) { gsStatus('❌ Lỗi: ' + e.message, true); }
}

async function gsPull() {
  const cfg = gsGetUrl(); if (!cfg) return;
  gsStatus('⏳ Đang tải từ Google Sheet...');
  try {
    const r = await fetch(cfg.url + '?action=get&sheet=' + encodeURIComponent(cfg.sheet));
    const rows = await r.json();
    if (!Array.isArray(rows)) throw new Error('Dữ liệu không hợp lệ');
    let added=0, updated=0;
    rows.forEach(row => {
      if (!row.kanji||!row.meaning) return;
      const i = ALL_KANJI.findIndex(k=>k.kanji===row.kanji);
      if (i>=0) { ALL_KANJI[i]={...ALL_KANJI[i],...row}; updated++; }
      else { ALL_KANJI.push(row); added++; }
    });
    gsStatus('✅ Kéo về ' + added + ' từ mới, ' + updated + ' cập nhật');
  } catch(e) { gsStatus('❌ Lỗi: ' + e.message, true); }
}

async function gsPush() {
  const cfg = gsGetUrl(); if (!cfg) return;
  gsStatus('⏳ Đang đẩy ' + ALL_KANJI.length + ' từ lên Sheet...');
  try {
    // text/plain avoids CORS preflight (GAS doesn't handle OPTIONS)
    const r = await fetch(cfg.url, {
      method: 'POST',
      body: JSON.stringify({action:'set', sheet:cfg.sheet, data:ALL_KANJI}),
      headers: {'Content-Type':'text/plain'}
    });
    const text = await r.text();
    // Parse response to detect server-side errors
    let json = null;
    try { json = JSON.parse(text); } catch(_) {}
    if (json && json.error) {
      gsStatus('❌ Lỗi từ Sheet: ' + json.error, true);
    } else if (json && json.ok) {
      gsStatus('✅ Đã đẩy ' + (json.written || ALL_KANJI.length) + ' từ lên Sheet thành công!');
    } else {
      gsStatus('⚠️ Phản hồi lạ: ' + text.slice(0, 80), true);
    }
  } catch(e) { gsStatus('❌ Lỗi: ' + e.message, true); }
}

function gsStatus(msg, isErr) {
  const el = document.getElementById('gs-status');
  if (!el) return;
  el.textContent = msg;
  el.className = 'gs-status ' + (isErr ? 'err' : 'ok');
}

function gsClose() {
  document.getElementById('gs-modal').classList.remove('open');
  document.getElementById('gs-content').innerHTML = '';
}

function fpVocabStat(msg) {
  const el = document.getElementById('fp-vocab-stat');
  if (el) el.textContent = msg;
}

function fpShowScript() {
  alert(`// Apps Script cho Google Sheet:\n\nfunction doGet(e) {\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(e.parameter.sheet||'Kanji');\n  if (e.parameter.action==='ping') return ContentService.createTextOutput('OK ' + sheet.getLastRow() + ' rows');\n  const data = sheet.getDataRange().getValues();\n  const headers = data[0];\n  const rows = data.slice(1).map(r => Object.fromEntries(headers.map((h,i)=>[h,r[i]])));\n  return ContentService.createTextOutput(JSON.stringify(rows)).setMimeType(ContentService.MimeType.JSON);\n}\n\nfunction doPost(e) {\n  const body = JSON.parse(e.postData.contents);\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(body.sheet||'Kanji');\n  sheet.clearContents();\n  const headers = ['kanji','hanviet','on','kun','meaning','meaning_jp','level'];\n  sheet.getRange(1,1,1,headers.length).setValues([headers]);\n  const rows = body.data.map(k=>headers.map(h=>k[h]||''));\n  if(rows.length) sheet.getRange(2,1,rows.length,headers.length).setValues(rows);\n  return ContentService.createTextOutput('OK ' + rows.length);\n}`);
}

function fpRenderVocab() {
  fpVocabStat('📚 Tổng: ' + ALL_KANJI.length + ' từ · ' + ALL_KANJI.filter(k=>k.meaning_jp).length + ' có nghĩa JP');
}

function fpRenderAll() {
  fpRenderGoal();
  fpRenderHistory();
  fpRenderDiary();
  fpRenderVocab();
}

// Keyboard: Enter trong input nhật ký / mục tiêu
document.addEventListener('keydown', e => {
  if (e.key==='Enter' && !e.shiftKey) {
    if (document.activeElement.id==='fp-diary-inp') { e.preventDefault(); fpAddDiary(); }
    if (document.activeElement.id==='fp-ml-inp')    { e.preventDefault(); fpAddMilestone(); }
  }
});

// ── Hook vào endGame (Speed Kanji) để tự log lịch sử ──
const _origEndGame = typeof endGame === 'function' ? endGame : null;
if (_origEndGame) {
  window.endGame = function() {
    _origEndGame.apply(this, arguments);
    // Log Speed Kanji result (delayed để DOM cập nhật)
    setTimeout(() => {
      const grade = document.getElementById('sr-g')?.textContent || '';
      const score = document.getElementById('sr-acc')?.textContent || '';
      const xp    = document.getElementById('sr-xp')?.textContent || '';
      if (grade) fpLogResult('⚡ Speed Kanji', score + ' ' + xp, grade, '');
    }, 200);
  };
}

// ── Hook vào showFloorComplete (Kanji Dungeon) để log lịch sử ──
const _origFloorComplete = typeof showFloorComplete === 'function' ? showFloorComplete : null;
if (_origFloorComplete) {
  window.showFloorComplete = function() {
    _origFloorComplete.apply(this, arguments);
    setTimeout(() => {
      const acc = typeof dCorrect !== 'undefined' && typeof dTotal !== 'undefined' && dTotal > 0
        ? Math.round((dCorrect / dTotal) * 100) + '%' : '?%';
      const floor = typeof dFloor !== 'undefined' ? 'Tầng ' + (dFloor - 1) : '';
      fpLogResult('🏰 Kanji Dungeon', acc, null, floor);
    }, 100);
  };
}
