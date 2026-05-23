// ══════════════════════════════════════════════════════
// KOERU KANJI — Google Apps Script Web App
// Paste toàn bộ file này vào Code.gs trong Apps Script
// Deploy as Web App: Execute as Me, Anyone can access
// ══════════════════════════════════════════════════════

// ⚠️ Thay SPREADSHEET_ID bằng ID từ URL Google Sheet của bạn
// URL dạng: https://docs.google.com/spreadsheets/d/<ID>/edit
const SPREADSHEET_ID   = '18L12LLSISwxwaolxC6AlJT04ei7Fib9ea90UC96qdT0';
const SHEET_NAME_DEFAULT = 'Kanji';

// ── GET handler ──────────────────────────────────────
function doGet(e) {
  const params = (e && e.parameter) ? e.parameter : {};
  const action = params.action || 'get';
  const sheet  = params.sheet  || SHEET_NAME_DEFAULT;

  try {
    if (action === 'ping') {
      return jsonResponse({ ok: true, message: 'Kết nối OK ✅', sheet: sheet });
    }
    if (action === 'get') {
      var data = readSheet(sheet);
      return jsonResponse(data);
    }
    return jsonResponse({ error: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse({ error: err.message });
  }
}

// ── POST handler ─────────────────────────────────────
function doPost(e) {
  try {
    var raw  = (e && e.postData) ? e.postData.contents : '{}';
    var body = JSON.parse(raw);
    var action = body.action || 'set';
    var sheet  = body.sheet  || SHEET_NAME_DEFAULT;
    var data   = body.data;

    if (action === 'set') {
      if (!Array.isArray(data)) throw new Error('data phải là array');
      writeSheet(sheet, data);
      return jsonResponse({ ok: true, written: data.length });
    }
    return jsonResponse({ error: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse({ error: err.message });
  }
}

// ── Mở spreadsheet theo ID (works for both bound & standalone) ─
function getSpreadsheet() {
  // Thử dùng ID cụ thể trước
  try {
    if (SPREADSHEET_ID && SPREADSHEET_ID !== 'YOUR_SPREADSHEET_ID') {
      return SpreadsheetApp.openById(SPREADSHEET_ID);
    }
  } catch (e) {}
  // Fallback: bound script
  return SpreadsheetApp.getActiveSpreadsheet();
}

// ── Đọc sheet → array of objects ─────────────────────
function readSheet(sheetName) {
  var ss    = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Sheet "' + sheetName + '" không tồn tại');

  var rows = sheet.getDataRange().getValues();
  if (rows.length < 2) return [];

  var headers = rows[0].map(function(h) { return String(h).trim(); });
  var result  = [];

  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    if (!row[0] && !row[1]) continue;
    var obj = {};
    headers.forEach(function(h, j) {
      if (h) obj[h] = (row[j] !== undefined && row[j] !== null) ? String(row[j]) : '';
    });
    result.push(obj);
  }
  return result;
}

// ── Ghi array of objects → sheet ─────────────────────
function writeSheet(sheetName, data) {
  var ss    = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) sheet = ss.insertSheet(sheetName);
  if (!data || !data.length) return;

  var headers = Object.keys(data[0]);
  var rows = [headers];
  data.forEach(function(obj) {
    rows.push(headers.map(function(h) {
      return (obj[h] !== undefined && obj[h] !== null) ? obj[h] : '';
    }));
  });

  sheet.clearContents();
  sheet.getRange(1, 1, rows.length, headers.length).setValues(rows);

  // Format header row
  sheet.getRange(1, 1, 1, headers.length)
    .setBackground('#1a1a2e')
    .setFontColor('#ffffff')
    .setFontWeight('bold');
  sheet.setFrozenRows(1);
}

// ── JSON response helper ──────────────────────────────
function jsonResponse(data) {
  var output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
