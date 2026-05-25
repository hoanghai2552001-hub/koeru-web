"""
Download vocab audio from soundoftext.com (Google TTS)
Saves to audio/vocab/<từ>.mp3
"""
import os, time, requests

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "audio", "vocab")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOCAB = [
    'がくせい','せんせい','かいしゃいん','いしゃ','けんきゅうしゃ','エンジニア',
    'これ','それ','あれ','ほん','ざっし','しんぶん','ノート','テキスト','えんぴつ',
    'かぎ','とけい','かさ','かばん','くるま',
    'ここ','そこ','あそこ','トイレ','エレベーター','かいだん',
    'いま','なんじ','ごぜん','ごご','はん',
    'いくら','みせ','デパート','やおや','にく','さかな','やさい','くだもの','たまご','パン',
    'たべます','のみます','みず','おちゃ','コーヒー','ビール',
    'あさごはん','ひるごはん','ばんごはん',
    'みます','ききます','よみます','かきます','かいます','します',
    'えき','くうこう','びょういん','ぎんこう','ゆうびんきょく',
    'でんしゃ','バス','タクシー','ひこうき',
    'きょう','きのう','あした','まいにち','やすみ','しごと',
    'がっこう','せんしゅう','らいしゅう','れんしゅう',
    'はなします','わかります','あります','います','おきます','ねます',
    'はたらきます','やすみます','べんきょうします','さんぽします',
    'おおきい','ちいさい','あたらしい','ふるい','たかい','やすい',
    'はやい','おそい','あつい','さむい','むずかしい','やさしい',
    'おもしろい','つまらない','いそがしい',
    'きれい','しずか','にぎやか','ゆうめい','べんり','すき','きらい','じょうず','へた',
    'かぞく','おとうさん','おかあさん','おにいさん','おねえさん',
    'おとうと','いもうと','こども','ともだち',
    'スポーツ','サッカー','テニス','おんがく','えいが','りょこう','りょうり',
    'てんき','あめ','ゆき','かぜ','はる','なつ','あき','ふゆ',
    'いろ','しろ','くろ','あか','あお','きいろ',
    'みぎ','ひだり','まっすぐ','となり','まえ','うしろ','うえ','した','なか',
]

API_URL    = "https://api.soundoftext.com/sounds"
STATUS_URL = "https://api.soundoftext.com/sounds/{}"
HEADERS    = {"Content-Type": "application/json"}

def get_sound_id(text):
    payload = {"engine": "Google", "data": {"text": text, "voice": "ja-JP"}}
    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("success"):
        return data["id"]
    raise ValueError(f"API error for '{text}': {data}")

def download_mp3(sound_id, out_path):
    # Poll status endpoint để lấy URL thực
    for _ in range(12):
        r = requests.get(STATUS_URL.format(sound_id), timeout=15)
        data = r.json()
        if data.get("status") == "Done" and data.get("location"):
            mp3_url = data["location"]
            mp3 = requests.get(mp3_url, timeout=15)
            if mp3.status_code == 200 and len(mp3.content) > 1000:
                with open(out_path, "wb") as f:
                    f.write(mp3.content)
                return True
        time.sleep(1)
    return False

done = skipped = failed = 0

for word in VOCAB:
    out = os.path.join(OUTPUT_DIR, f"{word}.mp3")
    if os.path.exists(out):
        print(f"  skip  {word}")
        skipped += 1
        continue
    try:
        sid = get_sound_id(word)
        time.sleep(0.4)   # tránh rate limit
        ok  = download_mp3(sid, out)
        if ok:
            print(f"  ✓     {word}")
            done += 1
        else:
            print(f"  FAIL  {word} (timeout)")
            failed += 1
    except Exception as e:
        print(f"  ERR   {word}: {e}")
        failed += 1
    time.sleep(0.3)

print(f"\nDone: {done}  Skipped: {skipped}  Failed: {failed}")
print(f"Files saved to: {OUTPUT_DIR}")
