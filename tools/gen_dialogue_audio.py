"""
Sinh audio hội thoại (会話) từ database/dialogue/n4|n5/*.json — tự nhiên hơn
Web Speech API đang dùng làm fallback trong minna.html.

2 engine:
  soundoftext (mặc định) — KHÔNG cần API key, dùng chung API mà
      tools/download_vocab_audio.py đã dùng để tạo audio/vocab/*.mp3.
      Giọng ja-JP đơn (Google TTS), không phân biệt nhân vật.
  google — cần GOOGLE_TTS_API_KEY (Neural2/WaveNet, tự nhiên hơn, mỗi
      nhân vật 1 giọng nam/nữ riêng). Lấy key tại
      https://console.cloud.google.com/apis/credentials
      (free tier ~1 triệu ký tự/tháng cho WaveNet/Neural2)

Chạy:
  python tools/gen_dialogue_audio.py [n4|n5] [lessonN]                # soundoftext, không cần key
  GOOGLE_TTS_API_KEY=xxx python tools/gen_dialogue_audio.py --engine google [n4|n5] [lessonN]

Không có bộ lọc n4/n5/lessonN → sinh audio cho tất cả bài đã có hội thoại.

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

# --- engine: soundoftext.com (không cần key, giống tools/download_vocab_audio.py) ---
SOT_API_URL = "https://api.soundoftext.com/sounds"
SOT_STATUS_URL = "https://api.soundoftext.com/sounds/{}"

# --- engine: Google Cloud TTS (cần GOOGLE_TTS_API_KEY, giọng tốt hơn + phân biệt nhân vật) ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY")
GOOGLE_API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
GOOGLE_VOICES = [
    {"name": "ja-JP-Neural2-B", "ssmlGender": "FEMALE"},
    {"name": "ja-JP-Neural2-C", "ssmlGender": "MALE"},
]
# Dự phòng nếu Neural2 lỗi (project chưa bật) — bỏ comment để dùng WaveNet:
# GOOGLE_VOICES = [
#     {"name": "ja-JP-Wavenet-A", "ssmlGender": "FEMALE"},
#     {"name": "ja-JP-Wavenet-C", "ssmlGender": "MALE"},
# ]


def jp_reading(text):
    """Chuyển '漢字[かな]' -> 'かな', giữ nguyên phần kana/ký tự khác (giống hàm
    jpReading() trong minna.html) — TTS đọc kana chuẩn hơn kanji trần với các
    từ đa âm."""
    return re.sub(r"[一-鿿々]+\[([ぁ-ゖー]+)\]", r"\1", text)


def synthesize_soundoftext(text, voice=None):
    payload = {"engine": "Google", "data": {"text": text, "voice": "ja-JP"}}
    r = requests.post(SOT_API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"API error: {data}")
    sound_id = data["id"]
    for _ in range(12):
        r = requests.get(SOT_STATUS_URL.format(sound_id), timeout=15)
        data = r.json()
        if data.get("status") == "Done" and data.get("location"):
            mp3 = requests.get(data["location"], timeout=15)
            if mp3.status_code == 200 and len(mp3.content) > 1000:
                return mp3.content
            raise RuntimeError("download thất bại hoặc file rỗng")
        time.sleep(1)
    raise RuntimeError("timeout chờ soundoftext xử lý")


def synthesize_google(text, voice):
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "ja-JP", "name": voice["name"], "ssmlGender": voice["ssmlGender"]},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.92},
    }
    r = requests.post(f"{GOOGLE_API_URL}?key={GOOGLE_API_KEY}", json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return base64.b64decode(r.json()["audioContent"])


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
    args = sys.argv[1:]
    engine = "soundoftext"
    if "--engine" in args:
        i = args.index("--engine")
        engine = args[i + 1]
        del args[i:i + 2]

    if engine == "google" and not GOOGLE_API_KEY:
        print("Thiếu GOOGLE_TTS_API_KEY. Chạy: GOOGLE_TTS_API_KEY=xxx python tools/gen_dialogue_audio.py --engine google")
        sys.exit(1)
    if engine not in ("soundoftext", "google"):
        print(f"Engine không hợp lệ: {engine} (chỉ nhận soundoftext hoặc google)")
        sys.exit(1)

    level_filter = None
    lesson_filter = None
    for arg in args:
        if arg in ("n4", "n5"):
            level_filter = arg
        elif arg.startswith("lesson"):
            lesson_filter = int(arg.replace("lesson", ""))

    lessons = load_lessons(level_filter, lesson_filter)
    if not lessons:
        print("Không tìm thấy bài nào khớp bộ lọc.")
        sys.exit(1)

    print(f"Engine: {engine}")
    done = skipped = failed = 0
    for level, d in lessons:
        out_dir = os.path.join(OUT_DIR, level)
        os.makedirs(out_dir, exist_ok=True)
        speakers = {}  # tên nhân vật -> voice cố định trong bài (chỉ dùng với engine google)
        for i, line in enumerate(d["lines"]):
            out_path = os.path.join(out_dir, f"lesson{d['lesson']}_{i+1:02d}.mp3")
            if os.path.exists(out_path):
                skipped += 1
                continue
            spk = line.get("spk", "")
            text = jp_reading(line["jp"])
            try:
                if engine == "google":
                    if spk not in speakers:
                        speakers[spk] = GOOGLE_VOICES[len(speakers) % len(GOOGLE_VOICES)]
                    audio = synthesize_google(text, speakers[spk])
                else:
                    audio = synthesize_soundoftext(text)
                with open(out_path, "wb") as f:
                    f.write(audio)
                print(f"  ✓  {level}/lesson{d['lesson']}_{i+1:02d}.mp3  ({spk})")
                done += 1
            except Exception as e:
                print(f"  ERR  {level}/lesson{d['lesson']}_{i+1:02d}.mp3: {e}")
                failed += 1
            time.sleep(0.4 if engine == "soundoftext" else 0.15)  # tránh rate limit

    print(f"\nDone: {done}  Skipped: {skipped}  Failed: {failed}")
    print(f"Files saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
