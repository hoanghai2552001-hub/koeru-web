// KOERU CRM Setup Script
// Chạy hàm setupKOERU_CRM() một lần duy nhất để khởi tạo toàn bộ cấu trúc

function setupKOERU_CRM() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const SHEETS = ["Leads", "Students", "Payments", "Sessions", "Retention", "Content"];

  // Xoá tất cả sheet cũ, giữ lại 1 sheet tạm
  const allSheets = ss.getSheets();
  const tempSheet = ss.insertSheet("_temp");
  allSheets.forEach(s => ss.deleteSheet(s));

  // Tạo lại đúng thứ tự
  SHEETS.forEach((name, i) => {
    if (i === 0) {
      tempSheet.setName(name);
    } else {
      ss.insertSheet(name);
    }
  });

  _setupLeads(ss.getSheetByName("Leads"));
  _setupStudents(ss.getSheetByName("Students"));
  _setupPayments(ss.getSheetByName("Payments"));
  _setupSessions(ss.getSheetByName("Sessions"));
  _setupRetention(ss.getSheetByName("Retention"));
  _setupContent(ss.getSheetByName("Content"));

  SpreadsheetApp.getUi().alert("✅ KOERU CRM đã setup xong!");
}

// ─── LEADS ───────────────────────────────────────────────────────────────────
function _setupLeads(sheet) {
  const headers = ["ID","Họ tên","SĐT","Email","Source","Interest","Status","Note","Ngày tạo","Liên hệ lần cuối"];
  _writeHeaders(sheet, headers, "#1A2A80");

  // Dropdown: Source
  _addDropdown(sheet, 5, 2, 200,
    ["TikTok","Facebook","Instagram","Web","Referral","Zalo","Other"]);

  // Dropdown: Interest
  _addDropdown(sheet, 6, 2, 200,
    ["JP — Speaking Program","JP — N5 Prep","JP — N3 Prep","JP — N2 Prep","JP — Business",
     "CN — HSK 1","CN — HSK 2","CN — HSK 3","CN — Giao tiếp","Chưa rõ"]);

  // Dropdown: Status + màu
  _addDropdown(sheet, 7, 2, 200,
    ["New","Contacted","Trial","Converted","Lost"]);

  // Conditional formatting màu Status
  const statusRange = sheet.getRange("G2:G200");
  const rules = [
    { value: "New",       bg: "#E8E8E8", fg: "#555555" },
    { value: "Contacted", bg: "#D0E8FF", fg: "#0A3D8F" },
    { value: "Trial",     bg: "#FFF3CD", fg: "#7A5F00" },
    { value: "Converted", bg: "#D4EDDA", fg: "#155724" },
    { value: "Lost",      bg: "#FDDEDE", fg: "#8B0000" },
  ];
  const cfRules = rules.map(r => {
    return SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo(r.value)
      .setBackground(r.bg)
      .setFontColor(r.fg)
      .setRanges([statusRange])
      .build();
  });
  sheet.setConditionalFormatRules(cfRules);

  _formatSheet(sheet, headers.length);
}

// ─── STUDENTS ────────────────────────────────────────────────────────────────
function _setupStudents(sheet) {
  const headers = ["ID","Họ tên","SĐT","Email","Program","Ngày bắt đầu","Ngày kết thúc",
                   "Tổng buổi","Buổi đã học","Học phí (VNĐ)","Payment Status","Engagement","Note"];
  _writeHeaders(sheet, headers, "#1A2A80");

  _addDropdown(sheet, 5, 2, 200,
    ["JP Speaking Basic (8b)","JP Speaking Advanced (12b)","JP N5 Prep","JP N3 Prep","JP Business",
     "CN HSK 1","CN HSK 2","CN HSK 3","CN Giao tiếp"]);

  _addDropdown(sheet, 11, 2, 200, ["Paid","Partial","Overdue"]);
  _addDropdown(sheet, 12, 2, 200, ["High","Medium","Low","Inactive"]);

  // Màu Payment Status
  const payRange = sheet.getRange("K2:K200");
  const payRules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Paid").setBackground("#D4EDDA").setFontColor("#155724").setRanges([payRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Partial").setBackground("#FFF3CD").setFontColor("#7A5F00").setRanges([payRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Overdue").setBackground("#FDDEDE").setFontColor("#8B0000").setRanges([payRange]).build(),
  ];
  sheet.setConditionalFormatRules(payRules);

  _formatSheet(sheet, headers.length);
}

