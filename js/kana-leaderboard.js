/* ════════════════════════════════
   KANA SPEED — Supabase Leaderboard
════════════════════════════════ */

const SUPA_URL = 'https://vjcxtnynjpbebhosynkw.supabase.co';
const SUPA_KEY = 'sb_publishable_Hn4Dx5Gt7xuJkt35WRhU9w_aDaUwQHa';
const supa     = supabase.createClient(SUPA_URL, SUPA_KEY);

let lbFilter  = 'all';
let scoreSaved = false;

async function saveScore() {
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
    document.getElementById('save-status').innerHTML =
      '✅ Đã lưu! <span style="color:var(--accent2);cursor:pointer;text-decoration:underline" onclick="openLeaderboard()">Xem bảng xếp hạng →</span>';
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

  list.innerHTML = data.map((row, i) => `
    <div class="lb-row ${topClass[i] || ''}">
      <div class="lb-rank">${medals[i] || '#'+(i+1)}</div>
      <div class="lb-name">${row.nickname}<br>
        <span class="lb-meta">${row.level === 3 ? '⚡Từ vựng' : 'Trình độ '+row.level} · ${new Date(row.created_at).toLocaleDateString('vi-VN')}</span>
      </div>
      <div class="lb-score">
        <div class="lb-acc">${row.accuracy}%</div>
        <div class="lb-correct">${row.correct} đúng · 🔥${row.streak}</div>
      </div>
    </div>`
  ).join('');
}
