# Trạng thái project (cập nhật 2026-07-23)

Ghi chú này để bất kỳ ai (người hoặc Claude) mở lại session sau đọc là hiểu ngay tình hình.

## Việc đang dở dang

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

## Quyết định / feedback quan trọng từ user trong session này
- Không có thay đổi code nào được yêu cầu hay thực hiện trong session này — chỉ hỏi "đang làm gì" và "task nào chưa xong". Chưa có quyết định về việc merge PR nào trước.

## Trạng thái git
- Branch hiện tại: `claude/hien-dang-lam-gi-fbxluo`, đang trùng hoàn toàn với `main`, working tree sạch, không có commit/thay đổi nào chưa push.
- Không có file nào bị sửa dở trong session này.

## Việc cần làm tiếp theo (gợi ý)
1. Review nội dung PR #1 và PR #2, đối chiếu xem còn xung đột/trùng lặp gì không (đặc biệt phần kanji-map-data.js).
2. Quyết định merge PR #2 vào `main` trước (đã verify kỹ, không còn mục treo).
3. Với PR #1 (base `dev`): kiểm tra lại xem các fix có còn áp dụng đúng sau khi PR #2 merge chưa, hoàn thành mục test Kanji Map còn thiếu, rồi merge vào `dev`.
4. Sau khi merge, nhớ bump cache version (`?v=YYYYMMDD`) theo quy ước trong CLAUDE.md nếu có sửa JS/CSS thêm.
