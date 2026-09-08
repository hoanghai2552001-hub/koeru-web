# KOERU — Project Context

## Tổng quan
Web app học tiếng Nhật & tiếng Trung — static HTML/JS/CSS, không có backend.
- **URL**: https://hoanghai2552001-hub.github.io/koeru-web/
- **Branch chính**: `dev` → push lên `origin/dev`
- **Local preview**: `python -m http.server 7788` → http://localhost:7788

## Cấu trúc file quan trọng

```
index.html              SPA chính — tất cả trang (home, flash, quiz, blog...)
kanji.html              Kanji Lab — 4 game (Flashcard, Match, Bubble, Quiz)
study.html              Tra cứu từ vựng + bảng kanji
kanji-map.html          Bản đồ Kanji (React + D3, force graph)
kana.html               Kana Speed game

js/kanji-data.js        window.KANJI_DATA — 1581 kanji flat array (N5-N1)
js/kanji-data-n5.js     window.KANJI_N5 — 80 kanji N5
js/kanji-data-n4.js     window.KANJI_N4 — 163 kanji N4
js/kanji-data-n3.js     window.KANJI_N3 — 367 kanji N3
js/kanji-data-n2.js     window.KANJI_N2 — 343 kanji N2
js/kanji-data-n1.js     window.KANJI_N1 — 628 kanji N1
kanji-map-data.js       window.KANJI_DATA {kanji,vocab} — dùng bởi kanji-map.html
kanji-map-vocab-ext.js  vocab mở rộng cho kanji-map

css/kanji.css           Styles cho kanji.html
kanji-map.css           Styles cho kanji-map.html

tools/sync_kanji_excel.py   Script đồng bộ Excel → JS (chạy: python tools/sync_kanji_excel.py)
tools/build.py              Master build (sync + bump cache + gen HTML + QA)
tools/pre_commit_check.py   Git hook: block commit nếu Excel mới hơn JS
tools/install_hooks.py      Cài git hook sau khi clone lần đầu
tools/export_excel.py       Export JS → Excel (để sửa rồi sync lại)
tools/qa_kanji.py           QA toàn bộ data → qa_report.html
tools/gen_kanji_map_data.py Tái tạo kanji-map-data.js từ kanji-data.js
tools/align_dialogue_audio.py   Cắt audio hội thoại từ CD gốc (STT + align) → audio/_aligned/
tools/verify_dialogue_cuts.py   Soát chất lượng audio hội thoại đã cắt (cảnh báo dòng lệch)
tools/archive/              Scripts legacy — đã dùng xong, giữ để tham khảo
input/excel/kanji_KOERU_full.xlsx   Nguồn dữ liệu chính (KHÔNG commit, KHÔNG sửa bằng script)
```

## Kiến trúc SPA (index.html)

- Navigation: `showPage(p)` — ẩn/hiện `.page` divs
- 3 tool pages nhúng iframe: `study`, `kanji`, `kana` → `EMBEDDED_TOOLS`
- Các tool khác (kanji-map...) mở qua slide-in panel: `openTool(url)`
- `body.tool-active` → ẩn footer khi tool active
- Tool history lưu `localStorage('koeru_tool_history')` max 5

## Data sync workflow

```bash
# Sau khi sửa Excel → chạy:
python tools/sync_kanji_excel.py

# Kết quả: cập nhật 7 file JS, giữ nguyên freq_rank/grade/mnemonic

# Sau đó bump cache version nếu deploy:
python tools/bump_cache.py
```

## Kanji Map (kanji-map.html)

- React 18 + D3 + Babel standalone (inline JSX)
- State chính: `selectedId`, `jlptFilter` (localStorage `km_jlpt_filter`, default `['N5']`)
- Full-map view: grid layout (không dùng force simulation)
- Subgraph view: D3 force simulation khi chọn 1 kanji
- ALL_LEVELS = `['N5', 'N4', 'N3', 'N2']` ← N1 trong data nhưng chưa có filter chip

## Game cards layout (kanji.html)

- `.game-cards`: CSS grid 2×2, card 5 (Quiz) full width `grid-column: 1/-1`
- Inline CSS `!important` trong kanji.html để bypass cache

## Git workflow

```bash
git add <files>
git commit -m "type(scope): message

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin dev
```

## Credentials — KHÔNG BAO GIỜ commit

- `oauth_credentials.json`
- `tools/oauth_credentials.json`
- Đã có trong `.gitignore`

**API key luôn truyền qua biến môi trường, không hardcode trong script:**

| Biến | Dùng cho |
|---|---|
| `GOOGLE_TTS_API_KEY` | `gen_vocab_audio.py`, `gen_business_vocab_audio.py`, `gen_dialogue_audio.py --engine google` |
| `GOOGLE_STT_API_KEY` | `align_dialogue_audio.py` (Speech-to-Text) |
| `MINNA_CD_DIR` | Thư mục mp3 CD Minna cho `align_dialogue_audio.py` (không phải secret, chỉ là đường dẫn ngoài repo) |

