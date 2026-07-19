# PROMPT CHO CLAUDE DESIGN — Nâng cấp UX/UI hệ thống KOERU

> Copy toàn bộ nội dung dưới đây vào Claude Design. Nếu có thể, đính kèm các file HTML được liệt kê ở mục 2.

---

Bạn là design lead cho **KOERU** — web app học tiếng Nhật & tiếng Trung cho người Việt, static HTML/JS/CSS thuần, deploy trên GitHub Pages, không backend, không build step.

## 1. Nhiệm vụ

Thiết kế lại UX/UI cho các interface hiện có theo hướng **tinh chỉnh (refine), không đập đi xây lại**. Output phải áp được vào code hiện tại mà **không phá vỡ bất kỳ logic, workflow hay tính năng nào** (ràng buộc kỹ thuật ở mục 4 là bắt buộc).

## 2. Các interface trong hệ thống

| File | Vai trò | Điểm cần chú ý |
|---|---|---|
| `index.html` | SPA chính: home, flash, quiz, blog; điều hướng bằng `showPage(p)` ẩn/hiện `.page` | 3 tool nhúng iframe (study/kanji/kana), tool khác mở slide-in panel `openTool(url)`; `body.tool-active` ẩn footer |
| `kanji.html` | Kanji Lab — 4 game: Flashcard, Match, Bubble, Quiz | `.game-cards` grid 2×2, card 5 (Quiz) full width; có inline CSS `!important` |
| `study.html` | Tra cứu từ vựng + bảng kanji | Data lớn (1581 kanji N5–N1) |
| `kanji-map.html` | Bản đồ Kanji: React 18 + D3 + Babel inline | Full-map = grid; subgraph = force simulation; filter chip JLPT lưu `localStorage('km_jlpt_filter')` |
| `kana.html` | Kana Speed game | |
| `test-dau-vao.html` | Landing + thi đầu vào N3: chọn 1/5 mã đề, timer 70', 40 câu MCQ, lưới điều hướng 40 ô, nộp bài → điểm + breakdown 4 kỹ năng + xem lại câu sai kèm giải thích | 3 màn: `#landing`, `#test`, `#result` |
| `minna-n5.html` | 25 bài Minna N5: bảng từ vựng (kana–kanji–nghĩa), mẫu câu self-check, luyện viết kanji trên canvas (tô theo chữ mờ), quiz 10 câu lưu điểm cao nhất, tra nhanh 830 từ | Tiến độ lưu localStorage: `mn5_quiz_<n>`, `mn5_gr_<n>`; furigana render bằng `<ruby>` |

## 3. Design language hiện tại (giữ và hệ thống hóa)

- **Dark theme**: nền `#0a0d14`, card `#121820`, card phụ `#1a2230`
- **Chữ**: `#f4f0ea` (chính), `#8a8070` (muted), font `Noto Sans JP / Noto Sans`
- **Accent**: cam `#e8845a`, vàng `#f5c842`; đúng `#5ac88a`, sai `#e85a6a`
- Nền có radial-gradient cam/vàng mờ ở góc; card bo 14–16px, border `rgba(244,240,234,.09)`
- Badge pill, tab pill, button gradient cam

## 4. RÀNG BUỘC BẮT BUỘC (không được vi phạm)

