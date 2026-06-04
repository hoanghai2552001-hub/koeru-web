#!/usr/bin/env python3
"""
KOERU Pre-commit Check — Excel vs JS Sync Guard

Chặn commit nếu input/excel/kanji_KOERU_full.xlsx mới hơn
bất kỳ JS data file nào (kanji-data-n*.js, kanji-data.js).

Nếu Excel không tồn tại (CI, máy khác không có file) → bỏ qua, cho phép commit.
"""
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
EXCEL = ROOT / "input" / "excel" / "kanji_KOERU_full.xlsx"

JS_FILES = [
    "js/kanji-data-n5.js",
    "js/kanji-data-n4.js",
    "js/kanji-data-n3.js",
    "js/kanji-data-n2.js",
    "js/kanji-data-n1.js",
    "js/kanji-data.js",
]


def fmt_time(mtime: float) -> str:
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")


def check() -> int:
    # Không có Excel → không kiểm tra được → cho phép commit
    if not EXCEL.exists():
        return 0

    excel_mtime = EXCEL.stat().st_mtime
    stale_files = []

    for rel in JS_FILES:
        js_path = ROOT / rel
        if not js_path.exists():
            stale_files.append((rel, "file không tồn tại"))
            continue
        js_mtime = js_path.stat().st_mtime
        if excel_mtime > js_mtime:
            delta = excel_mtime - js_mtime
            stale_files.append((rel, f"JS cũ hơn Excel {delta:.0f}s"))

    if not stale_files:
        # Tất cả JS đã được sync
        return 0

    # Block commit
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  🔴 COMMIT BỊ CHẶN — Excel chưa được sync sang JS  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"  Excel:  {EXCEL.relative_to(ROOT)}")
    print(f"  Sửa lúc: {fmt_time(excel_mtime)}")
    print()
    print("  File JS bị lỗi thời:")
    for fname, reason in stale_files:
        print(f"    ✗  {fname}  ({reason})")
    print()
    print("  ▶  Chạy để fix:")
    print("     python tools/sync_kanji_excel.py")
    print()
    print("  Sau khi sync xong, commit lại bình thường.")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(check())
