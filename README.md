# KOERU — Luyen Tap Tieng Nhat

Web app luyen tap tieng Nhat bang tieng Viet. Bao gom kanji N5–N1 va bai tap kana voi he thong spaced repetition.

**Live site**: _them link khi deploy_

---

## Tinh nang

### Kanji (N5 → N1) — `kanji.html`

| Mini-game | Mo ta |
|-----------|-------|
| **Flashcard** | On tap the xem — guong mat cua SRS. Deck duoc sap xep theo do uu tien: qua han ôn > chua gap > thap nhat |
| **Match** | Ghep doi kanji voi nghia. On xong tu dong phat am (TTS) |
| **Speed** | Toc chien — chon dap an truoc khi thanh time het. Co TTS |
| **Dungeon RPG** | Kanji hien ra nhu quai vat; chon dung thi giam mau quai |

Tat ca 4 game ghi progress chung vao `koeru_mastery_v2` (localStorage) theo thuat toan **SM-2 Spaced Repetition**.

### Kana — `kana.html`

- Trang Home chon: Hiragana / Katakana / Mixed x Trinh do 1-3
- Trinh do 3 luyen tu vung 1-3 ki tu tu Minna no Nihongo
- **Tap viet**: bang chu voi animation thu tu net but
- **Bang xep hang**: luu diem len Supabase (co the tat qua `kana-config.js`)

---

## Chay local

```bash
# Khong can cai dat gi them — chi can Python hoac Node
python -m http.server 8000
# Mo trinh duyet: http://localhost:8000/kanji.html
```

---

## Build data

```bash
# Can Python 3.9+
pip install -r tools/requirements.txt   # neu co

make all          # chay toan bo pipeline
# hoac tung buoc:
python tools/build_kanji_data.py
python tools/build_compounds.py
python tools/qa_kanji.py              # kiem tra chat luong, exit 1 neu co loi
```

Du lieu chinh: `js/kanji-data.js` (~1481 kanji), `js/kana-data.js`.

---

## Kiem tra & test

```bash
# JS syntax (khong can install)
node --check js/kanji-data.js

# E2E (Playwright)
npm ci
npx playwright test

# QA data
python tools/qa_kanji.py
```

---

## CI/CD

GitHub Actions chay tu dong khi push len `dev` hoac mo PR vao `main`:

| Job | Viec lam | Thoi gian |
|-----|----------|-----------|
| **QA Data** | `qa_kanji.py` — kiem tra khong con nghia tieng Anh | ~20 giay |
| **JS Syntax** | `node --check` toan bo `js/*.js` | ~10 giay |
| **E2E Tests** | Playwright Chromium — test ca man hinh game | ~3 phut |

Branch `main` duoc bao ve: merge chi duoc chap thuan khi ca 3 job tren deu pass.

Xem cau hinh: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

---

## Cau truc thu muc

```
koeru/
├── kanji.html          # Trang kanji chinh
├── kana.html           # Trang kana
├── css/                # Stylesheet
├── js/
│   ├── kanji-data.js   # Du lieu 1481 kanji (N5-N1)
│   ├── kana-data.js    # Du lieu hiragana/katakana
│   ├── koeru-mastery.js# SRS unified store (SM-2)
│   ├── kana-config.js  # Supabase config (leaderboard)
│   └── ...             # Game logic files
├── tools/
│   ├── qa_kanji.py     # QA script (dung trong CI)
│   ├── build_*.py      # Build pipeline
│   └── archive/        # Scripts mot lan da hoan thanh
├── tests/              # Playwright E2E tests
└── .github/workflows/  # CI/CD
```

---

## Tech stack

- **Frontend**: Vanilla JS + CSS (khong framework)
- **Du lieu**: JS files tinh (khong can server)
- **Leaderboard**: Supabase (PostgreSQL)
- **TTS**: Web Speech API (`speechSynthesis`, `lang: 'ja-JP'`)
- **SRS**: SM-2 algorithm, luu `localStorage`
- **CI**: GitHub Actions (free tier)

---

## Dong gop

Xem [`CONTRIBUTING.md`](CONTRIBUTING.md) de biet ve quy trinh branch, commit convention va cach chay test truoc khi PR.