1. **Không đổi tech stack**: HTML/CSS/JS thuần, một file HTML tự chứa CSS. KHÔNG thêm framework, KHÔNG CDN, KHÔNG font ngoài (trừ font hệ thống/Noto đã dùng), KHÔNG build step. Riêng kanji-map.html được giữ React+D3 như hiện có.
2. **Không đổi tên** bất kỳ: `id`, `class` mà JS đang bám (`#landing`, `#test`, `#result`, `#tabContent`, `.lesson-card`, `.opt`, `.tab`, `.gr-item`, `#kGrid`, `#cv`, `#drawBox`, `.set-btn`, `#gridNav`, `.game-cards`…), key `localStorage`, tên hàm (`showPage`, `openTool`). Chỉ được THÊM class/attribute mới.
3. **Không đổi luồng chức năng**: số bước làm bài, cách chấm điểm, cách lưu tiến độ, iframe/panel navigation của SPA, cache-busting `?v=YYYYMMDD` giữ nguyên.
4. **Responsive bắt buộc**: dùng tốt trên cả iPhone (375px, touch, tap target ≥ 44px) lẫn desktop. Không tràn ngang. Canvas luyện viết và lưới 40 ô điều hướng phải hoạt động tốt trên mobile.
5. **Tiếng Nhật hiển thị chuẩn**: kanji cần furigana (`<ruby>`) ở nội dung dành cho N5; không dùng font làm méo kana; cỡ chữ tiếng Nhật ≥ cỡ chữ tiếng Việt tương ứng.
6. **Ngôn ngữ UI**: tiếng Việt, giọng thân thiện — học thuật (brand KOERU: "chuyên sâu nhưng dễ hiểu").
7. **Accessibility**: contrast đạt WCAG AA trên nền dark, trạng thái focus rõ, không truyền thông tin chỉ bằng màu (đúng/sai phải kèm icon/text).
8. Dữ liệu học liệu (từ vựng, đề thi) là **cố định** — không đề xuất tính năng đòi thêm/sửa nội dung học liệu hay cần backend.

## 5. Vấn đề UX cần giải quyết (ưu tiên theo thứ tự)

1. **Tính nhất quán**: các trang tự viết CSS riêng, lệch nhau về spacing/kích thước nút/tab → cần **design token + component spec chung** (màu, spacing scale, radius, typography scale, button, tab, card, badge, bảng từ vựng, quiz option, progress bar, timer).
2. **Trang thi (`test-dau-vao.html`)**: giảm căng thẳng thị giác khi làm bài dài 40 câu; timer dễ thấy nhưng không gây áp lực; màn kết quả cần kể chuyện tốt hơn (điểm → kỹ năng yếu → nên ôn gì).
3. **Trang bài học (`minna-n5.html`)**: bảng 40–50 từ/bài đang là wall-of-text → cần nhịp thị giác (nhóm từ, sticky header cột, hoặc chế độ flashcard-list); tab Luyện viết cần cảm giác "bút mực" hơn; tiến độ tổng quan 25 bài cần trực quan (đã học bao nhiêu %, bài nào nên ôn lại).
4. **Trang chủ SPA (`index.html`)**: điều hướng tới đúng tool nhanh hơn cho học sinh mới (hiện hơi nhiều lối vào).
5. **Game (`kanji.html`, `kana.html`)**: juice/feedback khi đúng-sai, nhưng nhẹ nhàng, không âm thanh bắt buộc.

## 6. Deliverables yêu cầu

1. **Design tokens** dạng CSS custom properties (1 block `:root{}` dùng chung được cho mọi trang).
2. **Component library**: mỗi component 1 file HTML preview tự chứa (button các cỡ/trạng thái, tab, card bài học, quiz option 4 trạng thái mặc định/hover/đúng/sai, bảng từ vựng có ruby, timer, progress, badge, search box, canvas frame luyện viết).
3. **Mockup 3 màn hình then chốt** (mobile 375px + desktop 1280px): (a) trang chủ minna-n5 với tiến độ 25 bài, (b) màn làm bài thi + lưới điều hướng, (c) màn kết quả thi.
4. **Ghi chú bàn giao cho dev**: với mỗi thay đổi, ghi rõ "chỉ đổi CSS" hay "cần thêm markup", và markup thêm vào là gì — để dev áp vào code cũ mà không đụng JS.

## 7. Tiêu chí nghiệm thu

- Áp token mới vào một trang bất kỳ chỉ bằng cách thay block CSS, JS không cần sửa dòng nào.
- Học sinh N5 dùng điện thoại một tay làm được trọn quiz 10 câu và bài thi 40 câu.
- Mọi text đạt contrast AA; tap target ≥ 44px; không horizontal scroll ở 375px.
- Nhìn 2 trang bất kỳ cạnh nhau nhận ra ngay là cùng một sản phẩm KOERU.
