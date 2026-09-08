# -*- coding: utf-8 -*-
"""Nhận diện 85 track audio giáo trình HSK: track nào là đoạn nào.

Không cần nghe tay. Mỗi track trong giáo trình đều được người đọc xướng tên
ở đầu ("第3课 你叫什么名字，课文一，…"), nên chỉ cần Speech-to-Text 55 giây
đầu là biết chắc. Sau đó đối chiếu chéo với database/hsk<N>/*.json.

Cần GOOGLE_STT_API_KEY. Transcript được lưu cache nên chạy lại KHÔNG tốn tiền.

Chạy:
  python tools/qa_hsk_audio.py --dry-run   # chỉ xem sẽ gọi API bao nhiêu lần
  python tools/qa_hsk_audio.py             # nhận diện + in bảng đối chiếu
  python tools/qa_hsk_audio.py --write     # ghi thêm database/hsk<N>/audio_map.json
"""
import base64, glob, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "audio", "_hsk_aligned")
CACHE = os.path.join(SRC_DIR, "_transcripts.json")
KEY = os.environ.get("GOOGLE_STT_API_KEY")
STT_URL = "https://speech.googleapis.com/v1/speech:recognize"
MAX_SECONDS = 55           # speech:recognize đồng bộ giới hạn 60s

USAGE = ("Cách dùng:\n"
         "  python tools/qa_hsk_audio.py [--dry-run] [--write] [--force]\n"
         "    --dry-run  chỉ đếm số lần sẽ gọi API\n"
         "    --write    ghi kết quả ra database/hsk<N>/audio_map.json\n"
         "    --force    bỏ qua cache, nhận dạng lại từ đầu (TỐN TIỀN)")

# Số Hán trong lời xướng: "课文一" / "课文二" / "课文三"
CN_ORD = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}

# STT nghe nhầm có hệ thống ở lời xướng số thứ tự đoạn 课文N.
# Đây là các dạng đã thực sự gặp trong 85 transcript, không phải đoán:
#   课文二 -> "课文儿" (二 èr ≈ 儿 ér — lỗi phổ biến nhất, 7 track)
#   课文一 -> "课文以为" / "课文艺" / "课文以"
#   课文三 -> "课文山" (sān ≈ shān)
_SEP = r"[\s，,。、]*"          # STT hay chèn dấu phẩy vào giữa ("和文，一则天")
KEWEN_MISHEARD = [
    (r"课文" + _SEP + r"儿", 2),
    (r"(?:课文|克文|和文)" + _SEP + r"(?:以为|一位|一则|以|艺|一)", 1),
    (r"课文" + _SEP + r"(?:山|散)", 3),
]
# "课文" nhưng số thứ tự bị nuốt hẳn ("课文发信息…", "课文382 304…").
# Biết chắc là 课文, chưa biết đoạn mấy — để bước suy theo thứ tự điền nốt.
KEWEN_NO_NUM = r"课文"

# Loại đoạn suy từ nội dung khi lời xướng không nói rõ.
# Thứ tự quan trọng: mục cụ thể hơn phải đứng trước.
SECTION_RULES = [
    ("课堂用语", r"课堂用语"),
    ("练习",    r"看图片朗读|听录音并跟[读毒赌]|朗读下列|朗读夏令营节"),
    ("语音",    r"声母|生母|韵母|变调|轻声|声调|儿化|隔音符号|注意.{0,6}读音|注意.{0,6}读法"),
    ("生词",    r"生词"),
]


