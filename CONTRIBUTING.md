# Contributing to KOERU

## Branch Workflow

```
main        ← production, chỉ merge từ dev khi đã test
dev         ← branch làm việc chính
feature/*   ← tính năng mới (tách từ dev)
fix/*       ← hotfix nhỏ (tách từ dev)
```

### Quy tắc cơ bản
- **Không commit thẳng lên `main`** — luôn qua `dev` trước
- Merge `dev` → `main` chỉ khi: tests pass + QA report sạch
- Đặt tên branch mô tả r��: `feature/kana-quiz`, `fix/flashcard-timer`

---

## Commit Message Format

Theo [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <mô tả ngắn>

[body tuỳ chọn]
```

| Type | Khi nào dùng |
|------|-------------|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa bug |
| `refactor` | Cấu trúc lại code, không thay đổi behavior |
| `data` | Cập nhật dữ liệu kanji/kana |
| `test` | Thêm/sửa tests |
| `chore` | Công việc bảo trì (build, deps, config) |
| `docs` | Chỉ cập nhật tài liệu |

**Ví dụ tốt:**
```
feat(dungeon): thêm boss fight mỗi 5 tầng
fix(flashcard): timer không reset khi đổi mode
data(n3): sửa 23 reading sai trong N3
```

**Tránh:**
```
fix bug
update code
WIP
```

---

## Data Pipeline

Khi cần cập nhật `js/kanji-data.js`:

```bash
# Chạy toàn bộ pipeline
bash tools/build.sh all

# Hoặc từng bước
bash tools/build.sh fetch     # Fetch từ KanjiAPI
bash tools/build.sh fix       # Chạy tất cả scripts fix
bash tools/build.sh validate  # QA + syntax check
```

**Chỉ commit `js/kanji-data.js` sau khi `qa_report.json` báo `with_errors: 0`.**

---

## Chạy Tests

```bash
# Cài dependencies (lần đầu)
npm install

# Khởi động dev server
python3 -m http.server 8000

# Chạy E2E tests (tab khác)
npm run test:e2e

# Có UI (để debug)
npm run test:e2e:headed
```

---

## Cấu trúc thư mục

```
/
├── index.html          ← Landing page
├── kanji.html          ← Kanji app
├── kana.html           ← Kana app
├── js/                 ← Game logic (module per game)
├── css/                ← Stylesheets
├── tools/              ← Python build scripts (không deploy)
│   ├── build.sh        ← Build pipeline chính
│   ├── build_kanji_data.py
│   ├── qa_kanji.py
│   └── ...
├── tests/              ← Playwright E2E tests
├── Code.gs             ← Google Apps Script — Kanji data API
├── koeru_crm_setup.gs  ← GAS — CRM sheet setup
├── koeru_triggers.gs   ← GAS — Email automation
├── Makefile            ← Shortcuts (Linux/Mac)
└── .env.example        ← Template cho environment variables
```
