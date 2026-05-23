// ══════════════════════════════════════════════════════
// KOERU KANJI — Google Apps Script Web App
// Paste toàn bộ file này vào Code.gs trong Apps Script
// Deploy as Web App: Execute as Me, Anyone can access
// ══════════════════════════════════════════════════════

const SHEET_NAME_DEFAULT = 'Kanji';

// ── GET handler ──────────────────────────────────────
function doGet(e) {
  // Guard: e có thể undefined khi chạy test trong editor
  const params = (e && e.parameter) ? e.parameter : {};
  const action = params.action || 'get';
  const sheet  = params.sheet  || SHEET_NAME_DEFAULT;

  try {
    if (action === 'ping') {
      return jsonResponse({ ok: true, message: 'Kết nối OK ✅', sheet });
    }
    if (action === 'get') {
      const data = readSheet(sheet);
      return jsonResponse(data);
    }
    return jsonResponse({ error: 'Unknown action: ' + action }, 400);
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

// ── POST handler ─────────────────────────────────────
function doPost(e) {
  try {
    const body   = JSON.parse(e.postData.contents);
    const action = body.action || 'set';
    const sheet  = body.sheet  || SHEET_NAME_DEFAULT;
    const data   = body.data;

    if (action === 'set') {
      if (!Array.isArray(data)) throw new Error('data phải là array');
      writeSheet(sheet, data);
      return jsonResponse({ ok: true, written: data.length });
    }
    return jsonResponse({ error: 'Unknown action: ' + action }, 400);
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

// ── Đọc sheet → array of objects ─────────────────────
function readSheet(sheetName) {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Sheet "' + sheetName + '" không tồn tại');

  const rows = sheet.getDataRange().getValues();
  if (rows.length < 2) return [];

  const headers = rows[0].map(h => String(h).trim());
  const result  = [];

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row[0] && !row[1]) continue; // bỏ hàng trống
    const obj = {};
    headers.forEach((h, j) => {
      if (h) obj[h] = row[j] !== undefined && row[j] !== null ? String(row[j]) : '';
    });
    result.push(obj);
  }
  return result;
}

// ── Ghi array of objects → sheet ─────────────────────
function writeSheet(sheetName, data) {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let sheet   = ss.getSheetByName(sheetName);

  // Tạo sheet mới nếu chưa có
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }

  if (!data.length) return;

  // Headers từ keys của object đầu tiên
  const headers = Object.keys(data[0]);

  // Build rows 2D array
  const rows = [headers];
  data.forEach(obj => {
    rows.push(headers.map(h => obj[h] !== undefined ? obj[h] : ''));
  });

  // Xoá data cũ, ghi mới
  sheet.clearContents();
  sheet.getRange(1, 1, rows.length, headers.length).setValues(rows);

  // Format header row
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange
    .setBackground('#1a1a2e')
    .setFontColor('#ffffff')
    .setFontWeight('bold');

  // Freeze header
  sheet.setFrozenRows(1);
}

// ── Helper: trả về JSON response ─────────────────────
function jsonResponse(data) {
  const output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
