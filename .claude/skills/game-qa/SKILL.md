---
name: game-qa
description: >
  QA agent chuyên kiểm tra bug trong web game HTML/JS/CSS. Tự động phân tích
  static code để tìm hàm undefined, ID bị thiếu, event listener trỏ vào element
  không tồn tại, guard flag không reset, timer leak, và logic lỗi game.

  Dùng skill này khi người dùng:
  - Báo có bug trong game (crash, đơ, không phản hồi, hiệu ứng không chạy)
  - Muốn kiểm tra toàn bộ code game trước khi deploy
  - Nói "kiểm tra bug", "check lỗi game", "game bị đơ", "màn X bị lỗi"
  - Muốn QA định kỳ sau khi thêm tính năng mới
  - Hỏi "game có bug gì không?"

  Luôn dùng skill này thay vì đọc file thủ công khi người dùng hỏi về bug game.
---

# Game QA Skill

Bạn là QA engineer phân tích web game HTML/JS/CSS. Nhiệm vụ: tìm bug thực sự ảnh hưởng gameplay, không phải cảnh báo code style.

## Bước 1 — Chạy script phân tích tĩnh

Trước tiên, xác định HTML file cần QA. Các game hiện có:

| File | Game |
|------|------|
| `kanji.html` | Kanji Dungeon (Nhật) |
| `kana.html` | Kana Practice (Nhật) |
| `study.html` | Kanji Study (Nhật) |
| `pinyin.html` | Pinyin Speed (Trung) |
| `hsk-flash.html` | HSK Flashcard (Trung) |
| `hanzi-lab.html` | Hanzi Lab (Trung) |
| `hanzi-map.html` | Hanzi Map (Trung) |

**Nếu user không chỉ rõ game nào** → QA tất cả (chạy vòng lặp).
**Nếu user chỉ rõ** (vd: "check hanzi-lab") → chỉ chạy file đó.

Chạy script cho **từng** HTML file cần QA:

```bash
# Ví dụ cho hanzi-lab.html:
python .claude/skills/game-qa/scripts/static_analyzer.py \
  --html hanzi-lab.html \
  --js-dir js/ \
  --out qa_static_report.json

# Ví dụ quét tất cả game cùng lúc (gộp report):
for html in kanji.html kana.html study.html pinyin.html hsk-flash.html hanzi-lab.html hanzi-map.html; do
  python .claude/skills/game-qa/scripts/static_analyzer.py \
    --html $html --js-dir js/ --out qa_${html%.html}.json
done
```

Script tự động tìm:
- Hàm được gọi (`funcName(`) nhưng không định nghĩa trong bất kỳ JS nào
- `getElementById('id')` trỏ tới ID không có trong HTML tĩnh (loại trừ ID được tạo động qua innerHTML)
- Event listener gắn vào element theo ID — nếu ID không tồn tại → crash ngay khi load
- Biến toàn cục dùng trước khi khai báo trong file

Đọc từng `qa_*.json` để lấy danh sách lỗi. Sau khi xong, xoá các file tạm:
```bash
del qa_kanji.json qa_kana.json qa_study.json qa_pinyin.json qa_hsk-flash.json qa_hanzi-lab.json qa_hanzi-map.json 2>nul
```

## Bước 2 — Phân tích logic game (Claude đọc code)

Sau khi có kết quả static, đọc từng JS game file và kiểm tra:

### 2a. Guard flags
Tìm các boolean guard (`dAnswering`, `isAnimating`, `mMatchAnimating`, v.v.). Với mỗi flag:
- Có được reset về `false` trong mọi nhánh kết thúc không? (timeout, correct, wrong, game over)
- Có bị kẹt `true` nếu function throw error ở giữa không?

### 2b. Timer/interval leak
Với mỗi `setInterval` / `setTimeout`:
- Handle có được lưu vào biến không?
- Có hàm `clearInterval`/`clearTimeout` tương ứng được gọi khi exit game không?
- Nếu game bị navigate away, timer có còn chạy không?

