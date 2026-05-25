#!/usr/bin/env bash
# =============================================================
# KOERU — Kanji Data Build Pipeline
# Chạy từ root: bash tools/build.sh [step]
#
# Steps:
#   all       (mặc định) — chạy toàn bộ pipeline
#   fetch     — chỉ fetch dữ liệu từ KanjiAPI
#   fix       — chỉ chạy các bước fix/patch
#   validate  — chỉ chạy QA
#   clean     — xóa cache files
#
# Yêu cầu: Python 3.8+
# =============================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools"
JS_OUT="$ROOT/js/kanji-data.js"
PYTHON="${PYTHON:-python3}"

# Màu sắc terminal
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${BLUE}[build]${NC} $*"; }
ok()   { echo -e "${GREEN}[  ok ]${NC} $*"; }
warn() { echo -e "${YELLOW}[ warn]${NC} $*"; }
err()  { echo -e "${RED}[error]${NC} $*"; exit 1; }

# Kiểm tra Python
command -v "$PYTHON" >/dev/null 2>&1 || err "Python3 không tìm thấy. Cài tại: https://python.org"

STEP="${1:-all}"

# ------------------------------------------------------------------
step_fetch() {
  log "=== BƯỚC 1: Fetch dữ liệu từ KanjiAPI ==="
  cd "$ROOT"
  "$PYTHON" "$TOOLS/build_kanji_data.py" && ok "build_kanji_data.py xong"
}

# ------------------------------------------------------------------
step_fix() {
  log "=== BƯỚC 2: Fix & patch dữ liệu ==="
  cd "$ROOT"

  # 2a. Fix N5/N4 (readings + meanings cơ bản)
  "$PYTHON" "$TOOLS/fix_n5n4.py"        && ok "fix_n5n4.py xong"

  # 2b. Patch meanings sang tiếng Việt (full pass)
  "$PYTHON" "$TOOLS/patch_vi_full.py"   && ok "patch_vi_full.py xong"
  "$PYTHON" "$TOOLS/patch_vi_meanings.py" && ok "patch_vi_meanings.py xong"

  # 2c. Fix compound words per level
  "$PYTHON" "$TOOLS/fix_words_n4n3.py"  && ok "fix_words_n4n3.py xong"
  "$PYTHON" "$TOOLS/fix_words.py"        && ok "fix_words.py xong"
  "$PYTHON" "$TOOLS/fix_words2.py"       && ok "fix_words2.py xong"

  # 2d. Fix N2, N1 specifics
  "$PYTHON" "$TOOLS/fix_n2.py"           && ok "fix_n2.py xong"
  "$PYTHON" "$TOOLS/fix_n1.py"           && ok "fix_n1.py xong"

  # 2e. Fix meanings còn tiếng Anh
  "$PYTHON" "$TOOLS/fix_english_meanings.py" && ok "fix_english_meanings.py xong"

  # 2f. Apply reference fixes (compare + apply)
  "$PYTHON" "$TOOLS/compare_ref.py"      && ok "compare_ref.py xong"
  "$PYTHON" "$TOOLS/apply_ref_fixes.py"  && ok "apply_ref_fixes.py xong"
  "$PYTHON" "$TOOLS/compare_n4.py"       && ok "compare_n4.py xong"
  "$PYTHON" "$TOOLS/apply_n4_fixes.py"   && ok "apply_n4_fixes.py xong"
  "$PYTHON" "$TOOLS/compare_n3.py"       && ok "compare_n3.py xong"
  "$PYTHON" "$TOOLS/apply_n3_fixes.py"   && ok "apply_n3_fixes.py xong"

  # 2g. Dedup cuối cùng
  "$PYTHON" "$TOOLS/fix_duplicates.py"   && ok "fix_duplicates.py xong"
  "$PYTHON" "$TOOLS/fix_duplicates2.py"  && ok "fix_duplicates2.py xong"
}

# ------------------------------------------------------------------
step_validate() {
  log "=== BƯỚC 3: Validate output ==="
  cd "$ROOT"

  # Syntax check JS
  if command -v node >/dev/null 2>&1; then
    node --check "$JS_OUT" && ok "JS syntax OK"
  else
    warn "node không có — bỏ qua JS syntax check"
  fi

  # QA report
  "$PYTHON" "$TOOLS/qa_kanji.py" && ok "QA report tạo xong → qa_report.json"

  # Đọc summary từ qa_report.json
  if [ -f "$ROOT/qa_report.json" ]; then
    ERRORS=$("$PYTHON" -c "
import json
with open('qa_report.json') as f: d = json.load(f)
s = d.get('summary', {})
print(f\"Total: {s.get('total',0)}  Clean: {s.get('clean',0)}  With errors: {s.get('with_errors',0)}\")
    ")
    log "QA Summary: $ERRORS"

    WITH_ERRORS=$("$PYTHON" -c "
import json
with open('qa_report.json') as f: d = json.load(f)
print(d.get('summary',{}).get('with_errors', 0))
    ")

    if [ "$WITH_ERRORS" -gt 0 ]; then
      warn "$WITH_ERRORS entries vẫn còn lỗi. Xem chi tiết: qa_report.html"
    else
      ok "Tất cả entries sạch lỗi! ✅"
    fi
  fi
}

# ------------------------------------------------------------------
step_clean() {
  log "=== Dọn cache files ==="
  cd "$ROOT"
  rm -f kanji_api_cache.json kanji_words_cache.json
  ok "Đã xóa cache"
}

# ------------------------------------------------------------------
# Entrypoint
case "$STEP" in
  all)
    step_fetch
    echo ""
    step_fix
    echo ""
    step_validate
    echo ""
    ok "=== Pipeline hoàn thành! ==="
    ;;
  fetch)    step_fetch    ;;
  fix)      step_fix      ;;
  validate) step_validate ;;
  clean)    step_clean    ;;
  *)
    echo "Usage: bash tools/build.sh [all|fetch|fix|validate|clean]"
    exit 1
    ;;
esac
