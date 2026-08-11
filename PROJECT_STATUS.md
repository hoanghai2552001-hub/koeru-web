# Trạng thái project (cập nhật 2026-08-11)

Ghi chú này để bất kỳ ai (người hoặc Claude) mở lại session sau đọc là hiểu ngay tình hình.

## Việc đang dở dang — mới nhất (2026-08-11)

### Đã làm: tính năng phát âm + ghi chú/ví dụ cá nhân cho `minna.html`
User feedback (nguyên văn ý chính): trong `minna.html` (Minna no Nihongo N5·N4) có nhiều bài **thiếu chữ kanji**, **từ vựng chưa khớp sách Minna gốc**, cần **thêm phát âm** cho từng từ, và cần tính năng **thêm ví dụ + ghi chú riêng, lưu lại để ôn tập sau**.

Đã hỏi lại và chốt hướng đi:
1. **Việc sửa data (thiếu kanji / từ chưa khớp sách)**: user cho biết nguồn sách gốc nằm ở máy cá nhân của họ — `C:\Users\hoang\Desktop\BUILD WEB KOERU\input\pdf\N5\Bản dịch và giải thích ngữ pháp - Tập 1.pdf` và `...\N4\Mina N4 SGK mới.pdf`. **Hai file này KHÔNG có trong repo và không truy cập được từ session remote** → chưa thể đối chiếu/sửa data. **Cần user upload 2 file PDF này** (hoặc ảnh chụp từng bài) vào lần làm việc tiếp theo để đối chiếu thứ tự bài, từ vựng, kanji cho đúng.
2. **Ưu tiên đã chọn**: làm tính năng ví dụ + ghi chú cá nhân trước (việc code, không phụ thuộc sách) → **đã hoàn thành và push** (commit `e7f86ba` trên branch `claude/hien-dang-lam-gi-fbxluo`).

**Đã triển khai trong `minna.html`:**
- Phát âm: nút 🔊 cạnh mỗi từ trong bảng từ vựng và trong Flashcard (1 thẻ), dùng Web Speech API (`speak()`, giọng `ja-JP`).
- Ghi chú/ví dụ cá nhân: nút ✎ mở modal nhập "Ví dụ của tôi" + "Ghi chú", lưu vào `localStorage` key `koeru_minna_notes` (keyed theo `level-lessonNum-word`, không phụ thuộc thứ tự mảng vocab). Nút ✎ đổi màu vàng (`has-note`) nếu từ đã có ghi chú.
- Trang tổng hợp "📒 Ghi chú & ví dụ của tôi" (nút ở trang chủ `minna.html`) — liệt kê tất cả từ đã ghi chú across mọi bài/cấp độ, có nút nghe lại và xoá từng mục.
- Đã test bằng Playwright (chromium, executablePath `/opt/pw-browsers/chromium`): mở bài → 31 nút ✎ hiện đúng → lưu ghi chú → đánh dấu has-note → mở trang review → hiện đúng 1 mục vừa lưu. Không phát hiện lỗi JS console trong luồng test.

**Còn treo, cần làm tiếp:**
- **#1 Thiếu kanji trong nhiều từ** (field `k` rỗng trong `minna-n5-data.js`/`minna-n4-data.js` khi lẽ ra phải có) — **chưa sửa**, cần 2 file PDF nguồn ở trên để đối chiếu chính xác từng bài.
- **#2 Từ vựng chưa khớp sách Minna gốc** (thứ tự bài, nội dung từ) — **chưa sửa**, cùng lý do cần nguồn PDF.
- Nhiều bài trong `minna-n5-data.js` có `status: "REVIEW_REQUIRED"` (dữ liệu OCR từ sách, chưa được giáo viên duyệt lần cuối) — hiển thị cảnh báo ⚠ ngay trong UI tab Từ vựng. Đây chính là các bài cần đối chiếu ưu tiên khi có PDF nguồn.
- Chưa thêm nút phát âm/ghi chú vào Flashcard dạng lưới (`renderFlashGrid`) — hiện chỉ có ở bảng và Flashcard 1 thẻ. Có thể bổ sung sau nếu cần.

**Việc cần làm ngay khi user quay lại**: xin/nhận 2 file PDF nguồn Minna no Nihongo (N5 tập 1 "Bản dịch và giải thích ngữ pháp", N4 "SGK mới") qua upload, rồi đối chiếu từng bài trong `minna-n5-data.js`/`minna-n4-data.js` để bổ sung kanji thiếu + sửa từ vựng sai khớp, ưu tiên các bài đang gắn cờ `REVIEW_REQUIRED`.

## Việc đang dở dang — từ trước (2026-07-23)

Có **2 pull request draft đang mở, chưa merge**, chưa có việc nào được làm thêm trong session này (session này chỉ thuần rà soát, không sửa code):

