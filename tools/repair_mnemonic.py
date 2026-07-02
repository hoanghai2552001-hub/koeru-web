"""
repair_mnemonic.py — Collapse double-escaped backslashes in kanji-map-data.js
Bug: js_str() trong sync_kanji_excel.py double-escape backslash mỗi lần sync.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "kanji-map-data.js"


def fully_decode_js_str(s: str) -> str:
    """Collapse all levels of JS double-escaping cho đến khi ổn định."""
    prev = None
    iterations = 0
    while prev != s:
        prev = s
        # Decode one level: \\ -> \, \" -> ", \' -> '
        s = s.replace("\\\\", "\x00BKSL\x00")  # placeholder
        s = s.replace('\\"', '"')
        s = s.replace("\\'", "'")
        s = s.replace("\x00BKSL\x00", "\\")
        iterations += 1
        if iterations > 100:  # safety
            break
    return s


def fix_field(m: re.Match) -> str:
    field_name = m.group(1)
    raw = m.group(2)
    fixed = fully_decode_js_str(raw)
    return f'{field_name}:"{fixed}"'


def main():
    print(f"Loading {TARGET.name}...")
    content = TARGET.read_text(encoding="utf-8")
    before = len(content)
    print(f"Before: {before:,} bytes ({before/1024/1024:.1f} MB)")

    # Fix mnemonic and mn_vi fields
    content = re.sub(
        r'(mnemonic|mn_vi):"((?:[^"\\]|\\.)*)"',
        fix_field,
        content
    )

    after = len(content)
    print(f"After:  {after:,} bytes ({after/1024/1024:.1f} MB)")
    print(f"Reduced: {(before - after)/1024/1024:.1f} MB")

    TARGET.write_text(content, encoding="utf-8")
    print("Saved.")

    # Show sample mnemonic to verify
    m = re.search(r'mnemonic:"([^"]{1,200})"', content)
    if m:
        print(f"\nSample mnemonic (first 100 chars): {m.group(1)[:100]}")


if __name__ == "__main__":
    main()
