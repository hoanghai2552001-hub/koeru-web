"""
Kiểm tra chất lượng file audio hội thoại đã cắt: đối chiếu độ dài mp3 với số
ký tự thoại thật của từng dòng trong database/dialogue/n4|n5/lessonNN.json.

Ý tưởng: trong cùng 1 bài, tốc độ đọc (giây/ký tự) phải tương đối đều. Dòng nào
lệch xa mức trung vị của bài → nhiều khả năng điểm cắt sai (cắt hụt, cắt lẫn
sang câu khác, hoặc lệch cả đoạn). Script chỉ CẢNH BÁO, không sửa gì.

Dùng sau tools/align_dialogue_audio.py, hoặc để soát lại audio TTS sinh bởi
tools/gen_dialogue_audio.py.

Cần: ffprobe có trong PATH.

Chạy:
  python tools/verify_dialogue_cuts.py                 # tất cả bài
  python tools/verify_dialogue_cuts.py n5              # cả cấp N5
  python tools/verify_dialogue_cuts.py n5 lesson3      # 1 bài
  python tools/verify_dialogue_cuts.py --staging n5    # soát thư mục audio/_aligned/ thay vì audio/dialogue/

Exit code 1 nếu phát hiện dòng bất thường (tiện cho việc chặn deploy).
"""
import glob
import json
import os
import re
import statistics
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, "database", "dialogue")

# ngưỡng lệch so với trung vị tốc độ đọc của chính bài đó
RATIO_MIN = 0.35
RATIO_MAX = 2.8
MIN_ROWS = 3  # dưới 3 dòng có audio thì trung vị không đáng tin -> bỏ qua bài


def jp_len(s):
    # bo ruby [..], dau cau, khoang trang -> dem so ky tu thoai that su
    s = re.sub(r"\[[^\]]*\]", "", s or "")
    s = re.sub(r"[。、？！\s　……]", "", s)
    return len(s)


def duration(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=10,
        )
        return float(out.stdout.strip())
    except Exception:
        return None


def check_lesson(json_path, level, audio_root):
    """Trả về (số dòng có audio, danh sách dòng bất thường)."""
    d = json.load(open(json_path, encoding="utf-8"))
    lesson = d["lesson"]
    rows = []
    for i, line in enumerate(d["lines"]):
        mp3 = os.path.join(audio_root, level, f"lesson{lesson}_{i+1:02d}.mp3")
        if not os.path.exists(mp3):
            continue
        dur = duration(mp3)
        if dur is None:
            continue
        chars = jp_len(line["jp"])
        rows.append((i + 1, chars, dur, dur / chars if chars else None))

    rates = [r[3] for r in rows if r[3]]
    if len(rates) < MIN_ROWS:
        return len(rows), []

    med = statistics.median(rates)
    flagged = []
    for idx, chars, dur, rate in rows:
        if rate is None:
            continue
        ratio = rate / med
        if ratio < RATIO_MIN or ratio > RATIO_MAX:
            flagged.append((level, lesson, idx, chars, round(dur, 2), round(ratio, 2)))
    return len(rows), flagged


def parse_args(argv):
    """[--staging] [n4|n5] [lessonN] — cùng convention với các script audio khác."""
    level, lesson, staging = None, None, False
    for a in argv:
        al = a.lower()
        if al == "--staging":
            staging = True
        elif al in ("n4", "n5"):
            level = al
        else:
            m = re.fullmatch(r"lesson(\d+)", al) or re.fullmatch(r"(\d+)", al)
            if m:
                lesson = int(m.group(1))
            else:
                sys.exit(f"Tham số không hiểu: {a!r}. Dùng: [--staging] [n4|n5] [lessonN]")
    return level, lesson, staging


def main():
    level, lesson, staging = parse_args(sys.argv[1:])
    audio_root = os.path.join(ROOT, "audio", "_aligned" if staging else "dialogue")
    if not os.path.isdir(audio_root):
        sys.exit(f"Không thấy thư mục audio: {audio_root}")

    levels = [level] if level else ["n5", "n4"]
    flagged, total_rows, checked = [], 0, 0

    for lv in levels:
        for jf in sorted(glob.glob(os.path.join(DB_DIR, lv, "lesson*.json"))):
            d = json.load(open(jf, encoding="utf-8"))
            if lesson is not None and d["lesson"] != lesson:
                continue
            n, bad = check_lesson(jf, lv, audio_root)
            total_rows += n
            checked += 1
            flagged.extend(bad)

    print(f"Đã soát {checked} bài, {total_rows} dòng có audio  (nguồn: {audio_root})")
    if not total_rows:
        print("Không có file audio nào để soát.")
        return 0

    print(f"Tổng số dòng bất thường: {len(flagged)}")
    if not flagged:
        print("Không phát hiện dòng nào lệch bất thường.")
        return 0

    lessons_flagged = sorted(set((l, n) for l, n, *_ in flagged))
    print(f"Số bài có bất thường: {len(lessons_flagged)}")
    print("Bài:", lessons_flagged)
    print("\ncấp | bài | dòng | số chữ | thời lượng | lệch so với trung vị")
    for row in flagged:
        print(row)
    print("\nNghe lại các dòng trên trước khi dùng — script chỉ cảnh báo, không tự sửa.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
