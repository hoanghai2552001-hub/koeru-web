"""
Sinh audio hội thoại (会話) từ database/dialogue/n4|n5/*.json bằng Google Cloud
Text-to-Speech (giọng Neural2/WaveNet ja-JP — tự nhiên hơn nhiều so với
Web Speech API đang dùng làm fallback trong minna.html).

Cần GOOGLE_TTS_API_KEY (API key của Google Cloud, bật sẵn Text-to-Speech API).
Lấy tại: https://console.cloud.google.com/apis/credentials
(gói WaveNet/Neural2 có free tier ~1 triệu ký tự/tháng)

Chạy: GOOGLE_TTS_API_KEY=xxx python tools/gen_dialogue_audio.py [n4|n5] [lessonN]
Không có tham số → sinh audio cho tất cả bài đã có hội thoại.

Output: audio/dialogue/<n4|n5>/lesson<N>_<01,02,...>.mp3
(đúng quy ước file mà minna.html đã tự động dò tìm — không cần sửa code JS)
"""
import base64
import glob
import io
import json
import os
import re
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, "database", "dialogue")
OUT_DIR = os.path.join(ROOT, "audio", "dialogue")

API_KEY = os.environ.get("GOOGLE_TTS_API_KEY")
API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

# Chia giọng theo nhân vật lẻ/chẵn trong mỗi bài để hội thoại nghe có 2 giọng khác nhau.
# Neural2 tự nhiên nhất; nếu tài khoản chưa bật Neural2, đổi sang Wavenet bên dưới.
VOICES = [
    {"name": "ja-JP-Neural2-B", "ssmlGender": "FEMALE"},
    {"name": "ja-JP-Neural2-C", "ssmlGender": "MALE"},
]
# Dự phòng nếu Neural2 lỗi (project chưa bật) — bỏ comment dòng dưới để dùng WaveNet:
# VOICES = [
#     {"name": "ja-JP-Wavenet-A", "ssmlGender": "FEMALE"},
#     {"name": "ja-JP-Wavenet-C", "ssmlGender": "MALE"},
# ]


def jp_reading(text):
    """Chuyển '漢字[かな]' -> 'かな', giữ nguyên phần kana/ký tự khác (giống hàm
    jpReading() trong minna.html) — Google TTS đọc kana chuẩn hơn kanji trần
    với các từ đa âm."""
    return re.sub(r"[一-鿿々]+\[([ぁ-ゖー]+)\]", r"\1", text)


def synthesize(text, voice):
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "ja-JP", "name": voice["name"], "ssmlGender": voice["ssmlGender"]},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.92},
    }
    r = requests.post(f"{API_URL}?key={API_KEY}", json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    audio_b64 = r.json()["audioContent"]
    return base64.b64decode(audio_b64)


def load_lessons(level_filter=None, lesson_filter=None):
    lessons = []
    for level in ("n4", "n5"):
        if level_filter and level != level_filter:
            continue
        for path in sorted(glob.glob(os.path.join(DB_DIR, level, "lesson*.json"))):
            d = json.load(io.open(path, encoding="utf-8"))
            if lesson_filter and d["lesson"] != lesson_filter:
                continue
            lessons.append((level, d))
    return lessons


def main():
    if not API_KEY:
        print("Thiếu GOOGLE_TTS_API_KEY. Chạy: GOOGLE_TTS_API_KEY=xxx python tools/gen_dialogue_audio.py")
        sys.exit(1)

    level_filter = None
    lesson_filter = None
    for arg in sys.argv[1:]:
        if arg in ("n4", "n5"):
            level_filter = arg
        elif arg.startswith("lesson"):
            lesson_filter = int(arg.replace("lesson", ""))

    lessons = load_lessons(level_filter, lesson_filter)
    if not lessons:
        print("Không tìm thấy bài nào khớp bộ lọc.")
        sys.exit(1)

    done = skipped = failed = 0
    for level, d in lessons:
        out_dir = os.path.join(OUT_DIR, level)
        os.makedirs(out_dir, exist_ok=True)
        speakers = {}  # tên nhân vật -> voice cố định trong bài (nhất quán giữa các lượt thoại)
        for i, line in enumerate(d["lines"]):
            out_path = os.path.join(out_dir, f"lesson{d['lesson']}_{i+1:02d}.mp3")
            if os.path.exists(out_path):
                skipped += 1
                continue
            spk = line.get("spk", "")
            if spk not in speakers:
                speakers[spk] = VOICES[len(speakers) % len(VOICES)]
            text = jp_reading(line["jp"])
            try:
                audio = synthesize(text, speakers[spk])
                with open(out_path, "wb") as f:
                    f.write(audio)
                print(f"  ✓  {level}/lesson{d['lesson']}_{i+1:02d}.mp3  ({spk})")
                done += 1
            except Exception as e:
                print(f"  ERR  {level}/lesson{d['lesson']}_{i+1:02d}.mp3: {e}")
                failed += 1
            time.sleep(0.15)  # tránh rate limit

    print(f"\nDone: {done}  Skipped: {skipped}  Failed: {failed}")
    print(f"Files saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
