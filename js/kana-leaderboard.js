/* ════════════════════════════════
   KANA SPEED — Supabase Leaderboard
════════════════════════════════ */

// Keys được quản lý trong js/kana-config.js
const supa = (window.supabase && KANA_CONFIG.leaderboardEnabled)
  ? supabase.createClient(KANA_CONFIG.supabaseUrl, KANA_CONFIG.supabaseKey)
  : null;

let lbFilter  = 'all';
let scoreSaved = false;

async function saveScore() {
  if (!supa) { document.getElementById('save-status').textContent = '⚠️ Leaderboard tạm thời không khả dụng.'; return; }
  const nick = document.getElementById('nickname-input').value.trim();
  if (!nick) { document.getElementById('save-status').textContent = '⚠️ Nhập tên trước nhé!'; return; }

  const btn = document.getElementById('save-btn');
  btn.disabled = true;
  document.getElementById('save-status').textContent = 'Đang lưu…';

  const total       = scoreCorrect + scoreWrong;
  const acc         = total > 0 ? Math.round((scoreCorrect / total) * 100) : 0;
  const scriptLabel = selectedLevel === 3 ? 'vocab' : selectedScript;

  const { error } = await supa.from('scores').insert({
    nickname : nick,
    correct  : scoreCorrect,
    accuracy : acc,
    streak   : maxStreak,
    script   : scriptLabel,
    level    : selectedLevel,
  });

  if (error) {
    document.getElementById('save-status').textContent = '❌ Lỗi: ' + error.message;
    btn.disabled = false;
  } else {
    localStorage.setItem('kana_nickname', nick);
    scoreSaved = true;
    const statusEl = document.getElementById('save-status');
    statusEl.innerHTML =
      '✅ Đã lưu! <span style="color:var(--accent2);cursor:pointer;text-decoration:underline">Xem bảng xếp hạng →</span>';
    statusEl.querySelector('span').addEventListener('click', openLeaderboard);
  }
}

async function openLeaderboard() {
  document.getElementById('lb-overlay').classList.add('show');
  await fetchLeaderboard();
}

function closeLeaderboard() {
  document.getElementById('lb-overlay').classList.remove('show');
}

function closeLbOnOverlay(e) {
  if (e.target === document.getElementById('lb-overlay')) closeLeaderboard();
}

async function switchLbTab(filter, btn) {
  lbFilter = filter;
  document.querySelectorAll('.lb-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  await fetchLeaderboard();
}

async function fetchLeaderboard() {
  const list = document.getElementById('lb-list');
  if (!supa) { list.innerHTML = '<div class="lb-empty">Leaderboard tạm thời không khả dụng.</div>'; return; }
  list.innerHTML = '<div id="lb-loading">Đang tải…</div>';

  let q = supa.from('scores').select('*')
    .order('accuracy', { ascending: false })
    .order('correct',  { ascending: false })
    .limit(20);
  if (lbFilter !== 'all') q = q.eq('level', lbFilter);

  const { data, error } = await q;
  if (error)              { list.innerHTML = `<div class="lb-empty">Lỗi tải dữ liệu 😢</div>`; return; }
  if (!data?.length)      { list.innerHTML = `<div class="lb-empty">Chưa có điểm nào. Hãy là người đầu tiên! 🚀</div>`; return; }

  const medals   = ['🥇','🥈','🥉'];
  const topClass = ['top1','top2','top3'];
  const esc = s => s ? s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') : '';

  list.innerHTML = data.map((row, i) => `
    <div class="lb-row ${topClass[i] || ''}">
      <div class="lb-rank">${medals[i] || '#'+(i+1)}</div>
      <div class="lb-name">${esc(row.nickname)}<br>
        <span class="lb-meta">${row.level === 3 ? '⚡Từ vựng' : 'Trình độ '+row.level} · ${new Date(row.created_at).toLocaleDateString('vi-VN')}</span>
      </div>
      <div class="lb-score">
        <div class="lb-acc">${row.accuracy}%</div>
        <div class="lb-correct">${row.correct} đúng · 🔥${row.streak}</div>
      </div>
    </div>`
  ).join('');
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('lb-home-btn').addEventListener('click', openLeaderboard);
  document.getElementById('lb-close').addEventListener('click', closeLeaderboard);
  document.getElementById('lb-overlay').addEventListener('click', closeLbOnOverlay);
  document.getElementById('save-btn').addEventListener('click', saveScore);
  document.getElementById('nickname-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') saveScore();
  });

  document.getElementById('lb-tab-all').addEventListener('click', function() { switchLbTab('all', this); });
  document.getElementById('lb-tab-1').addEventListener('click', function() { switchLbTab(1, this); });
  document.getElementById('lb-tab-2').addEventListener('click', function() { switchLbTab(2, this); });
  document.getElementById('lb-tab-3').addEventListener('click', function() { switchLbTab(3, this); });
});
