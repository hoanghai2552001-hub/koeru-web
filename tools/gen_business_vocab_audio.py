"""
Sinh audio Google TTS (Chirp3-HD Zephyr) cho từ vựng Business Japanese (business.html).
Output: audio/vocab-business/<kana>.mp3

Chạy:
  GOOGLE_TTS_API_KEY=xxx python tools/gen_business_vocab_audio.py
"""
import base64
import os
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "audio", "vocab-business")

GOOGLE_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY")
GOOGLE_API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
GOOGLE_VOICE = {"name": "ja-JP-Chirp3-HD-Zephyr", "ssmlGender": "FEMALE"}

# Giữ đồng bộ thủ công với TOPIC1_VOCAB / TOPIC2_VOCAB trong business.html
VOCAB = [
    {"w": "予約", "r": "よやく"},
    {"w": "チェックイン", "r": ""},
    {"w": "チェックアウト", "r": ""},
    {"w": "部屋番号", "r": "へやばんごう"},
    {"w": "鍵", "r": "かぎ"},
    {"w": "朝食券", "r": "ちょうしょくけん"},
    {"w": "フロント", "r": ""},
    {"w": "一泊", "r": "いっぱく"},
    {"w": "宿泊料金", "r": "しゅくはくりょうきん"},
    {"w": "かしこまりました", "r": ""},
    {"w": "会計", "r": "かいけい"},
    {"w": "支払い", "r": "しはらい"},
    {"w": "現金", "r": "げんきん"},
    {"w": "カード", "r": ""},
    {"w": "暗証番号", "r": "あんしょうばんごう"},
    {"w": "サイン", "r": ""},
    {"w": "お釣り", "r": "おつり"},
    {"w": "領収書", "r": "りょうしゅうしょ"},
    {"w": "延長", "r": "えんちょう"},
    {"w": "忘れ物", "r": "わすれもの"},
    {"w": "朝食", "r": "ちょうしょく"},
    {"w": "営業時間", "r": "えいぎょうじかん"},
    {"w": "開店", "r": "かいてん"},
    {"w": "閉店", "r": "へいてん"},
    {"w": "会場", "r": "かいじょう"},
    {"w": "奥", "r": "おく"},
    {"w": "突き当たり", "r": "つきあたり"},
    {"w": "エレベーター", "r": ""},
    {"w": "まっすぐ", "r": ""},
    {"w": "案内", "r": "あんない"},
    {"w": "お手洗い", "r": "おてあらい"},
    {"w": "喫煙室", "r": "きつえんしつ"},
    {"w": "廊下", "r": "ろうか"},
    {"w": "階段", "r": "かいだん"},
    {"w": "ロビー", "r": ""},
    {"w": "左手", "r": "ひだりて"},
    {"w": "右手", "r": "みぎて"},
]


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


def main():
    if not GOOGLE_API_KEY:
        print("Thiếu GOOGLE_TTS_API_KEY.")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    done = skipped = failed = 0
    for v in VOCAB:
        key = v["r"] or v["w"]
        out_path = os.path.join(OUT_DIR, f"{key}.mp3")
        if os.path.exists(out_path):
            skipped += 1
            continue
        try:
            audio = synthesize_google(v["w"])
            with open(out_path, "wb") as f:
                f.write(audio)
            print(f"  OK  {key}")
            done += 1
        except Exception as e:
            print(f"  ERR  {key}: {e}")
            failed += 1
        time.sleep(0.15)
    print(f"\nDone: {done}  Skipped: {skipped}  Failed: {failed}")
    print(f"Files saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