def transcribe(path):
    import requests
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "_hsk_stt.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-t", str(MAX_SECONDS),
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", tmp], check=True)
    body = {
        "config": {"encoding": "LINEAR16", "sampleRateHertz": 16000, "audioChannelCount": 1,
                   "languageCode": "zh-CN", "enableAutomaticPunctuation": True},
        "audio": {"content": base64.b64encode(open(tmp, "rb").read()).decode()},
    }
    r = requests.post("%s?key=%s" % (STT_URL, KEY), json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError("%s: %s" % (r.status_code, r.text[:200]))
    return "".join(a["alternatives"][0]["transcript"]
                   for a in r.json().get("results", []))


def classify(txt, lesson, db):
    """Đoán track này là đoạn gì, dựa vào lời xướng + đối chiếu nội dung bài."""
    head = txt[:80]                       # lời xướng luôn ở ngay đầu
    flat = re.sub(r"[^一-鿿]", "", txt)

    kind, detail, why = "?", "", ""

    m = re.search(r"课文\s*([一二三四五六])", head)
    if m:
        kind, detail = "课文", CN_ORD[m.group(1)]
        why = "lời xướng"
    if kind == "?":
        for pat, part in KEWEN_MISHEARD:
            if re.search(pat, head):
                kind, detail, why = "课文", part, "lời xướng (STT nghe nhầm số đoạn)"
                break
    if kind == "?" and re.search(KEWEN_NO_NUM, head):
        kind, detail, why = "课文", "", "lời xướng có 课文 nhưng nuốt mất số đoạn"
    if kind == "?":
        for label, pat in SECTION_RULES:
            if re.search(pat, head):
                kind, why = label, "lời xướng"
                break

    # Đối chiếu chéo với dữ liệu bài: câu thoại nào xuất hiện trong transcript
    hits = []
    for d in db.get("dialogue", []):
        body = re.sub(r"[^一-鿿]", "", d["zh"])
        if len(body) >= 4 and body in flat:
            hits.append(d["part"])
    if hits:
        top = max(set(hits), key=hits.count)
        if kind == "?" or (kind == "课文" and not detail):
            kind, detail = "课文", top
            why = (why + " + " if why else "") + "khớp %d câu thoại" % len(hits)
        elif kind == "课文" and detail and detail != top:
            why += " ⚠ lời xướng nói 课文%s nhưng nội dung khớp 课文%s" % (detail, top)
        else:
            why += " + khớp %d câu thoại" % len(hits)

    # Đếm từ vựng của bài xuất hiện — track 生词 sẽ trúng rất nhiều
    vocab_hits = sum(1 for v in db.get("vocab", [])
                     if len(v["h"]) >= 1 and re.sub(r"[^一-鿿]", "", v["h"]) in flat)
    if kind == "?" and vocab_hits >= 5:
        kind, why = "生词", "trúng %d/%d từ của bài" % (vocab_hits, len(db.get("vocab", [])))

    # Kiểm tra số bài trong lời xướng có khớp tên file không
    mn = re.search(r"第\s*(\d+|[一二三四五六七八九十]+)\s*[课可克]", head)
    warn = ""
    if mn:
        raw = mn.group(1)
        n = int(raw) if raw.isdigit() else None
        if n and n != lesson:
            warn = " 🔴 lời xướng nói BÀI %d nhưng tên file là bài %d" % (n, lesson)
    return kind, detail, why, vocab_hits, warn


def main():
    dry = "--dry-run" in sys.argv
    write = "--write" in sys.argv
    force = "--force" in sys.argv
    for a in sys.argv[1:]:
        if a not in ("--dry-run", "--write", "--force"):
            sys.exit("Không hiểu tham số: %r\n\n%s" % (a, USAGE))

    files = sorted(glob.glob(os.path.join(SRC_DIR, "lesson*.mp3")))
    if not files:
        sys.exit("Không thấy track nào trong audio/_hsk_aligned/\n"
                 "  Chạy trước: python tools/extract_hsk_audio.py")

    cache = {}
    if os.path.isfile(CACHE) and not force:
        cache = json.load(io.open(CACHE, encoding="utf-8"))

    todo = [f for f in files if os.path.basename(f) not in cache]
    print("%d track · đã có transcript %d · cần nhận dạng %d"
          % (len(files), len(files) - len(todo), len(todo)))
    if dry:
        print("\n--dry-run: KHÔNG gọi API.")
        return
    if todo and not KEY:
        sys.exit("Thiếu GOOGLE_STT_API_KEY.\n"
                 "  PowerShell:  $env:GOOGLE_STT_API_KEY='xxx'\n\n" + USAGE)

    for i, f in enumerate(todo, 1):
        name = os.path.basename(f)
        try:
            cache[name] = transcribe(f)
            print("  [%d/%d] %s" % (i, len(todo), name))
        except Exception as e:
            print("  [%d/%d] %s — LỖI: %s" % (i, len(todo), name, e))
            cache[name] = ""
        with io.open(CACHE, "w", encoding="utf-8") as fh:   # lưu ngay, đứt mạng không mất tiền đã trả
            fh.write(json.dumps(cache, ensure_ascii=False, indent=1))

    # ── Đối chiếu & báo cáo ──
    db_cache = {}
    def get_db(lv, n):
        k = (lv, n)
        if k not in db_cache:
            p = os.path.join(ROOT, "database", "hsk%d" % lv, "lesson%02d.json" % n)
            db_cache[k] = json.load(io.open(p, encoding="utf-8")) if os.path.isfile(p) else {}
        return db_cache[k]

    print("\nAudio giáo trình HSK1 — track nào là đoạn nào")
    print("=" * 78)
    print("track            | đoạn      | căn cứ")
    print("-----------------|-----------|" + "-" * 46)

    rows = []
    for f in files:
        name = os.path.basename(f)
        m = re.match(r"lesson(\d+)_(\d+)\.mp3$", name)
        if not m:
            continue
        lesson, track = int(m.group(1)), int(m.group(2))
        kind, detail, why, vh, warn = classify(cache.get(name, ""), lesson, get_db(1, lesson))
        rows.append({"lesson": lesson, "track": track, "file": name,
                     "kind": kind, "part": detail, "why": why, "warn": warn})

    # ── Suy theo thứ tự: giáo trình xếp 课文1 → 课文2 → 课文3 rồi mới tới
    # 语音/练习. Track nào chắc chắn là 课文 mà STT nuốt mất số, hoặc chưa nhận
    # ra gì nhưng nằm KẸP GIỮA hai đoạn 课文 đã xác nhận, thì điền nốt số còn
    # trống. Đánh dấu riêng để biết đây là suy, không phải nghe thấy. ──
    for lesson in sorted(set(r["lesson"] for r in rows)):
        grp = [r for r in rows if r["lesson"] == lesson]
        known = [r for r in grp if r["kind"] == "课文" and r["part"]]
        if not known:
            continue
        taken = set(r["part"] for r in known)
        lo, hi = min(r["track"] for r in known), max(r["track"] for r in known)
        for r in grp:
            if r["part"]:
                continue
            gap = r["kind"] == "课文" or (r["kind"] == "?" and lo < r["track"] < hi)
            if not gap:
                continue
            free = [p for p in (1, 2, 3, 4) if p not in taken]
            if not free:
                continue
            # trong một bài, thứ tự track trùng thứ tự đoạn
            after = [k["part"] for k in known if k["track"] < r["track"]]
            want = (max(after) + 1) if after else free[0]
            if want not in free:
                want = free[0]
            r["kind"], r["part"] = "课文", want
            r["why"] = ("suy theo thứ tự (kẹp giữa các đoạn đã xác nhận)"
                        if not r["why"] else r["why"] + " → suy số đoạn theo thứ tự")
            taken.add(want)

    amap, warns, unknown = {}, [], []
    cur = None
    for r in rows:
        if r["lesson"] != cur:
            cur = r["lesson"]
            print("-----------------|-----------|" + "-" * 46)
        label = r["kind"] + (str(r["part"]) if r["part"] else "")
        if r["kind"] == "?":
            unknown.append(r["file"])
        if r["warn"]:
            warns.append(r["file"] + r["warn"])
        print(" %-15s | %-9s | %s%s" % (r["file"], label, r["why"] or "—", r["warn"]))
        amap.setdefault(r["lesson"], []).append(
            {"track": r["track"], "file": r["file"], "kind": r["kind"],
             "part": r["part"] or None, "why": r["why"]})

    print("=" * 78)
    from collections import Counter
    c = Counter(x["kind"] for v in amap.values() for x in v)
    print("Tổng hợp:", " · ".join("%s %d" % (k, n) for k, n in c.most_common()))
    if warns:
        print("\n🔴 Lệch số bài — phải kiểm tra tay:")
        for w in warns:
            print("   " + w)
    if unknown:
        print("\n⚠ %d track chưa nhận ra là đoạn gì:" % len(unknown))
        for u in unknown:
            print("   %-18s transcript: %s" % (u, (cache.get(u, "") or "(rỗng)")[:56]))

    if write:
        out = os.path.join(ROOT, "database", "hsk1", "audio_map.json")
        with io.open(out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"level": "HSK1", "source": "MP3 GIAO TRINH CHUAN HSK1 -GT",
                                 "lessons": amap}, ensure_ascii=False, indent=2))
        print("\n✓ Đã ghi database/hsk1/audio_map.json")


if __name__ == "__main__":
    main()
