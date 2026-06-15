/**
 * KOERU — Google Apps Script cho Exam Results
 *
 * HƯỚNG DẪN DEPLOY:
 * 1. Mở Google Sheet (hoặc tạo sheet mới)
 * 2. Extensions → Apps Script
 * 3. Xóa code mặc định, paste toàn bộ file này vào
 * 4. Thay SPREADSHEET_ID bên dưới bằng ID sheet của bạn
 * 5. Deploy → New deployment → Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 6. Copy URL deployment → paste vào exam.html, dòng:
 *    const SHEETS_WEBHOOK = 'https://script.google.com/macros/s/...';
 */

const SPREADSHEET_ID = '1K8wr7NjFl1XyLL36xz7p8cq2BI8uYSrkQ3ryJm-CcMk';
const SHEET_NAME = 'Kết quả thi N4';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow([
        'Thời gian', 'Học sinh', 'Mã đề',
        'Đúng', 'Sai', 'Thời gian làm',
        'Phần A (18)', 'Phần B1 (14)', 'Phần B2 (8)',
        'Rời tab', 'Rời chuột', 'Câu nhanh (<8s)',
        'TB giây/câu', 'AI Risk'
      ]);
      // Format header row
      const header = sheet.getRange(1, 1, 1, 14);
      header.setFontWeight('bold');
      header.setBackground('#1a1d27');
      header.setFontColor('#ffffff');
      sheet.setFrozenRows(1);
    }

    sheet.appendRow([
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

    // Color-code AI risk column (col 14)
    const lastRow = sheet.getLastRow();
    const riskCell = sheet.getRange(lastRow, 14);
    if (data.aiRisk === 'high') riskCell.setBackground('#3a1010').setFontColor('#f25f5c');
    else if (data.aiRisk === 'medium') riskCell.setBackground('#3a2e10').setFontColor('#f5a623');
    else riskCell.setBackground('#1a3a25').setFontColor('#34c97b');

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', row: lastRow }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Test function — chạy thủ công trong Apps Script editor để kiểm tra
function testDoPost() {
  const mockData = {
    date: new Date().toLocaleString('vi-VN'),
    student: 'Test Student',
    examId: 1,
    correct: 35, wrong: 5,
    duration: '55m30s',
    secA: 16, secB1: 12, secB2: 7,
    tabSwitches: 1, mouseLeaves: 3,
    fastAnswers: 0, avgSecs: 90.5,
    aiRisk: 'low'
  };
  const mock = { postData: { contents: JSON.stringify(mockData) } };
  const result = doPost(mock);
  Logger.log(result.getContent());
}
