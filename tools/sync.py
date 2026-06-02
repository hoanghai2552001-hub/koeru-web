#!/usr/bin/env python3
"""
KOERU — Quick Sync (shortcut cho build.py --quick)
====================================================
Dùng: python tools/sync.py       ← sync data + bump version (nhanh)
      python tools/build.py      ← full build (+ Excel + study HTML)
"""
import sys, subprocess
from pathlib import Path

def main():
    build = Path(__file__).parent / "build.py"
    subprocess.run([sys.executable, str(build), "--quick"])

if __name__ == "__main__":
    main()
