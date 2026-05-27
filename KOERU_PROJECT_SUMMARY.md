# KOERU — Project Summary
> Cập nhật: 2026-05-27 | Branch: dev → main (GitHub Pages)
> Live: https://hoanghai2552001-hub.github.io/koeru-web/

---

## 1. Mục tiêu sản phẩm

Nền tảng học tiếng Nhật cho người Việt, gồm:
- Học Kanji N5–N1 kèm Hán Việt, bộ thủ, gợi nhớ tiếng Việt, stroke order
- Luyện qua các mini-game (Flashcard, Nối từ, Dungeon, Speed Kanji)
- Học Kana (Hiragana/Katakana)
- Bản đồ Kanji tương tác (D3 force graph)
- Theo dõi tiến độ cá nhân (mastery system)

**Stack:** HTML/CSS/JS thuần — không dùng React, Vite, Next.js, bundler, import/export ES module.

**Phase 1 scope:** N5–N2 chuẩn hóa đầy đủ. N1 giữ nguyên.

---

## 2. File chính

| File | Vai trò |
|------|---------|
| `index.html` | Trang chủ — navbar, onboarding |
| `kanji.html` | Kanji Lab — 4 mini-games |
| `study.html` | Học Kanji — browse + detail panel |
| `kana.html` | Kana Speed game |
| `kanji-map.html` | Bản đồ Kanji (React + D3 + Babel) |
| `js/kanji-data.js` | ALL_KANJI 1481 kanji — dùng bởi kanji.html |
| `js/kanji-data-n5~n1.js` | Data theo level — lazy load bởi study.html |
| `js/kanji-study.js` | Logic trang Học Kanji |
| `js/kanji-stroke.js` | Stroke order overlay (dùng trong kanji.html) |
| `js/koeru-mastery.js` | Tracking tiến độ (localStorage) |
| `js/kanji-state.js` | State chung cho các game |
| `js/kanji-flashcard.js` | Game Flashcard |
| `js/kanji-match.js` | Game Nối từ |
| `js/kanji-bubble.js` | Game Kanji Dungeon |
| `js/kanji-speed.js` | Game Speed Kanji |
| `js/kanji-panel.js` | Floating panel (mục tiêu, nhật ký, từ vựng) |
| `css/kanji.css` | Style cho kanji.html |
| `css/study.css` | Style cho study.html |
| `kanji-map-app.jsx` | React app Kanji Map |

---

## 3. Tính năng hiện có

### Trang Học Kanji (`study.html`)
- Grid kanji theo level N5/N4/N3/N2/N1/Tất cả
- Tìm kiếm theo kanji, nghĩa, Hán Việt, On/Kun
- Detail panel: stroke order (KanjiVG), bộ thủ tiếng Việt, thành phần, gợi nhớ VI, từ vựng
- Lazy load data theo level (N5=55KB lúc đầu, preload N4 sau 2s)
- Progressive render: 150 cells đầu, load thêm khi scroll
- Keyboard navigation: ←→ đổi kanji, Esc đóng panel

### Kanji Lab (`kanji.html`)
- 4 game: Flashcard, Nối từ, Kanji Dungeon, Speed Kanji
- Stroke order overlay (nút ▶ Nét vẽ trong Flashcard)
- Mastery tracking (SRS-lite)
- Floating panel: mục tiêu, lịch sử, nhật ký, từ vựng

### Kanji Map (`kanji-map.html`)
- Force-directed graph N5–N2
- Click node xem detail + stroke order
- Tìm kiếm, lọc theo JLPT level

### Kana Speed (`kana.html`)
- Nhận diện Hiragana/Katakana

---

## 4. ID/Function/Script Order — KHÔNG ĐƯỢC ĐỔI

### Script order trong `kanji.html` (bắt buộc giữ nguyên)
```
1. js/kanji-data.js
2. js/koeru-mastery.js
3. js/kanji-state.js
4. js/kanji-flashcard.js
5. js/kanji-match.js
6. js/kanji-bubble.js
7. js/kanji-speed.js
8. js/kanji-panel.js
```

### ID HTML không được đổi tên
```
home-screen       flash-screen      match-screen      bubble-screen
go-flash          go-match          go-bubble         go-speed
s-sph             s-speed           s-spr
kanji-lead-modal  kanji-lead-form
fp-toggle         fp-panel
gs-modal
detail-panel      detail-backdrop   detail-content    detail-placeholder
detail-kanji-big  detail-hanviet    detail-meaning
detail-on         detail-kun        detail-badges
detail-radical    detail-parts      detail-mnemonic
detail-stroke-svg detail-stroke-count
btn-replay-stroke detail-vocab-list
detail-go-game    detail-go-map
kanji-grid        study-search      study-search-clear
study-stats-count study-goto-game
```

### Function global không được xóa/đổi tên
```
handleKanjiLead   fpSaveGoal        fpAddMilestone    fpClearHistory
fpAddDiary        fpExportCSV       fpShowImport      fpShowGSheet
gsTest            gsPull            gsPush            gsClose
showStrokeOrder   replayStrokeOrder closeStrokeOverlay
openDetail        closeDetail       renderGrid        replayStroke
ensureLevelLoaded
```

