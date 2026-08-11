---
name: minna-dialogue
description: Thêm hội thoại (会話) cho 1 bài Minna no Nihongo (N4 hoặc N5) vào tab "Hội thoại" trong minna.html, từ ảnh chụp/scan sách gốc do người dùng cung cấp. Dùng khi người dùng gửi ảnh 会話 của 1 bài Minna và muốn đưa vào app, hoặc yêu cầu "thêm hội thoại bài X", "làm tiếp bài X-Y kiểu minna-dialogue".
---

# Minna Dialogue — thêm hội thoại cho 1 bài Minna no Nihongo

## Input cần có

- Số bài (1 bài = 1 số thứ tự trong sách, N5 = bài 1–25, N4 = bài 26–50).
- Ảnh chụp/scan trang 会話 gốc của bài đó (người dùng gửi trực tiếp trong chat). **Không tự bịa hoặc nhớ lại nội dung hội thoại từ trí nhớ** — sách Minna no Nihongo có bản quyền, web search sẽ KHÔNG tìm ra bản 会話 đầy đủ (đã kiểm chứng: các trang giáo án tiếng Nhật công khai chỉ nói về ngữ pháp/từ vựng trọng tâm, không đăng nguyên văn hội thoại). Nếu chưa có ảnh, hỏi người dùng gửi trước khi làm tiếp.

## Quy trình

1. **Transcribe** đúng nguyên văn hội thoại từ ảnh: tên nhân vật, từng lượt thoại, chú thích CD/số trang nếu có trong ảnh.
2. **Đối chiếu** với dữ liệu đã có của đúng bài đó trước khi viết bản dịch:
   - Ngữ pháp: `N4_grammar_summary.md` hoặc `N5_grammar_summary.md` (tìm heading `## Bài N`).
   - Từ vựng: `database/n4/lessonNN.json` hoặc `database/n5/lessonNN.json` (field `vocab`, `expressions`).
   - Xác nhận hội thoại có dùng đúng mẫu ngữ pháp trọng tâm của bài (vd bài 27 phải thấy 可能形 hoặc 見える/聞こえる) — nếu không khớp, transcribe lại cẩn thận, có thể đã nhầm bài.
3. **Viết bản dịch VN** tự nhiên cho từng câu, giọng văn nói, sát nghĩa — theo đúng văn phong đang dùng trong `expressions[].m` của bài đó (tham khảo file JSON cùng bài).
4. **Tạo file** `database/dialogue/n4/lessonNN.json` (hoặc `n5/`) theo đúng schema:
   ```json
   {
     "lesson": 27,
     "source": "Minna no Nihongo II SBT — 会話 CD04, tr.11",
     "status": "REVIEW_REQUIRED",
     "title": "何[なん]でも 作[つく]れるんですね",
     "characters": ["ミラー", "鈴木[すずき]"],
     "lines": [
       {"spk": "ミラー", "jp": "明[あか]るくて、いい 部屋[へや]ですね。", "vn": "Phòng sáng sủa, đẹp quá nhỉ."}
     ]
   }
   ```
   - `jp`/`spk`/`title` dùng cú pháp ruby `漢字[かな]` (chỉ đặt `[かな]` ngay sau cụm kanji cần đọc, không đặt sau kana thuần).
   - `source` ghi rõ tên sách + CD/trang lấy từ ảnh gốc.
   - `status` luôn để `"REVIEW_REQUIRED"` — người dùng (giáo viên) sẽ tự duyệt sau, không tự đổi.
5. **Chạy generator**: `python3 tools/gen_minna_dialogue_data.py` → sinh lại `minna-dialogue-data.js`.
6. **Bump cache version** trong `minna.html`: sửa `?v=YYYYMMDD` ở dòng `<script src="minna-dialogue-data.js?v=...">` nếu file này đã từng được deploy.
7. **Kiểm chứng bằng trình duyệt** trước khi commit — không chỉ dựa vào "chạy script không lỗi":
   - `python -m http.server 7788` (hoặc dùng server đang chạy sẵn), mở `minna.html?level=N4` (hoặc `N5`).
   - Vào đúng bài vừa thêm → tab "Hội thoại": kiểm tra ruby furigana hiện đúng (kể cả ở tên nhân vật, không chỉ câu thoại), toggle "Ẩn/Hiện nghĩa" hoạt động, nút 🔊 không báo lỗi console (sẽ tự fallback sang giọng đọc trình duyệt vì audio thật thường chưa có).
   - Cách nhanh: dùng Playwright headless có sẵn trong repo — `test.use({ launchOptions: { executablePath: '/opt/pw-browsers/chromium' } })` rồi `page.goto('/minna.html?level=N4')`, click `.lesson-card` chứa "Bài N", click `.tab[data-tab="dialogue"]`, chụp screenshot hoặc đọc `#tabContent`.
8. Đối chiếu **thủ công lần cuối** từng câu JP trong file JSON với ảnh gốc trước khi commit (transcribe sai 1 chữ kanji/kana là sai hẳn nghĩa).

## Audio (không bắt buộc ở bước này)

Khung audio đã có sẵn trong `minna.html` (hàm `playAudio`/`speakJP`), không cần code thêm. Khi người dùng có file mp3 thật cho hội thoại, đặt đúng tên: `audio/dialogue/<n4|n5>/lesson<N>_<01,02,...>.mp3` (1 file / lượt thoại, đánh số theo thứ tự trong `lines[]`, 2 chữ số). Không có file thì tự động fallback giọng đọc trình duyệt, không cần làm gì thêm.

## Không làm

- Không tự bịa hội thoại khi không có ảnh nguồn thật (khác với việc *biên soạn hội thoại mới bám sát ngữ pháp/từ vựng* — nếu người dùng muốn hướng đó thay vì hội thoại gốc từ sách, phải hỏi rõ trước, đây không phải mặc định).
- Không đổi `status` thành khác `REVIEW_REQUIRED` — đó là quyền của người dùng.
- Không sửa `database/n4|n5/lessonNN.json` (vocab/grammar) trong lúc làm việc này — phạm vi chỉ là hội thoại.
