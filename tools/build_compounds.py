"""
Bổ sung từ ghép (compound words) vào kanji-data.js
Nguồn: KanjiAPI /v1/words/{kanji}
Mỗi kanji lấy tối đa 3 từ ghép phổ biến nhất (có kanji representation)

Chạy: python build_compounds.py
"""
import re, json, time, requests, os, sys

BASE     = os.path.dirname(os.path.abspath(__file__))
INPUT_JS = os.path.join(BASE, "js", "kanji-data.js")
CACHE_F  = os.path.join(BASE, "kanji_words_cache.json")
MAX_WORDS = 3  # số từ ghép mỗi kanji

# ── Load cache ──────────────────────────────
def load_cache():
    try:
        with open(CACHE_F, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_cache(c):
    with open(CACHE_F, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)

# ── Katakana → Hiragana ───────────────────
def to_hiragana(s):
    return "".join(
        chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c
        for c in (s or "")
    )

# ── Fetch words from KanjiAPI ─────────────
def fetch_words(kanji, cache):
    if kanji in cache:
        return cache[kanji]
    url = f"https://kanjiapi.dev/v1/words/{kanji}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            cache[kanji] = data
            return data
    except Exception as e:
        print(f"  ERROR {kanji}: {e}")
    cache[kanji] = []
    return []

# ── Pick best compound words ──────────────
def pick_words(kanji, raw_words):
    """
    Chọn MAX_WORDS từ ghép tốt nhất.
    API format: entry = {meanings:[{glosses:[...]}], variants:[{written, pronounced, priorities}]}
    Ưu tiên variants có priority (ichi/news/nf...) — phổ biến hơn
    """
    results = []
    seen = set()

    # Sort: ưu tiên entries có variant phổ biến (có priorities)
    def has_priority(entry):
        for v in entry.get("variants", []):
            if v.get("priorities"):
                return True
        return False
    sorted_words = sorted(raw_words, key=lambda e: 0 if has_priority(e) else 1)

    for entry in sorted_words:
        variants = entry.get("variants", [])
        meanings = entry.get("meanings", [])
        if not variants or not meanings:
            continue

        # Lấy gloss ngắn nhất < 40 ký tự
        gloss = ""
        for m in meanings:
            for g in m.get("glosses", []):
                if len(g) <= 35 and not g.startswith("("):
                    gloss = g
                    break
            if gloss:
                break
        if not gloss:
            # fallback: lấy gloss đầu tiên
            for m in meanings:
                gs = m.get("glosses", [])
                if gs and len(gs[0]) <= 50:
                    gloss = gs[0]
                    break
        if not gloss:
            continue

        # Tìm variant viết bằng kanji (có chứa kanji cần tìm), 2-4 chữ
        for v in sorted(variants, key=lambda x: 0 if x.get("priorities") else 1):
            word_kanji = v.get("written", "")
            reading    = to_hiragana(v.get("pronounced", ""))
            if not word_kanji or word_kanji in seen:
                continue
            if kanji not in word_kanji:
                continue
            if len(word_kanji) < 2 or len(word_kanji) > 4:
                continue
            # Bỏ từ chỉ có hiragana/katakana
            if not any('一' <= c <= '鿿' or '㐀' <= c <= '䶿' for c in word_kanji):
                continue
            seen.add(word_kanji)
            results.append({"w": word_kanji, "r": reading, "m": gloss})
            break

        if len(results) >= MAX_WORDS:
            break

    return results

# ── Parse kanji-data.js ───────────────────
def parse_kanji_list(js_text):
    """Trích kanji từ file JS, trả về list string"""
    return re.findall(r'\{kanji:"([^"]+)"', js_text)

# ── Inject words vào từng entry ───────────
def inject_words(js_text, words_map):
    """
    Thêm words:[...] vào cuối mỗi entry trước dấu }
    Nếu đã có words: thì bỏ qua
    """
    def replacer(m):
        entry = m.group(0)
        kanji_match = re.search(r'kanji:"([^"]+)"', entry)
        if not kanji_match:
            return entry
        k = kanji_match.group(1)
        if "words:" in entry:
            return entry  # đã có rồi
        ws = words_map.get(k, [])
        if not ws:
            return entry
        words_json = json.dumps(ws, ensure_ascii=False)
        # Chèn trước dấu } cuối
        entry = entry.rstrip()
        if entry.endswith("}"):
            entry = entry[:-1] + f',words:{words_json}' + "}"
        return entry

    return re.sub(r'\{kanji:"[^"]+?"(?:[^{}]|\{[^}]*\})*\}', replacer, js_text)

# ── MAIN ──────────────────────────────────
def main():
    print("=== Build Compounds ===")
    with open(INPUT_JS, encoding="utf-8") as f:
        js_text = f.read()

    kanji_list = parse_kanji_list(js_text)
    print(f"Found {len(kanji_list)} kanji entries")

    cache = load_cache()
    words_map = {}
    total = len(kanji_list)

    for i, k in enumerate(kanji_list):
        sys.stdout.write(f"\r  Fetching {i+1}/{total}: {k}   ")
        sys.stdout.flush()
        raw = fetch_words(k, cache)
        ws  = pick_words(k, raw)
        if ws:
            words_map[k] = ws
        # Save cache every 50
        if (i + 1) % 50 == 0:
            save_cache(cache)
        # Rate limit
        if k not in cache or cache[k] == []:
            time.sleep(0.15)

    save_cache(cache)
    print(f"\n  Got compounds for {len(words_map)}/{total} kanji")

    new_js = inject_words(js_text, words_map)

    with open(INPUT_JS, "w", encoding="utf-8") as f:
        f.write(new_js)
    print(f"  Written to {INPUT_JS}")
    print("Done!")

if __name__ == "__main__":
    main()
