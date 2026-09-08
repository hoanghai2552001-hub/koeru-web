# -*- coding: utf-8 -*-
"""Bóc audio gốc của giáo trình HSK1 ra thư mục chờ duyệt.

Nguồn: Tiếng Trung/HSK1.zip
  "MP3 GIAO TRINH CHUAN HSK1 -GT/NN-M.mp3"  -> audio giáo trình (mặc định)
  "MP3 GIAO TRINH CHUAN HSK1-BT/NN-M.mp3"   -> audio sách bài tập (--baitap)

NN = số bài, M = thứ tự đoạn trong bài (生词 / 课文 1 / 课文 2 / 语音…).
Đây là track theo TỪNG ĐOẠN, không phải từng câu — script chỉ sao chép
nguyên vẹn, KHÔNG cắt, KHÔNG align.

Ra:  audio/_hsk_aligned/lessonNN_MM.mp3   (thư mục staging, đã .gitignore)
Nghe duyệt xong rồi mới chuyển sang audio/hsk-dialogue/.

Chạy:
  python tools/extract_hsk_audio.py --dry-run   # chỉ in bảng thời lượng
  python tools/extract_hsk_audio.py             # bóc ra staging
  python tools/extract_hsk_audio.py lesson3     # riêng bài 3
"""
import os
import re
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_PATH = os.path.join(ROOT, "Tiếng Trung", "HSK1.zip")
OUT_DIR = os.path.join(ROOT, "audio", "_hsk_aligned")
TOTAL_LESSONS = 15

DIR_GT = "MP3 GIAO TRINH CHUAN HSK1 -GT"
DIR_BT = "MP3 GIAO TRINH CHUAN HSK1-BT"

USAGE = (
    "Cách dùng:\n"
    "  python tools/extract_hsk_audio.py [lessonN] [--baitap] [--dry-run]\n"
    "    lessonN    chỉ bóc bài N (1-%d); bỏ trống = tất cả\n"
    "    --baitap   lấy audio sách bài tập thay vì giáo trình\n"
    "    --dry-run  chỉ in bảng thời lượng, không ghi file"
) % TOTAL_LESSONS


def duration(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=20)
        return float(out.stdout.strip())
    except Exception:
        return 0.0


def main():
    lesson_filter = None
    src_dir = DIR_GT
    dry = False

    for arg in sys.argv[1:]:
        if arg == "--dry-run":
            dry = True
        elif arg == "--baitap":
            src_dir = DIR_BT
        elif arg.startswith("lesson"):
            n = arg[len("lesson"):]
            if not n.isdigit() or not (1 <= int(n) <= TOTAL_LESSONS):
                sys.exit("Số bài không hợp lệ: %r\n\n%s" % (arg, USAGE))
            lesson_filter = int(n)
        else:
            sys.exit("Không hiểu tham số: %r\n\n%s" % (arg, USAGE))

    if not os.path.isfile(ZIP_PATH):
        sys.exit("Không thấy %s" % ZIP_PATH)

    zf = zipfile.ZipFile(ZIP_PATH)
    # Tên file dạng "01-9.mp3" nằm trong thư mục src_dir
    pat = re.compile(r"/" + re.escape(src_dir) + r"/(\d{2})-(\d{1,2})\.mp3$")
    found = []
    for name in zf.namelist():
        m = pat.search(name)
        if not m:
            continue
        lesson, track = int(m.group(1)), int(m.group(2))
        if lesson_filter and lesson != lesson_filter:
            continue
        found.append((lesson, track, name))
    found.sort()

    if not found:
        sys.exit("Không thấy file audio nào khớp trong %r.\n\n%s" % (src_dir, USAGE))

    print("Nguồn: %s · %d file\n" % (src_dir, len(found)))
    if not dry:
        os.makedirs(OUT_DIR, exist_ok=True)

    print("Bài | đoạn | thời lượng | file ra")
    print("----|------|------------|---------------------")
    cur = None
    total = 0.0
    for lesson, track, member in found:
        out_name = "lesson%02d_%02d.mp3" % (lesson, track)
        out_path = os.path.join(OUT_DIR, out_name)
        if not dry:
            with open(out_path, "wb") as f:
                f.write(zf.read(member))
            secs = duration(out_path)
        else:
            secs = 0.0
        total += secs
        if lesson != cur:
            cur = lesson
            print("----|------|------------|---------------------")
        print(" %2d |  %2d  | %s | %s"
              % (lesson, track,
                 ("%5.1f s" % secs).rjust(10) if secs else "     —    ",
                 out_name))

    if dry:
        print("\n--dry-run: KHÔNG ghi file. Bỏ --dry-run để bóc ra %s" % OUT_DIR)
        return

    print("\n✓ Đã bóc %d file (%.1f phút) vào audio/_hsk_aligned/" % (len(found), total / 60))
    print("  Thư mục này đã .gitignore — nghe duyệt xong hãy chuyển sang audio/hsk-dialogue/.")
    print("  Lưu ý: đây là track theo ĐOẠN của giáo trình, chưa cắt theo từng câu.")


if __name__ == "__main__":
    main()
