// KOERU CRM — Automation Triggers
// Sau khi paste, chạy hàm installTriggers() MỘT LẦN để đăng ký tất cả triggers

// ── Lấy cấu hình từ Script Properties (không hardcode credential) ──
// Setup: Apps Script → Project Settings → Script Properties
//   CRM_SS_ID       : ID của Google Sheet CRM
//   FOUNDER_EMAIL   : Email nhận thông báo
// Xem .env.example để biết danh sách đầy đủ.
function getCrmConfig() {
  const props = PropertiesService.getScriptProperties();
  const ssId   = props.getProperty('CRM_SS_ID');
  const email  = props.getProperty('FOUNDER_EMAIL');
  if (!ssId)  throw new Error('Script Property "CRM_SS_ID" chưa được set. Xem .env.example');
  if (!email) throw new Error('Script Property "FOUNDER_EMAIL" chưa được set. Xem .env.example');
  return { ssId, email };
}

// ─── INSTALL TẤT CẢ TRIGGERS ─────────────────────────────────────────────────
// Chạy hàm này 1 lần duy nhất
function installTriggers() {
  const { ssId } = getCrmConfig();
  // Xoá triggers cũ tránh trùng
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));

  const ss = SpreadsheetApp.openById(ssId);

  // Trigger 1: Form submit → onFormSubmit
  ScriptApp.newTrigger("onFormSubmit")
    .forSpreadsheet(ss)
    .onFormSubmit()
    .create();

  // Trigger 2: Mỗi ngày 8–9h sáng → dailyFollowUp
  ScriptApp.newTrigger("dailyFollowUp")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();

  // Trigger 3: Mỗi ngày 8–9h sáng → retentionCheck
  ScriptApp.newTrigger("retentionCheck")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();

  // Trigger 4: Mỗi ngày 8–9h sáng → paymentReminder
  ScriptApp.newTrigger("paymentReminder")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();

  SpreadsheetApp.getUi().alert("✅ Đã cài 4 triggers thành công!");
}

// ─── TRIGGER 1 — FORM SUBMIT ──────────────────────────────────────────────────
// Khi có người điền Google Form → ghi vào sheet Leads + email notify founder
function onFormSubmit(e) {
  const { ssId, email: FOUNDER_EMAIL } = getCrmConfig();
  const ss = SpreadsheetApp.openById(ssId);
  const leadsSheet = ss.getSheetByName("Leads");

  // Lấy responses từ form
  const responses = e.namedValues;
  const name     = _get(responses, ["Họ tên", "Full name", "Tên"]);
  const phone    = _get(responses, ["SĐT", "Số điện thoại", "Phone"]);
  const email    = _get(responses, ["Email"]);
  const interest = _get(responses, ["Quan tâm đến khóa nào", "Khóa học", "Interest"]);
  const source   = _get(responses, ["Biết KOERU qua đâu", "Nguồn", "Source"]);

  const today = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "dd/MM/yyyy");
  const lastRow = leadsSheet.getLastRow();
  const id = "L" + String(lastRow).padStart(3, "0");

  // Ghi vào sheet Leads — cột A = Timestamp (tự động bởi Form), bắt đầu từ cột B
  const targetRow = lastRow + 1;
  leadsSheet.getRange(targetRow, 2, 1, 9).setValues([[
    name, phone, email, source || "Web", interest || "Chưa rõ",
    "New", "", today, today
  ]]);
  leadsSheet.getRange(targetRow, 11).setValue(id);

  // Email notify founder
  const subject = `🔔 Lead mới: ${name} — ${source || "Web"}`;
  const body = `
Có lead mới vừa đăng ký trên KOERU!

👤 Tên: ${name}
📞 SĐT: ${phone}
📧 Email: ${email}
🎯 Quan tâm: ${interest || "Chưa rõ"}
📣 Nguồn: ${source || "Web"}
📅 Thời gian: ${today}

→ Mở CRM: https://docs.google.com/spreadsheets/d/${SS_ID}
  `;

  GmailApp.sendEmail(FOUNDER_EMAIL, subject, body);
}

// ─── TRIGGER 2 — DAILY FOLLOW-UP ─────────────────────────────────────────────
// Mỗi sáng: list các lead New chưa được liên hệ sau 3+ ngày
function dailyFollowUp() {
  const { ssId, email: FOUNDER_EMAIL } = getCrmConfig();
  const ss = SpreadsheetApp.openById(ssId);
  const sheet = ss.getSheetByName("Leads");
  const data = sheet.getDataRange().getValues();

  const today = new Date();
  const overdue = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (!row[1]) continue; // bỏ hàng trống

    const status    = row[6];
    const createdStr = row[8];
    if (status !== "New" && status !== "Contacted") continue;

    const created = _parseDate(createdStr);
    if (!created) continue;

    const daysSince = Math.floor((today - created) / (1000 * 60 * 60 * 24));
    if (daysSince >= 3) {
      overdue.push({ name: row[1], phone: row[2], interest: row[5], days: daysSince, row: i + 1 });
    }
  }

  if (overdue.length === 0) return;

  const lines = overdue.map(l =>
    `• ${l.name} | ${l.phone} | ${l.interest} | ${l.days} ngày chưa contact (hàng ${l.row})`
  ).join("\n");

  GmailApp.sendEmail(
    FOUNDER_EMAIL,
    `📋 KOERU — ${overdue.length} lead cần follow-up hôm nay`,
    `Danh sách lead chưa được liên hệ sau 3+ ngày:\n\n${lines}\n\n→ Mở CRM: https://docs.google.com/spreadsheets/d/${SS_ID}`
  );
}