### PR #1 — https://github.com/hoanghai2552001-hub/koeru-web/pull/1
`fix(qa): QA toàn diện — 16 bugs + tách quiz module + accessibility`
- Base: `dev` ← head: `claude/tom-tat-oqz6jq`
- Tạo 2026-06-27, cập nhật lần cuối 2026-07-02
- Sửa 25+ bug: flashcard chấm sai điểm (fake meaning trùng nghĩa), speed game distractor trùng, CSV export escape sai (RFC-4180), kanji-map streak "hôm nay" luôn = 0, leaderboard crash khi Supabase CDN fail, `km_jlpt_filter` kẹt N1 vĩnh viễn, v.v.
- **Còn treo**: 1 mục test plan chưa tick — "Kanji Map: cần test trên môi trường có CDN (sandbox chặn) — verify React production load + badge 'hôm nay'".
- Lưu ý từ tác giả PR: `kanji-map-data.js` từng bị gỡ khỏi git tracking (commit c660d44) → nếu không có trên GitHub Pages thì trang kanji-map thiếu data trên production. Vấn đề này **đã được PR #2 xử lý** (xem dưới).

### PR #2 — https://github.com/hoanghai2552001-hub/koeru-web/pull/2
`fix(qa): sửa Kanji Map hỏng trên production, lỗi JS index.html, viết lại e2e suite (21/21 pass)`
- Base: `main` ← head: `claude/qa-testing-deployment-h9g9ne`
- Tạo 2026-07-09 (mới hơn PR #1)
- Sửa lỗi production nghiêm trọng: `kanji-map-data.js` bị lọt vào `.gitignore` nên chưa từng được deploy → trang Kanji Map trắng trên GitHub Pages. Đã gỡ khỏi gitignore, tái tạo file, sửa `tools/gen_kanji_map_data.py` + `tools/gen_vocab_ext.py` (bỏ hardcode path Windows).
- Sửa 4 `ReferenceError` trong `index.html` (iframe onload fire trước khi `frameReady()` được định nghĩa).
- Viết lại toàn bộ e2e suite: 19/19 fail → 21/21 pass (game Bubble đổi thành Kanji Dungeon, match game đổi markup, flashcard easy-mode stub `Math.random`).
- Đã kiểm chứng đầy đủ, **không còn mục nào treo** theo mô tả PR.

**Việc cần quyết định khi quay lại**: cả 2 PR đều là draft, chưa ai review/approve/merge. Cần quyết định thứ tự merge (PR #2 base `main`, PR #1 base `dev` — khác base branch nên có thể xung đột/trùng lặp phần xử lý kanji-map-data). Nên rà lại xem PR #1 có bị PR #2 làm lỗi thời một phần không trước khi merge cả hai.

## Quyết định / feedback quan trọng từ user (toàn bộ session, gộp các lần)
- 2026-08-11: rà soát tính năng có thể cải thiện toàn site → đã liệt kê 10 gợi ý (xem lịch sử chat / có thể yêu cầu Claude rà lại nếu cần), chưa triển khai cái nào trong số đó ngoại trừ việc user tự chọn đi vào `minna.html` cụ thể.
- 2026-08-11: với `minna.html`, user xác nhận ưu tiên **ghi chú/ví dụ cá nhân trước**, việc sửa data (kanji thiếu, từ chưa khớp sách) để sau khi có PDF nguồn.
- Chưa có quyết định về thứ tự merge PR #1/#2 (mục cũ bên dưới).

## Trạng thái git
- Branch hiện tại: `claude/hien-dang-lam-gi-fbxluo`.
- Đã push 2 commit trong session 2026-08-11: `2928916` (docs: PROJECT_STATUS.md ban đầu) và `e7f86ba` (feat: phát âm + ghi chú minna.html). Working tree sạch tại thời điểm ghi chú này.
- Branch này **chưa có PR mở** — cân nhắc mở PR nếu muốn merge các thay đổi trên vào `dev`/`main`.
- PR #1 và #2 (mục dưới) vẫn đang là draft riêng biệt, không liên quan tới branch này.

## Việc cần làm tiếp theo (gợi ý)
1. **Ưu tiên**: nhận PDF nguồn Minna no Nihongo từ user → sửa kanji thiếu + từ vựng sai khớp trong `minna-n5-data.js`/`minna-n4-data.js`, gỡ cờ `REVIEW_REQUIRED` sau khi duyệt xong từng bài.
2. Cân nhắc mở PR cho branch `claude/hien-dang-lam-gi-fbxluo` (chứa tính năng ghi chú/phát âm) để merge vào `dev`.
3. Review nội dung PR #1 và PR #2 (repo gốc, không liên quan minna), đối chiếu xem còn xung đột/trùng lặp gì không (đặc biệt phần kanji-map-data.js).
4. Quyết định merge PR #2 vào `main` trước (đã verify kỹ, không còn mục treo).
5. Với PR #1 (base `dev`): kiểm tra lại xem các fix có còn áp dụng đúng sau khi PR #2 merge chưa, hoàn thành mục test Kanji Map còn thiếu, rồi merge vào `dev`.
6. Sau khi merge, nhớ bump cache version (`?v=YYYYMMDD`) theo quy ước trong CLAUDE.md nếu có sửa JS/CSS thêm.