### 2c. Null-access patterns
Tìm `document.getElementById(x).something` không có null-check — nếu element không tồn tại sẽ crash.
Phân biệt: ID được tạo động (qua innerHTML) vs ID phải có sẵn trong HTML.

### 2d. Boss / đặc biệt flow
Kiểm tra logic rẽ nhánh đặc biệt:
- Boss floor logic (HP 2 lần, re-render không reset HP)
- Game over vs floor complete
- State reset khi bắt đầu tầng mới

### 2e. Shared state giữa các game
Khi navigate từ game A sang B rồi quay lại A: state có bị dirty không?
Timer của game A có bị clear khi rời không?

## Bước 3 — Phân tích data

Chạy tùy theo ngôn ngữ:

```bash
# Kanji data (Nhật):
python .claude/skills/game-qa/scripts/data_checker.py \
  --data js/kanji-data.js \
  --out qa_data_report.json

# HSK/Hanzi data (Trung) — dùng --lang zh:
python .claude/skills/game-qa/scripts/data_checker.py \
  --data js/hsk-data.js \
  --lang zh \
  --out qa_hsk_data_report.json

python .claude/skills/game-qa/scripts/data_checker.py \
  --data js/hanzi-radical-data.js \
  --lang zh \
  --out qa_hanzi_data_report.json
```

**Kiểm tra data Nhật (`--lang ja`, default):**
- `words[].m` có nghĩa tiếng Anh không (Latin không dấu)
- Kanji thiếu trường bắt buộc: `on`/`kun`/`meaning`/`level`
- `on` không phải katakana, `kun` không phải hiragana
- `words[].r` không phải kana

**Kiểm tra data Trung (`--lang zh`):**
- Hanzi thiếu trường bắt buộc: `pinyin`/`meaning`/`hsk`
- `pinyin` không có dấu thanh (ā á ǎ à)
- `meaning` để trống hoặc chỉ có placeholder
- `hsk` nằm ngoài 1–9

## Bước 4 — Tổng hợp và báo cáo

Phân loại bug theo severity:

| Severity | Ký hiệu | Mô tả |
|----------|---------|-------|
| Critical | 🔴 | Crash/freeze ngay khi trigger (undefined function, null-access không guard) |
| High     | 🟠 | Game bị kẹt, không chơi được tiếp (guard flag stuck, timer không clear) |
| Medium   | 🟡 | Sai hiển thị, sai logic nhưng không crash |
| Low      | 🔵 | Data quality (English meanings), UX nhỏ |

## Format báo cáo

```
## 🎮 Game QA Report — [tên game] — [ngày]

### 🔴 Critical (N lỗi)
**[Tên lỗi]**
- File: `js/kanji-bubble.js` dòng 429
- Vấn đề: `playTone` được gọi nhưng không được định nghĩa ở bất kỳ đâu
- Hậu quả: `dAnswering` bị kẹt `true`, người chơi không thể tiếp tục
- Fix: Thêm `playTone()` vào `kanji-state.js`

### 🟠 High (N lỗi)
...

### 📊 Tóm tắt
- Tổng bug: X (Critical: Y, High: Z, Medium: W, Low: V)
- File sạch: [danh sách file không có lỗi]
```

## Nguyên tắc quan trọng

**Ưu tiên hậu quả gameplay:** Chỉ báo những gì ảnh hưởng thực sự đến người chơi. Không báo code style, không báo `var` vs `let`, không báo missing JSDoc.

**Phân biệt dynamic vs static IDs:** Một ID như `dng-opts-grid` được tạo qua `innerHTML` bên trong function là chủ ý thiết kế — không phải bug. Bug thực sự là ID được gọi `.addEventListener()` ngay khi page load mà không tồn tại.

**Verify trước khi báo:** Nếu thấy hàm X "không định nghĩa", check tất cả file JS (kể cả kanji-state.js, kanji-panel.js) trước khi kết luận là bug.

**Đề xuất fix cụ thể:** Mỗi bug phải có fix suggestion rõ ràng (file + cách sửa), không chỉ mô tả vấn đề.
