"""
bump_cache.py — Cache-busting tự động theo nội dung file.

Quét các file *.html ở thư mục gốc, tìm tham chiếu dạng:
    src="js/foo.js?v=..."   href="css/bar.css?v=..."
rồi đặt ?v= = 8 ký tự đầu của md5(nội dung file).

→ Version chỉ đổi khi file thực sự đổi (idempotent, chạy lại bao nhiêu lần
  cũng cho kết quả như nhau). Không invalidate cache thừa.

Dùng:
    python tools/bump_cache.py          # cập nhật + in các thay đổi
    python tools/bump_cache.py --check  # chỉ báo file lệch, không sửa (exit 1 nếu có)
"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# src="path?v=ver" hoặc href="path?v=ver" — bắt path local + version cũ
REF_RE = re.compile(r'(?P<attr>\b(?:src|href)=")(?P<path>[^"?]+)\?v=(?P<ver>[^"]*)"')


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def process(html_path: Path, check_only: bool):
    text = html_path.read_text(encoding="utf-8")
    changes = []

    def repl(m):
        ref = m.group("path")
        # Bỏ qua URL ngoài
        if ref.startswith(("http://", "https://", "//")):
            return m.group(0)
        asset = (html_path.parent / ref).resolve()
        if not asset.is_file():
            return m.group(0)  # file không tồn tại → để nguyên
        new_ver = file_hash(asset)
        old_ver = m.group("ver")
        if new_ver != old_ver:
            changes.append((ref, old_ver, new_ver))
        return f'{m.group("attr")}{ref}?v={new_ver}"'

    new_text = REF_RE.sub(repl, text)
    if changes and not check_only:
        html_path.write_text(new_text, encoding="utf-8")
    return changes


def main():
    check_only = "--check" in sys.argv
    html_files = sorted(ROOT.glob("*.html"))
    total = 0
    for html in html_files:
        changes = process(html, check_only)
        if changes:
            total += len(changes)
            print(f"\n{html.name}:")
            for ref, old, new in changes:
                print(f"  {ref}: {old or '(trống)'} -> {new}")

    if total == 0:
        print("Cache-busting: tất cả version đã khớp nội dung. Không cần đổi.")
        return 0
    if check_only:
        print(f"\n[--check] {total} tham chiếu lệch version. Chạy lại không kèm --check để sửa.")
        return 1
    print(f"\nĐã cập nhật {total} tham chiếu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
