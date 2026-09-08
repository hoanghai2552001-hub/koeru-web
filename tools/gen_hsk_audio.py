# -*- coding: utf-8 -*-
"""
Sinh audio Google TTS cho từ vựng HSK 1·2·3 từ database/hsk<N>/*.json
Output: audio/hsk/<chữ Hán>.mp3 — đúng đường dẫn hsk.html đang gọi.

Cần GOOGLE_TTS_API_KEY.

Chạy:
  GOOGLE_TTS_API_KEY=xxx python tools/gen_hsk_audio.py             # tất cả bài
  GOOGLE_TTS_API_KEY=xxx python tools/gen_hsk_audio.py lesson3     # riêng bài 3
  GOOGLE_TTS_API_KEY=xxx python tools/gen_hsk_audio.py --dialogue  # thêm câu hội thoại

Dedup theo chữ Hán trên toàn bộ 15 bài — 1 từ chỉ sinh 1 lần, và bỏ qua nếu
file đã tồn tại. Tham số không nhận diện được thì BÁO LỖI và dừng (không âm
thầm chạy toàn bộ làm đốt quota).
"""
import base64
import glob
import re
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "audio", "hsk")
LESSON_COUNT = {1: 15, 2: 15, 3: 20}

# Chirp3-HD từ chối câu quá dài ("This request contains sentences that are too
# long"). Bài đọc dài trong giáo trình vượt ngưỡng này — bỏ qua, trang web sẽ tự
# rơi về giọng đọc của trình duyệt vốn không giới hạn độ dài.
MAX_TTS_CHARS = 90

GOOGLE_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY")
GOOGLE_API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
GOOGLE_VOICE = {"name": "cmn-CN-Chirp3-HD-Zephyr", "ssmlGender": "FEMALE"}

USAGE = (
    "Cách dùng:\n"
    "  python tools/gen_hsk_audio.py [hsk1|hsk2|hsk3] [lessonN] [--dialogue] [--dry-run]\n"
    "    hskN        chỉ cấp đó; bỏ trống = cả 3 cấp\n"
    "    lessonN     chỉ bài N; bỏ trống = tất cả các bài\n"
    "    --dialogue  sinh thêm audio cho từng câu hội thoại\n"
    "    --dry-run   chỉ liệt kê sẽ sinh những gì, KHÔNG gọi API"
)


def synthesize_google(text):
    import requests
    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": "cmn-CN",
            "name": GOOGLE_VOICE["name"],
            "ssmlGender": GOOGLE_VOICE["ssmlGender"],
        },
        # Chậm hơn mặc định một chút để người mới nghe rõ thanh điệu
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.9},
    }
    r = requests.post("%s?key=%s" % (GOOGLE_API_URL, GOOGLE_API_KEY), json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError("%s: %s" % (r.status_code, r.text[:300]))
    return base64.b64decode(r.json()["audioContent"])


def load_texts(levels, lesson_filter, with_dialogue):
    """Trả về list (text, nhãn) đã dedup theo text trên TOÀN BỘ các cấp — một từ
    xuất hiện ở cả HSK2 lẫn HSK3 chỉ sinh audio một lần (tên file theo chữ Hán)."""
    seen, out = set(), []
    for lv in levels:
        db = os.path.join(ROOT, "database", "hsk%d" % lv)
        for path in sorted(glob.glob(os.path.join(db, "lesson*.json"))):
            d = json.load(io.open(path, encoding="utf-8"))
            if lesson_filter and d["lesson"] != lesson_filter:
                continue
            for v in d.get("vocab", []):
                h = (v.get("h") or "").strip()
                # "哪(哪儿)" -> đọc dạng chính, bỏ phần trong ngoặc
                h = h.split("(")[0].split("（")[0].strip()
                if h and h not in seen:
                    seen.add(h)
                    out.append((h, "HSK%d bài %d · từ vựng" % (lv, d["lesson"])))
            if with_dialogue:
                for line in d.get("dialogue", []):
                    zh = (line.get("zh") or "").strip()
                    if zh and zh not in seen:
                        seen.add(zh)
                        out.append((zh, "HSK%d bài %d · hội thoại" % (lv, d["lesson"])))
    return out


def main():
    lesson_filter = None
    with_dialogue = False
    dry = False
    levels = []

    for arg in sys.argv[1:]:
        low = arg.lower()
        if arg == "--dialogue":
            with_dialogue = True
        elif arg == "--dry-run":
            dry = True
        elif re.fullmatch(r"hsk[123]", low):
            levels.append(int(low[-1]))
        elif low.startswith("lesson"):
            n = low[len("lesson"):]
            if not n.isdigit() or not (1 <= int(n) <= 20):
                sys.exit("Số bài không hợp lệ: %r\n\n%s" % (arg, USAGE))
            lesson_filter = int(n)
        else:
            # Không đoán bừa: gõ sai mà vẫn chạy hết là đốt quota TTS
            sys.exit("Không hiểu tham số: %r\n\n%s" % (arg, USAGE))
    levels = sorted(set(levels)) or [1, 2, 3]
    if lesson_filter and lesson_filter > max(LESSON_COUNT[lv] for lv in levels):
        sys.exit("Cấp đã chọn không có bài %d.\n\n%s" % (lesson_filter, USAGE))

    if not dry and not GOOGLE_API_KEY:
        sys.exit("Thiếu GOOGLE_TTS_API_KEY.\n"
                 "  PowerShell:  $env:GOOGLE_TTS_API_KEY='xxx'\n\n" + USAGE)

    items = load_texts(levels, lesson_filter, with_dialogue)
    if not items:
        sys.exit("Không có nội dung nào khớp bộ lọc.\n\n" + USAGE)

    have = [(t, lb) for t, lb in items if os.path.exists(os.path.join(OUT_DIR, t + ".mp3"))]
    toolong = [(t, lb) for t, lb in items
               if (t, lb) not in have and len(t) > MAX_TTS_CHARS]
    todo = [(t, lb) for t, lb in items
            if (t, lb) not in have and len(t) <= MAX_TTS_CHARS]
    print("Khớp %d mục · đã có sẵn %d · sẽ gọi API %d lần" % (len(items), len(have), len(todo)))
    if toolong:
        print("Bỏ qua %d đoạn dài quá %d ký tự (TTS từ chối; web dùng giọng trình duyệt):"
              % (len(toolong), MAX_TTS_CHARS))
        for t, lb in toolong:
            print("   %s — %d ký tự" % (lb, len(t)))
    if dry:
        for t, lb in todo:
            print("   %-14s %s" % (t, lb))
        print("\n--dry-run: KHÔNG gọi API.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    done = failed = 0
    for text, label in todo:
        try:
            audio = synthesize_google(text)
            with open(os.path.join(OUT_DIR, text + ".mp3"), "wb") as f:
                f.write(audio)
            print("  ✓  %-14s %s" % (text, label))
            done += 1
        except Exception as e:
            print("  ERR %-14s %s: %s" % (text, label, e))
            failed += 1
        time.sleep(0.15)

    print("\nXong: %d · Bỏ qua (đã có): %d · Lỗi: %d" % (done, len(items) - len(todo), failed))
    print("Lưu tại: %s" % OUT_DIR)


if __name__ == "__main__":
    main()
