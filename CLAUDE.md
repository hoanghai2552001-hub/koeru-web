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
js/kanji-data-n5.js     window.KANJI_N5 — 103 kanji N5
js/kanji-data-n4.js     window.KANJI_N4 — 160 kanji N4
js/kanji-data-n3.js     window.KANJI_N3 — 377 kanji N3
js/kanji-data-n2.js     window.KANJI_N2 — 313 kanji N2
js/kanji-data-n1.js     window.KANJI_N1 — 628 kanji N1
kanji-map-data.js       window.KANJI_DATA {kanji,vocab} — dùng bởi kanji-map.html
kanji-map-vocab-ext.js  vocab mở rộng cho kanji-map

css/kanji.css           Styles cho kanji.html
kanji-map.css           Styles cho kanji-map.html

tools/sync_kanji_excel.py   Script đồng bộ Excel → JS (chạy: python tools/sync_kanji_excel.py)
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
# Sau đó bump cache version trong HTML nếu deploy:
# kanji-data.js?v=YYYYMMDD
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

## Cache busting

Khi sửa JS/CSS, bump version trong HTML:
- `?v=YYYYMMDD` (ngày hôm nay)
- Files hay sửa: `kanji-data.js`, `kanji.css`, `kanji-map-data.js`

## Lệnh hay dùng

```bash
python tools/sync_kanji_excel.py      # Sync data từ Excel
python -m http.server 7788            # Local preview
git push origin dev                   # Deploy
```