---

## 5. Thay đổi đã làm (session này)

| Commit | Nội dung |
|--------|---------|
| `4959325` | Tạo trang Học Kanji (study.html) |
| `01ce7b0` | Fix layout responsive — grid multi-column, side panel |
| `6ac76f9` | Đổi CDN animCJK (403) → KanjiVG (CC BY-SA 3.0) |
| `c5d515d` | Fix kanji-map: đổi unpkg→jsDelivr, bỏ SRI hash |
| `7aa5ab4` | Logo KOERU trong Kanji Map |
| `79c365f` | Bổ sung radical/parts/mnemonic/grade từ the-kanji-map |
| `4f5fea1` | Bổ sung data N1 (99.8% coverage) |
| `d8d687a` + `51aa2eb` | Merge dịch VI: radical_vi + mn_vi cho 1003 kanji |
| `78a19b5` | Lazy load data by level + progressive grid render |
| `b9cc3bf` | Cleanup: comment, dead code, CSS trùng |

### Data kanji hiện tại
- **1481 kanji** (N5–N1), tất cả có: Hán Việt, nghĩa VI, On/Kun, stroke count, radical
- **N5–N2** (853 kanji): đầy đủ bộ thủ VI, thành phần, gợi nhớ VI, frequency rank, grade
- **N1** (628 kanji): có radical/parts/mnemonic EN, 153 kanji có mnemonic VI
- **Source:** KanjiAPI + Jisho/KanjiAlive via the-kanji-map (CC BY-SA 3.0) + dịch ChatGPT

---

## 6. Việc còn lại

### Ưu tiên cao
- [ ] Sửa label tab study.html sai số lượng (N4 ghi 181 thực tế 116, N3 ghi 361 thực tế 89)
- [ ] Kiểm tra koeru-mastery.js tích hợp đầy đủ chưa

### Ưu tiên trung bình
- [ ] N1 mnemonic VI còn 475 kanji chỉ có tiếng Anh
- [ ] Dữ liệu N4/N3 số lượng chênh lệch so với chuẩn JLPT — cần kiểm tra lại nguồn

### Tùy chọn / Phase 2
- [ ] Pipeline Google Sheet → review → publish cho data chuẩn hóa
- [ ] KANJIDIC2 XML trực tiếp thay vì KanjiAPI wrapper
- [ ] Thêm audio phát âm (từ KanjiAlive nếu được phép)

---

## 7. Guardrails khi sửa code

```
TRƯỚC KHI SỬA:
1. Đọc file liên quan
2. Liệt kê phạm vi: file, ID, function, script order bị ảnh hưởng
3. Commit Git checkpoint: git add . && git commit -m "checkpoint: before ..."

KHI SỬA:
✗ Không refactor toàn bộ
✗ Không đổi id/class HTML đang được JS dùng
✗ Không đổi tên function global đang được HTML gọi qua onclick
✗ Không đổi thứ tự <script>
✗ Không dùng import/export (không có bundler)
✗ Không xóa CSS selector khi chưa chắc còn dùng
✓ Chỉ sửa đúng phần được yêu cầu
✓ Chia nhỏ thành nhiều patch, mỗi patch test xong mới làm tiếp

SAU KHI SỬA:
- Báo cáo: file đã sửa, ID/function đã động tới
- Cung cấp checklist test thủ công

ROLLBACK nếu crash:
git restore .
```

---

## 8. Checklist test

### study.html
- [ ] Grid load — hiển thị nhiều cột (không phải 1 cột)
- [ ] Level tabs N5/N4/N3/N2/N1/Tất cả chuyển đúng
- [ ] Search hoạt động
- [ ] Click kanji → detail panel mở
- [ ] Stroke order animate (KanjiVG)
- [ ] Bộ thủ tiếng Việt hiển thị
- [ ] Thành phần (parts) hiển thị
- [ ] Gợi nhớ tiếng Việt hiển thị
- [ ] Nút ↺ Phát lại stroke hoạt động
- [ ] Keyboard ←→ điều hướng kanji
- [ ] Nút "Luyện trong Kanji Lab" → kanji.html
- [ ] Console không có lỗi đỏ

### kanji.html
- [ ] Home — 4 game card hiển thị
- [ ] Flashcard — lật thẻ, đúng/sai, ▶ Nét vẽ
- [ ] Nối từ — chọn cặp đúng/sai
- [ ] Kanji Dungeon — options hiển thị, chọn đáp án
- [ ] Speed Kanji — timer chạy, tính điểm
- [ ] Console không có lỗi đỏ

### kanji-map.html
- [ ] Graph load — nodes hiển thị
- [ ] Click node → detail
- [ ] Search hoạt động
- [ ] Logo KOERU hiển thị (không phải text "越 KOERU")

### index.html
- [ ] Navbar link đến kanji.html, study.html, kanji-map.html
- [ ] Mobile menu hoạt động