PowerShell: `$env:GOOGLE_TTS_API_KEY='xxx'` trước khi chạy script.

## Cache busting

Khi sửa JS/CSS, **chạy `python tools/bump_cache.py`** — không gõ tay.

- Version là **md5 nội dung file** (`?v=04d29f29`), không phải ngày. Nghĩa là `?v=` chỉ đổi khi file thực sự đổi → không tạo diff rác, chạy lại bao nhiêu lần cũng ra một kết quả (idempotent).
- Quét toàn bộ `*.html` ở root, cập nhật mọi `src=`/`href=` có `?v=`.
- `python tools/bump_cache.py --check` → exit 1 nếu có file lệch version (dùng để chặn deploy).

## Lệnh hay dùng

```bash
# Workflow hàng ngày
python tools/sync_kanji_excel.py      # Sau khi sửa Excel → sync tất cả JS + auto QA
python tools/build.py                 # Full build: sync + bump cache + gen study HTML + QA
python tools/build.py --quick         # Nhanh: chỉ sync + bump cache (bỏ qua gen HTML)
python tools/build.py --check         # Chỉ chạy QA, không sync

# Xem QA report dạng HTML
python tools/qa_kanji.py              # → mở qa_report.html trong browser

# Audio Minna (xem skill minna-audio) — [n4|n5] [lessonN], bỏ trống = tất cả bài
python tools/gen_vocab_audio.py n5 lesson3      # TTS từ vựng   (cần GOOGLE_TTS_API_KEY)
python tools/gen_dialogue_audio.py n5 lesson3   # TTS hội thoại (mặc định soundoftext, không cần key)
python tools/align_dialogue_audio.py n5 lesson3 # Cắt từ CD gốc (cần GOOGLE_STT_API_KEY + MINNA_CD_DIR)
python tools/verify_dialogue_cuts.py n5 lesson3 # Soát audio đã cắt (thêm --staging để soát audio/_aligned/)

# Tiếng Trung — HSK 标准教程 1·2·3 (hsk.html) — bỏ trống cấp = làm cả 3
python tools/extract_hsk_source.py --dry-run       # Bóc từ vựng/hội thoại/mẫu câu từ Tiếng Trung/HSK<N>.zip
python tools/extract_hsk_source.py hsk2            # → database/hsk2/*.json (status REVIEW_REQUIRED)
python tools/gen_hsk_data.py                       # database/hsk<N>/ → hsk<N>-data.js
python tools/gen_hsk_audio.py hsk2 --dry-run       # Xem sẽ gọi API bao nhiêu lần TRƯỚC khi tốn quota
python tools/gen_hsk_audio.py hsk2 --dialogue      # TTS cmn-CN → audio/hsk/ (cần GOOGLE_TTS_API_KEY)
python tools/extract_hsk_audio.py --dry-run        # Audio gốc giáo trình → audio/_hsk_aligned/ (staging)

# Data Minna (xem skill minna-lesson) — sửa database/ rồi chạy generator tương ứng
python tools/gen_minna_n5_data.py     # database/n5/ + N5_grammar_summary.md → minna-n5-data.js
python tools/gen_minna_n4_data.py     # database/n4/ + N4_grammar_summary.md → minna-n4-data.js
python tools/gen_minna_dialogue_data.py  # database/dialogue/ → minna-dialogue-data.js
python tools/bump_cache.py            # Bump ?v= theo md5 nội dung (idempotent)

# Setup (chạy 1 lần sau clone)
python tools/install_hooks.py         # Cài pre-commit hook

# Local preview & deploy
python -m http.server 7788            # http://localhost:7788
git push origin dev                   # Deploy lên GitHub Pages

# Automation (Karpathy Loop Architecture)
python tools/watch_excel.py           # Watchdog: auto-sync khi Excel thay đổi (chạy ngầm)
```

## Vocabulary QA — Rules

Khi làm việc với từ vựng Nhật-Việt (dịch nghĩa, review data, thêm từ mới, báo cáo lỗi),
bắt buộc đọc và áp dụng:

- @.claude/rules/dictionary_standard.md — Tiêu chuẩn dịch thuật & chuẩn hóa
- @.claude/rules/qa_validation.md       — Checklist phát hiện lỗi & format báo cáo
- @.claude/brand-voice-guidelines.md    — Brand voice & phong cách triển khai tổng quan

**Trigger**: Bất kỳ yêu cầu nào liên quan đến:
- Dịch nghĩa từ Nhật → Việt
- Kiểm tra chất lượng `words[].m`, `words[].r`
- Review sau `sync_kanji_excel.py`
- Báo cáo lỗi từ vựng
- Thêm/sửa data trong Excel sheet Words
