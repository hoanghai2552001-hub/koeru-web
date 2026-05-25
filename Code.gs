// ══════════════════════════════════════════════════════
// KOERU KANJI — Google Apps Script Web App
// Paste toàn bộ file này vào Code.gs trong Apps Script
// Deploy as Web App: Execute as Me, Anyone can access
// ══════════════════════════════════════════════════════

// ── Cấu hình qua Script Properties (không hardcode) ──
// Cách setup: Apps Script → Project Settings → Script Properties
//   Key: KANJI_SHEET_ID   Value: <ID của Google Sheet>
// Xem .env.example để biết danh sách tất cả keys cần thiết.
function getConfig() {
  const props = PropertiesService.getScriptProperties();
  return {
    spreadsheetId : props.getProperty('KANJI_SHEET_ID') || '',
    sheetDefault  : props.getProperty('KANJI_SHEET_NAME') || 'Kanji',
  };
}
const SHEET_NAME_DEFAULT = 'Kanji'; // fallback nếu getConfig() chưa set

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
    // append: thêm hàng mới, không xoá data cũ (dùng khi import từ sách)
    if (action === 'append') {
      if (!Array.isArray(data)) throw new Error('data phải là array');
      var appended = appendToSheet(sheet, data);
      return jsonResponse({ ok: true, appended: appended });
    }
    return jsonResponse({ error: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse({ error: err.message });
  }
}

// ── Mở spreadsheet theo ID (works for both bound & standalone) ─
function getSpreadsheet() {
  const id = getConfig().spreadsheetId;
  try {
    if (id) return SpreadsheetApp.openById(id);
  } catch (e) {}
  // Fallback: bound script (khi chạy từ sheet trực tiếp)
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

// ── Thêm hàng mới vào sheet (không xoá dữ liệu cũ) ───
function appendToSheet(sheetName, data) {
  var ss    = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    // Sheet chưa có → tạo mới với writeSheet
    writeSheet(sheetName, data);
    return data.length;
  }
  if (!data || !data.length) return 0;

  // Lấy headers hiện tại từ hàng 1
  var existingHeaders = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0]
    .map(function(h) { return String(h).trim(); })
    .filter(function(h) { return h; });

  if (!existingHeaders.length) {
    // Sheet trống → ghi mới
    writeSheet(sheetName, data);
    return data.length;
  }

  // Kiểm tra trùng (theo cột 'kanji' nếu có)
  var kanjiCol = existingHeaders.indexOf('kanji');
  var existingKanji = new Set();
  if (kanjiCol >= 0 && sheet.getLastRow() > 1) {
    var existing = sheet.getRange(2, kanjiCol + 1, sheet.getLastRow() - 1, 1).getValues();
    existing.forEach(function(r) { if (r[0]) existingKanji.add(String(r[0])); });
  }

  // Lọc chỉ lấy từ chưa có
  var newRows = data.filter(function(obj) {
    if (kanjiCol >= 0 && obj.kanji) return !existingKanji.has(String(obj.kanji));
    return true;
  }).map(function(obj) {
    return existingHeaders.map(function(h) {
      return (obj[h] !== undefined && obj[h] !== null) ? obj[h] : '';
    });
  });

  if (!newRows.length) return 0;

  // Append vào cuối
  sheet.getRange(sheet.getLastRow() + 1, 1, newRows.length, existingHeaders.length)
    .setValues(newRows);

  return newRows.length;
}

// ── JSON response helper ──────────────────────────────
function jsonResponse(data) {
  var output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