// ─── PAYMENTS ────────────────────────────────────────────────────────────────
function _setupPayments(sheet) {
  const headers = ["ID","Student ID","Tên học viên","Số tiền (VNĐ)","Ngày thanh toán","Phương thức","Program","Note"];
  _writeHeaders(sheet, headers, "#1A2A80");

  _addDropdown(sheet, 6, 2, 200, ["Chuyển khoản","Momo","Tiền mặt","ZaloPay"]);
  _formatSheet(sheet, headers.length);
}

// ─── SESSIONS ────────────────────────────────────────────────────────────────
function _setupSessions(sheet) {
  const headers = ["Ngày","Student ID","Tên học viên","Program","Buổi số","Attended","Homework","Speaking Score (1-5)","Note"];
  _writeHeaders(sheet, headers, "#1A2A80");

  _addDropdown(sheet, 6, 2, 200, ["Yes","No","Rescheduled"]);
  _addDropdown(sheet, 7, 2, 200, ["Done","Partial","Skipped"]);
  _formatSheet(sheet, headers.length);
}

// ─── RETENTION ───────────────────────────────────────────────────────────────
function _setupRetention(sheet) {
  const headers = ["Student ID","Tên học viên","Program","Buổi còn lại","Ngày học gần nhất","Ngày vắng (tính từ hôm nay)","Homework Rate (%)","Risk Flag","Action"];
  _writeHeaders(sheet, headers, "#8B0000");

  // Công thức Risk Flag (cột H = col 8) — tự động
  sheet.getRange("H2").setFormula(
    '=IF(OR(F2>7, G2<50), "⚠️ At Risk", "✅ OK")'
  );
  sheet.getRange("H2").copyTo(sheet.getRange("H3:H200"));

  _addDropdown(sheet, 9, 2, 200, ["None","Follow-up Scheduled","Called","Resolved"]);

  // Màu Risk Flag
  const riskRange = sheet.getRange("H2:H200");
  const riskRules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextContains("At Risk").setBackground("#FDDEDE").setFontColor("#8B0000").setRanges([riskRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextContains("OK").setBackground("#D4EDDA").setFontColor("#155724").setRanges([riskRange]).build(),
  ];
  sheet.setConditionalFormatRules(riskRules);

  _formatSheet(sheet, headers.length);
}

// ─── CONTENT ─────────────────────────────────────────────────────────────────
function _setupContent(sheet) {
  const headers = ["Ngày","Platform","Content Type","Topic","Emotional Angle","Status","Link","Engagement Note"];
  _writeHeaders(sheet, headers, "#0A3D8F");

  _addDropdown(sheet, 2, 2, 500, ["TikTok","Facebook Reels","Facebook Post","Instagram","Threads","YouTube Shorts"]);
  _addDropdown(sheet, 3, 2, 500, ["Reel","Caption","Story","Thread","Blog","Short"]);
  _addDropdown(sheet, 5, 2, 500,
    ["Speaking Fear","Quiet Ambition","Study Burnout","Identity Growth","Belonging","Discipline","Real-life Japanese","Chinese Learning"]);
  _addDropdown(sheet, 6, 2, 500, ["Idea","In Progress","Scheduled","Posted"]);

  // Màu Status
  const statusRange = sheet.getRange("F2:F500");
  const rules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Idea").setBackground("#F0F0F0").setRanges([statusRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("In Progress").setBackground("#FFF3CD").setFontColor("#7A5F00").setRanges([statusRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Scheduled").setBackground("#D0E8FF").setFontColor("#0A3D8F").setRanges([statusRange]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("Posted").setBackground("#D4EDDA").setFontColor("#155724").setRanges([statusRange]).build(),
  ];
  sheet.setConditionalFormatRules(rules);

  _formatSheet(sheet, headers.length);
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function _writeHeaders(sheet, headers, bgColor) {
  const range = sheet.getRange(1, 1, 1, headers.length);
  range.setValues([headers]);
  range.setBackground(bgColor)
       .setFontColor("#FFFFFF")
       .setFontWeight("bold")
       .setFontSize(11);
  sheet.setFrozenRows(1);
}

function _addDropdown(sheet, col, startRow, endRow, options) {
  const range = sheet.getRange(startRow, col, endRow - startRow + 1, 1);
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(options, true)
    .setAllowInvalid(false)
    .build();
  range.setDataValidation(rule);
}

function _formatSheet(sheet, numCols) {
  sheet.setColumnWidth(1, 60);   // ID
  sheet.setColumnWidth(2, 160);  // Name
  for (let i = 3; i <= numCols; i++) {
    sheet.setColumnWidth(i, 140);
  }
  sheet.getRange(2, 1, 200, numCols)
       .setVerticalAlignment("middle")
       .setFontSize(10);
}
