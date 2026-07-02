/**
 * KOERU — Google Apps Script cho Exam Results
 *
 * HƯỚNG DẪN DEPLOY:
 * 1. Mở Google Sheet → Extensions → Apps Script
 * 2. Xóa code mặc định, paste toàn bộ file này vào
 * 3. (SPREADSHEET_ID đã điền sẵn bên dưới)
 * 4. Deploy → Manage deployments → Edit (✏️) → Version: New version → Deploy
 *    (redeploy thì code mới mới có hiệu lực; webhook URL giữ nguyên)
 *
 * GHI CHÚ: Không cần xóa tab thủ công. Khi gặp tab cũ (thiếu cột 'Mã KQ'),
 * script tự chèn cột vào đầu nên dữ liệu cũ không bị lệch.
 */

const SPREADSHEET_ID = '1K8wr7NjFl1XyLL36xz7p8cq2BI8uYSrkQ3ryJm-CcMk';
const SHEET_NAME = 'Kết quả thi N4';
const DETAIL_SHEET_NAME = 'Chi tiết câu trả lời';

const SUMMARY_HEADER = [
  'Mã KQ', 'Thời gian', 'Học sinh', 'Mã đề',
  'Đúng', 'Sai', 'Thời gian làm',
  'Phần A (18)', 'Phần B1 (14)', 'Phần B2 (8)',
  'Rời tab', 'Rời chuột', 'Câu nhanh (<8s)',
  'TB giây/câu', 'AI Risk'
];
const DETAIL_HEADER = [
  'Mã KQ', 'Thời gian', 'Học sinh', 'Mã đề',
  'Câu', 'Phần', 'Đáp án chọn', 'Đáp án đúng', 'Kết quả'
];

function styleHeader(sheet, ncols) {
  const h = sheet.getRange(1, 1, 1, ncols);
  h.setFontWeight('bold');
  h.setBackground('#1a1d27');
  h.setFontColor('#ffffff');
  sheet.setFrozenRows(1);
}

// Đảm bảo tab tổng hợp tồn tại + có cột 'Mã KQ' ở đầu (tự migrate tab cũ)
function ensureSummarySheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(SUMMARY_HEADER);
    styleHeader(sheet, SUMMARY_HEADER.length);
    return sheet;
  }
  // Tab cũ (header bắt đầu bằng 'Thời gian') → chèn cột 'Mã KQ' vào trước
  const firstCell = sheet.getRange(1, 1).getValue();
  if (firstCell !== 'Mã KQ') {
    sheet.insertColumnBefore(1);
    sheet.getRange(1, 1, 1, SUMMARY_HEADER.length).setValues([SUMMARY_HEADER]);
    styleHeader(sheet, SUMMARY_HEADER.length);
  }
  return sheet;
}

// Đảm bảo tab chi tiết tồn tại + header đúng
function ensureDetailSheet(ss) {
  let detail = ss.getSheetByName(DETAIL_SHEET_NAME);
  if (!detail) {
    detail = ss.insertSheet(DETAIL_SHEET_NAME);
    detail.appendRow(DETAIL_HEADER);
    styleHeader(detail, DETAIL_HEADER.length);
    return detail;
  }
  // Tab cũ (header 'Mã lần thi') → đổi nhãn header thành chuẩn mới
  const firstCell = detail.getRange(1, 1).getValue();
  if (firstCell !== 'Mã KQ') {
    detail.getRange(1, 1, 1, DETAIL_HEADER.length).setValues([DETAIL_HEADER]);
    styleHeader(detail, DETAIL_HEADER.length);
  }
  return detail;
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

    const sheet = ensureSummarySheet(ss);
    sheet.appendRow([
      data.resultCode,
      data.date,
      data.student,
      'Mã 0' + data.examId,
      data.correct,
      data.wrong,
      data.duration,
      data.secA + '/18',
      data.secB1 + '/14',
      data.secB2 + '/8',
      data.tabSwitches,
      data.mouseLeaves,
      data.fastAnswers,
      data.avgSecs + 's',
      data.aiRisk === 'high' ? '🚨 Cao' : data.aiRisk === 'medium' ? '⚠️ TB' : '✅ Thấp'
    ]);

    // Color-code AI risk column (col 15)
    const lastRow = sheet.getLastRow();
    const riskCell = sheet.getRange(lastRow, 15);
    if (data.aiRisk === 'high') riskCell.setBackground('#3a1010').setFontColor('#f25f5c');
    else if (data.aiRisk === 'medium') riskCell.setBackground('#3a2e10').setFontColor('#f5a623');
    else riskCell.setBackground('#1a3a25').setFontColor('#34c97b');

    // Ghi chi tiết từng câu vào tab riêng (mỗi câu = 1 dòng)
    if (data.items && data.items.length) {
      const detail = ensureDetailSheet(ss);
      const rows = data.items.map(function (it) {
        return [
          data.resultCode,
          data.date,
          data.student,
          'Mã 0' + data.examId,
          it.no,
          it.sec,
          it.pick,
          it.ans,
          it.ok ? '✅ Đúng' : '❌ Sai'
        ];
      });
      detail.getRange(detail.getLastRow() + 1, 1, rows.length, DETAIL_HEADER.length).setValues(rows);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', row: lastRow }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// (Tùy chọn) Chạy 1 lần trong editor để xóa sạch & tạo lại 2 tab với header mới.
// CẢNH BÁO: xóa toàn bộ dữ liệu trong 2 tab.
function setupSheets() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  [SHEET_NAME, DETAIL_SHEET_NAME].forEach(function (name) {
    const old = ss.getSheetByName(name);
    if (old) ss.deleteSheet(old);
  });
  ensureSummarySheet(ss);
  ensureDetailSheet(ss);
  Logger.log('Đã tạo lại 2 tab với header chuẩn.');
}

// Test function — chạy thủ công trong Apps Script editor để kiểm tra
function testDoPost() {
  const mockData = {
    attemptId: Date.now(),
    resultCode: 'KOERU-E1-35-TEST1',
    date: new Date().toLocaleString('vi-VN'),
    student: 'Test Student',
    examId: 1,
    correct: 35, wrong: 5,
    duration: '55m30s',
    secA: 16, secB1: 12, secB2: 7,
    tabSwitches: 1, mouseLeaves: 3,
    fastAnswers: 0, avgSecs: 90.5,
    aiRisk: 'low',
    items: [
      { no: 1, sec: 'A', pick: 2, ans: 2, ok: 1 },
      { no: 2, sec: 'A', pick: 1, ans: 4, ok: 0 },
      { no: 19, sec: 'B1', pick: '—', ans: 2, ok: 0 }
    ]
  };
  const mock = { postData: { contents: JSON.stringify(mockData) } };
  const result = doPost(mock);
  Logger.log(result.getContent());
}
