// ══════════════════════════════════════════════════════
// KOERU KANJI — Google Apps Script Web App
// Paste toàn bộ file này vào Code.gs trong Apps Script
// Deploy as Web App: Execute as Me, Anyone can access
// ══════════════════════════════════════════════════════

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
      const data = readSheet(sheet);
      return jsonResponse(data);
    }
    return jsonResponse({ error: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse({ error: err.message });
  }
}

// ── POST handler ─────────────────────────────────────
// Note: use Content-Type: text/plain from client to avoid CORS preflight
function doPost(e) {
  try {
    const raw  = e.postData ? e.postData.contents : '{}';
    const body = JSON.parse(raw);
    const action = body.action || 'set';
    const sheet  = body.sheet  || SHEET_NAME_DEFAULT;
    const data   = body.data;

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

// ── Đọc sheet → array of objects ─────────────────────
function readSheet(sheetName) {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Sheet "' + sheetName + '" không tồn tại');

  const rows = sheet.getDataRange().getValues();
  if (rows.length < 2) return [];

  const headers = rows[0].map(function(h) { return String(h).trim(); });
  var result = [];

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
  const ss  = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) sheet = ss.insertSheet(sheetName);
  if (!data.length) return;

  var headers = Object.keys(data[0]);
  var rows = [headers];
  data.forEach(function(obj) {
    rows.push(headers.map(function(h) {
      return obj[h] !== undefined ? obj[h] : '';
    }));
  });

  sheet.clearContents();
  sheet.getRange(1, 1, rows.length, headers.length).setValues(rows);

  // Format header
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
