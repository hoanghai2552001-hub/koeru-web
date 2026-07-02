"""
watch_excel.py — Auto-sync khi Excel thay đổi (Tier 3: Loop Architecture)

Chạy ngầm trong terminal riêng:
    python tools/watch_excel.py

Khi phát hiện kanji_KOERU_full.xlsx thay đổi → tự động chạy sync_kanji_excel.py
Ctrl+C để dừng.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXCEL_PATH = ROOT / "input" / "excel" / "kanji_KOERU_full.xlsx"
SYNC_CMD = [sys.executable, str(ROOT / "tools" / "sync_kanji_excel.py")]
LOG_FILE = ROOT / "tools" / "watch_log.txt"
POLL_INTERVAL = 5  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watch] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def run_sync():
    log.info("Excel changed → running sync_kanji_excel.py ...")
    start = time.time()
    result = subprocess.run(SYNC_CMD, capture_output=True, text=True, cwd=ROOT)
    elapsed = time.time() - start

    if result.returncode == 0:
        # Print last 5 lines of stdout (summary)
        lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
        for line in lines[-5:]:
            log.info(f"  {line}")
        log.info(f"Sync done in {elapsed:.1f}s")
    else:
        log.error(f"Sync failed (exit {result.returncode}):")
        for line in result.stderr.strip().splitlines()[-10:]:
            log.error(f"  {line}")


def main():
    if not EXCEL_PATH.exists():
        log.error(f"Excel not found: {EXCEL_PATH}")
        log.error("Đặt file kanji_KOERU_full.xlsx vào input/excel/ rồi chạy lại.")
        sys.exit(1)

    last_mtime = get_mtime(EXCEL_PATH)
    log.info(f"Watching: {EXCEL_PATH.name}")
    log.info(f"Poll interval: {POLL_INTERVAL}s | Log: {LOG_FILE.name}")
    log.info("Ctrl+C để dừng.\n")

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_mtime = get_mtime(EXCEL_PATH)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                run_sync()
    except KeyboardInterrupt:
        log.info("Watchdog stopped.")


if __name__ == "__main__":
    main()
