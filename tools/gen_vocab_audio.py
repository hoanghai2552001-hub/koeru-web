"""
Sinh audio Google TTS cho từ vựng (vocab) N4/N5 từ database/n4|n5/*.json
Output: audio/vocab/<từ (kana thuần)>.mp3 — đúng convention mà minna.html
đang dùng (hàm vocabKana() trong minna.html: bỏ marker nhóm ⅠⅡⅢ + bỏ [...]).

Cần GOOGLE_TTS_API_KEY (Neural2, giọng tự nhiên hơn Web Speech API fallback).

Chạy:
  GOOGLE_TTS_API_KEY=xxx python tools/gen_vocab_audio.py [n4|n5] [lessonN]

Không có bộ lọc n4/n5/lessonN -> sinh cho tất cả bài.
Dedup theo từ (kana thuần) trên toàn bộ N4+N5 — 1 từ chỉ sinh audio 1 lần
dù xuất hiện ở nhiều bài, và bỏ qua nếu file audio/vocab/<từ>.mp3 đã có sẵn.
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
DB_DIR = os.path.join(ROOT, "database")
OUT_DIR = os.path.join(ROOT, "audio", "vocab")

GOOGLE_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY")
GOOGLE_API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
GOOGLE_VOICE = {"name": "ja-JP-Chirp3-HD-Kore", "ssmlGender": "FEMALE"}


def vocab_kana(w):
    """Giống hệt vocabKana() trong minna.html: bỏ marker nhóm ⅠⅡⅢ (chỉ khi
    đứng cuối/trước [) + bỏ mọi ghi chú trong ngoặc [...]."""
    w = re.sub(r"[ⅠⅡⅢ](?=\s*\[|$)", "", w or "")
    w = re.sub(r"\s*\[[^\]]*\]", "", w).strip()
    return w


def synthesize_google(text):
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "ja-JP", "name": GOOGLE_VOICE["name"], "ssmlGender": GOOGLE_VOICE["ssmlGender"]},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.92},
    }
    r = requests.post(f"{GOOGLE_API_URL}?key={GOOGLE_API_KEY}", json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return base64.b64decode(r.json()["audioContent"])


def load_words(level_filter=None, lesson_filter=None):
    """Trả về list (word_kana, level, lesson) đã dedup theo word_kana,
    giữ thứ tự xuất hiện đầu tiên."""
    seen = set()
    words = []
    for level in ("n4", "n5"):
        if level_filter and level != level_filter:
            continue
        for path in sorted(glob.glob(os.path.join(DB_DIR, level, "lesson*.json"))):
            d = json.load(io.open(path, encoding="utf-8"))
            if lesson_filter and d["lesson"] != lesson_filter:
                continue
            for entry in d.get("vocab", []):
                kana = vocab_kana(entry.get("w", ""))
                if not kana or kana in seen:
                    continue
                seen.add(kana)
                words.append((kana, level, d["lesson"]))
    return words


def main():
    args = sys.argv[1:]
    if not GOOGLE_API_KEY:
        print("Thiếu GOOGLE_TTS_API_KEY. Chạy: GOOGLE_TTS_API_KEY=xxx python tools/gen_vocab_audio.py")
        sys.exit(1)

    level_filter = None
    lesson_filter = None
    for arg in args:
        if arg in ("n4", "n5"):
            level_filter = arg
        elif arg.startswith("lesson"):
            lesson_filter = int(arg.replace("lesson", ""))

    words = load_words(level_filter, lesson_filter)
    if not words:
        print("Không tìm thấy từ nào khớp bộ lọc.")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    done = skipped = failed = 0
    for kana, level, lesson in words:
        out_path = os.path.join(OUT_DIR, f"{kana}.mp3")
        if os.path.exists(out_path):
            skipped += 1
            continue
        try:
            audio = synthesize_google(kana)
            with open(out_path, "wb") as f:
                f.write(audio)
            print(f"  ✓  {kana}  ({level} bài {lesson})")
            done += 1
        except Exception as e:
            print(f"  ERR  {kana}  ({level} bài {lesson}): {e}")
            failed += 1
        time.sleep(0.15)

    print(f"\nDone: {done}  Skipped: {skipped}  Failed: {failed}")
    print(f"Files saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
