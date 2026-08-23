---
name: minna-lesson
description: Thêm hoặc cập nhật trọn một bài Minna no Nihongo trong minna.html — từ vựng, mẫu câu, ngữ pháp, hội thoại, audio — rồi regen data, bump cache và verify bằng trình duyệt. Dùng khi người dùng nói "thêm bài X", "cập nhật bài X", "sửa từ vựng bài X", "sửa nghĩa bài X", "làm trọn bài X", "regen data minna", hoặc chuyển yêu cầu sửa lỗi từ giáo viên cho một bài cụ thể.
---

# Minna Lesson — thêm/cập nhật trọn 1 bài Minna

Skill **điều phối**. Nó không tự làm hội thoại và không tự làm audio:

- Hội thoại (会話) → dùng skill **`minna-dialogue`**
- Audio → dùng skill **`minna-audio`**

Việc của skill này là: sửa đúng file nguồn → chạy đúng generator → bump cache → verify → dừng cho người dùng duyệt.

## Context

- **Root**: `C:\Users\hoang\Desktop\BUILD WEB KOERU`
- **Branch**: `dev`
- **N5 = bài 1–25**, **N4 = bài 26–50**
- `minna.html` có 5 tab: `vocab` (Từ vựng), `dialogue` (Hội thoại), `grammar` (Mẫu câu), `write` (Luyện viết), `quiz` (Kiểm tra)

---

## Bước 1 — Xác định phạm vi

Chốt rõ trước khi đụng file nào:

- Bài số mấy? Cấp nào (suy từ số bài)?
- Đụng tab nào? Chỉ sửa cái được yêu cầu — **không mở rộng sang bài khác**.
- Nguồn thông tin là gì (ảnh sách, feedback giáo viên, file có sẵn)? Nếu là nội dung tiếng Nhật mới mà không có nguồn thật → **hỏi người dùng, không tự bịa**.

## Bước 2 — Sửa đúng file nguồn

**Luôn sửa file nguồn. Tuyệt đối không sửa `*-data.js`** — chúng là sản phẩm sinh ra và sẽ bị ghi đè ở bước 3.

| Nội dung | File nguồn |
|---|---|
| Từ vựng, mẫu câu của bài | `database/n4\|n5/lessonNN.json` (2 chữ số: `lesson01.json`) |
| Hội thoại | `database/dialogue/n4\|n5/lessonNN.json` — làm theo skill `minna-dialogue` |
| Tóm tắt ngữ pháp | `N4_grammar_summary.md` / `N5_grammar_summary.md` (heading `## Bài N`, bullet `- `) |

Schema `database/n4|n5/lessonNN.json`:

```json
{
  "lesson": 1,
  "source": "Bản dịch và giải thích ngữ pháp - Tập 1, tr.10-11",
  "status": "REVIEW_REQUIRED",
  "vocab": [{"w": "わたし", "k": "", "m": "tôi"}],
  "expressions": [{"w": "初[はじ]めまして。", "m": "Rất hân hạnh được gặp anh/chị."}]
}
```

- `w` = từ, `k` = kanji (rỗng nếu không có), `m` = nghĩa tiếng Việt
- Ruby furigana dùng cú pháp `漢字[かな]` — chỉ đặt `[かな]` ngay sau cụm kanji, không đặt sau kana thuần
- `status` giữ nguyên `"REVIEW_REQUIRED"` — quyền đổi thuộc về người dùng (giáo viên)
- Nghĩa tiếng Việt phải theo `.claude/rules/dictionary_standard.md`: không để tiếng Anh thô, phân tầng nghĩa bằng `;`

## Bước 3 — Chạy generator

Chỉ chạy cái liên quan tới thứ vừa sửa:

| Đã sửa | Chạy |
|---|---|
| `database/n5/*` hoặc `N5_grammar_summary.md` | `python tools/gen_minna_n5_data.py` |
| `database/n4/*` hoặc `N4_grammar_summary.md` | `python tools/gen_minna_n4_data.py` |
| `database/dialogue/*` | `python tools/gen_minna_dialogue_data.py` |

**Cảnh báo — `tools/gen_minna_grammar_data.py`**: script này parse 50 file .docx từ đường dẫn tuyệt đối **ngoài repo** (`...\jlpt-lesson-generator\output\docs\grammar`). Chỉ chạy khi thư mục đó thật sự tồn tại. Nếu không có, **bỏ qua và báo người dùng** — đừng để script fail rồi đoán mò nguyên nhân.

## Bước 4 — Audio

Nếu bài có từ vựng hoặc hội thoại mới → chuyển sang skill **`minna-audio`**.

Không bắt buộc: thiếu file audio thật thì `minna.html` tự fallback giọng đọc trình duyệt. Đừng sinh audio hàng loạt khi người dùng không yêu cầu.

## Bước 5 — Bump cache

```bash
python tools/bump_cache.py
```

Băm md5 nội dung, idempotent. **Không tự gõ `?v=YYYYMMDD` bằng tay.**

## Bước 6 — Verify bằng trình duyệt

"Script chạy không lỗi" **không** đủ. Phải nhìn thấy kết quả thật:

```bash
python -m http.server 7788
```

Mở `http://localhost:7788/minna.html?level=N5` (hoặc `N4`), vào đúng bài vừa sửa, kiểm **từng tab đã đụng**:

- Nội dung mới hiện đúng (nghĩa, từ, mẫu câu)
- Ruby furigana render đúng — kể cả ở tên nhân vật, không chỉ câu thoại
- Toggle "Ẩn/Hiện nghĩa" hoạt động
- Console sạch, nút 🔊 không báo lỗi

Cách nhanh: Playwright headless có sẵn trong repo — `test.use({ launchOptions: { executablePath: '/opt/pw-browsers/chromium' } })`, rồi `page.goto('/minna.html?level=N5')`, click `.lesson-card` chứa "Bài N", click `.tab[data-tab="vocab"]`, đọc `#tabContent` hoặc chụp screenshot.

## Bước 7 — Dừng

```bash
git status --short
git diff --stat
```

Tóm tắt cho người dùng: đã sửa bài nào, tab nào, bao nhiêu mục, generator nào đã chạy, kết quả verify.

**DỪNG Ở ĐÂY. Không commit.** Data ngôn ngữ cần mắt người duyệt — chờ người dùng đọc lại nội dung tiếng Nhật/tiếng Việt rồi mới chốt.

---

## Không làm

- Không sửa `minna-n4-data.js` / `minna-n5-data.js` / `minna-dialogue-data.js` bằng tay — sẽ bị generator ghi đè.
- Không đổi `status: "REVIEW_REQUIRED"`.
- Không tự bịa nội dung tiếng Nhật khi không có nguồn thật (ảnh sách, file gốc, hoặc chỉ dẫn rõ của người dùng).
- Không mở rộng phạm vi sang bài khác bài được yêu cầu.
- Không nhầm sang `koeru-sync` — skill đó phục vụ pipeline kanji ← Excel, hoàn toàn khác nhánh dữ liệu này.
- Không commit.