// ─── TRIGGER 3 — RETENTION CHECK ─────────────────────────────────────────────
// Mỗi sáng: cập nhật sheet Retention + email nếu có học viên At Risk
function retentionCheck() {
  const { ssId, email: FOUNDER_EMAIL } = getCrmConfig();
  const ss = SpreadsheetApp.openById(ssId);
  const sessionsSheet  = ss.getSheetByName("Sessions");
  const studentsSheet  = ss.getSheetByName("Students");
  const retentionSheet = ss.getSheetByName("Retention");

  const sessions = sessionsSheet.getDataRange().getValues();
  const students = studentsSheet.getDataRange().getValues();
  const today    = new Date();

  // Tính stats per student từ Sessions sheet
  const stats = {};
  for (let i = 1; i < sessions.length; i++) {
    const row = sessions[i];
    if (!row[1]) continue;
    const sid      = row[1]; // Student ID
    const dateStr  = row[0];
    const attended = row[5];
    const homework = row[6];

    if (!stats[sid]) stats[sid] = { lastDate: null, total: 0, hwDone: 0, name: row[2], program: row[3] };
    stats[sid].total++;
    if (homework === "Done") stats[sid].hwDone++;

    const d = _parseDate(dateStr);
    if (d && (!stats[sid].lastDate || d > stats[sid].lastDate)) {
      stats[sid].lastDate = d;
    }
  }

  // Xoá data cũ trong Retention (giữ header)
  const lastRow = retentionSheet.getLastRow();
  if (lastRow > 1) retentionSheet.getRange(2, 1, lastRow - 1, 9).clearContent();

  const atRisk = [];
  let retRow = 2;

  for (const [sid, s] of Object.entries(stats)) {
    const daysSince  = s.lastDate ? Math.floor((today - s.lastDate) / (1000 * 60 * 60 * 24)) : 999;
    const hwRate     = s.total > 0 ? Math.round((s.hwDone / s.total) * 100) : 0;
    const flag       = (daysSince > 7 || hwRate < 50) ? "⚠️ At Risk" : "✅ OK";
    const lastDateFmt = s.lastDate ? Utilities.formatDate(s.lastDate, "Asia/Ho_Chi_Minh", "dd/MM/yyyy") : "—";

    // Tìm buổi còn lại từ Students sheet
    let sessionsRemaining = "—";
    for (let i = 1; i < students.length; i++) {
      if (students[i][0] === sid) {
        const total = parseInt(students[i][7]) || 0;
        const done  = parseInt(students[i][8]) || 0;
        sessionsRemaining = total - done;
        break;
      }
    }

    retentionSheet.getRange(retRow, 1, 1, 9).setValues([[
      sid, s.name, s.program, sessionsRemaining, lastDateFmt, daysSince, hwRate + "%", flag, "None"
    ]]);
    retRow++;

    if (flag === "⚠️ At Risk") atRisk.push({ name: s.name, days: daysSince, hw: hwRate });
  }

  if (atRisk.length === 0) return;

  const lines = atRisk.map(a =>
    `• ${a.name} — vắng ${a.days} ngày, homework ${a.hw}%`
  ).join("\n");

  GmailApp.sendEmail(
    FOUNDER_EMAIL,
    `⚠️ KOERU — ${atRisk.length} học viên có nguy cơ bỏ học`,
    `Danh sách học viên cần chăm sóc hôm nay:\n\n${lines}\n\nGợi ý: nhắn tin cá nhân, không dùng template.\n\n→ Mở CRM: https://docs.google.com/spreadsheets/d/${SS_ID}`
  );
}

// ─── TRIGGER 4 — PAYMENT REMINDER ────────────────────────────────────────────
// Mỗi sáng: check học viên sắp hết hạn trong 3 ngày tới
function paymentReminder() {
  const { ssId, email: FOUNDER_EMAIL } = getCrmConfig();
  const ss = SpreadsheetApp.openById(ssId);
  const sheet = ss.getSheetByName("Students");
  const data = sheet.getDataRange().getValues();
  const today = new Date();

  const expiringSoon = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (!row[1]) continue;

    const endDateStr = row[6];
    const payStatus  = row[10];
    if (!endDateStr || payStatus === "Paid") continue;

    const endDate = _parseDate(endDateStr);
    if (!endDate) continue;

    const daysLeft = Math.floor((endDate - today) / (1000 * 60 * 60 * 24));
    if (daysLeft >= 0 && daysLeft <= 3) {
      expiringSoon.push({ name: row[1], phone: row[2], program: row[4], daysLeft, payStatus: row[10] });
    }
  }

  if (expiringSoon.length === 0) return;

  const lines = expiringSoon.map(s =>
    `• ${s.name} | ${s.phone} | ${s.program} | còn ${s.daysLeft} ngày | ${s.payStatus}`
  ).join("\n");

  GmailApp.sendEmail(
    FOUNDER_EMAIL,
    `💰 KOERU — ${expiringSoon.length} học viên sắp hết hạn`,
    `Danh sách học viên cần nhắc gia hạn:\n\n${lines}\n\n→ Mở CRM: https://docs.google.com/spreadsheets/d/${SS_ID}`
  );
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function _get(obj, keys) {
  for (const k of keys) {
    if (obj && obj[k] && obj[k][0]) return obj[k][0].trim();
  }
  return "";
}

function _parseDate(str) {
  if (!str) return null;
  if (str instanceof Date) return str;
  // dd/MM/yyyy
  const parts = str.toString().split("/");
  if (parts.length === 3) {
    return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
  }
  const d = new Date(str);
  return isNaN(d) ? null : d;
}
