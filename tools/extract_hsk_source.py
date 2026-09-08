# -*- coding: utf-8 -*-
"""Bóc từ vựng / hội thoại / ngữ pháp HSK1 theo từng bài từ giáo trình.

Nguồn (đọc thẳng trong zip, KHÔNG giải nén ra đĩa):
  Tiếng Trung/HSK1.zip
    - "150 Từ vựng HSK 1.docx"        -> bảng gốc: hanzi | pinyin | từ loại | nghĩa Việt
    - "HSK标准教程1-第N课.pptx" (15 bài) -> từ nào thuộc bài nào + 课文 (hội thoại) + 语言点 (ngữ pháp)
  js/pinyin-data.js (HSK1_DATA)        -> hanviet + câu ví dụ

Ra:  database/hsk1/lessonNN.json  (status = REVIEW_REQUIRED)

Chạy:
  python tools/extract_hsk_source.py --dry-run   # chỉ in báo cáo, không ghi file
  python tools/extract_hsk_source.py             # ghi database/hsk1/
"""
import io, json, os, re, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_PATH = os.path.join(ROOT, "Tiếng Trung", "HSK1.zip")
PINYIN_JS = os.path.join(ROOT, "js", "pinyin-data.js")
OUT_DIR = os.path.join(ROOT, "database", "hsk1")
TOTAL_LESSONS = 15

DOCX_MEMBER = "HSK1/Từ vựng HSK 1/150 Từ vựng HSK 1.docx"
PPTX_PREFIX = "HSK1/Powerpoint Giáo trình HSK 1 chuẩn/HSK标准教程1-第"

# Giáo trình dùng ɡ (U+0261) thay g thường, và đôi chỗ rơi mất dấu thanh.
TONE_MAP = {
    "ā": "a", "á": "a", "ǎ": "a", "à": "a",
    "ē": "e", "é": "e", "ě": "e", "è": "e",
    "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
    "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
    "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
    "ǖ": "v", "ǘ": "v", "ǚ": "v", "ǜ": "v", "ü": "v",
    "ń": "n", "ň": "n", "ǹ": "n", "ɡ": "g",
}

POS_LABELS = [
    "T\u1eeb ch\u1ec9 th\u1eddi gian", "Ch\u1ec9 s\u1ed1 l\u01b0\u1ee3ng", "T\u00ean ri\u00eang", "L\u01b0\u1ee3ng t\u1eeb", "Tr\u1ea1ng ng\u1eef",
    "\u0110\u1ed9ng t\u1eeb", "Danh t\u1eeb", "T\u00ednh t\u1eeb", "\u0110\u1ea1i t\u1eeb", "S\u1ed1 t\u1eeb", "Ph\u00f3 t\u1eeb", "Gi\u1edbi t\u1eeb",
    "Li\u00ean t\u1eeb", "Tr\u1ee3 t\u1eeb", "Th\u00e1n t\u1eeb",
]

HAN_RE = re.compile(r"[\u4e00-\u9fff]")

# Gi\u00e1o tr\u00ecnh g\u00f5 l\u1eabn d\u1ea5u c\u00e2u ASCII v\u1edbi d\u1ea5u full-width. Ngo\u00e0i chuy\u1ec7n kh\u00f4ng nh\u1ea5t
# qu\u00e1n, "?" v\u00e0 ":" c\u00f2n KH\u00d4NG h\u1ee3p l\u1ec7 trong t\u00ean file Windows \u2014 m\u00e0 audio \u0111\u1eb7t t\u00ean
# theo \u0111\u00fang c\u00e2u (audio/hsk/<c\u00e2u>.mp3), n\u00ean ph\u1ea3i chu\u1ea9n ho\u00e1 ngay t\u1eeb kh\u00e2u b\u00f3c.
ASCII_PUNCT = {"?": "\uff1f", "!": "\uff01", ":": "\uff1a", ";": "\uff1b", ",": "\uff0c"}


def norm_punct(s):
    for a, b in ASCII_PUNCT.items():
        s = s.replace(a, b)
    return s
PINYIN_RE = re.compile(r"^[a-z\u00e0-\u01ff\u0251\u0261\s]{2,24}$")


def norm_tone(s):
    """Bỏ khoảng trắng + dấu câu, thường hoá, giữ dấu thanh."""
    s = (s or "").strip().lower().replace("\u0261", "g")
    return re.sub(r"[\s\u3000\u00b7,\uff0c.\u3002!\uff01?\uff1f:\uff1a;\uff1b\"'()\uff08\uff09]", "", s)


def norm_plain(s):
    """Như trên nhưng bỏ luôn dấu thanh — dùng khi giáo trình gõ thiếu dấu."""
    return "".join(TONE_MAP.get(c, c) for c in norm_tone(s))


# ───────────────────────── 1. Bảng 150 từ từ .docx ─────────────────────────

def read_master(zf):
    raw = zipfile.ZipFile(io.BytesIO(zf.read(DOCX_MEMBER))).read("word/document.xml").decode("utf-8")
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", raw, re.S)
    out = []
    for tr in rows:
        cells = []
        for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S):
            # Mỗi <w:p> trong ô là MỘT dòng (một nét nghĩa / một từ loại).
            # Phải giữ ranh giới dòng, nếu gộp hết bằng dấu cách sẽ dính chữ:
            # "Động từ" -> "Động, từ",  "Là / Đúng, chính xác" -> "Là Đúng, chính xác".
            lines = []
            for wp in re.findall(r"<w:p[ >].*?</w:p>", tc, re.S) or [tc]:
                txt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", wp))
                txt = re.sub(r"\s+", " ", txt).strip()
                if txt:
                    lines.append(txt)
            cells.append(lines)
        if len(cells) < 4:
            continue  # dòng tiêu đề, hoặc dòng chữ cái A/B/C
        hanzi = " ".join(cells[0]).strip()
        pinyin = " ".join(cells[1]).strip()
        if not hanzi or not pinyin or not HAN_RE.search(hanzi):
            continue
        if pinyin.lower() in ("phiên âm", "pinyin"):
            continue
        pos = ", ".join(cells[2])
        mean = "; ".join(cells[3])      # mỗi dòng trong ô = một nét nghĩa
        # Vài dòng trong docx gõ lẫn nghĩa vào ô "Từ loại" và bỏ trống ô nghĩa
        # (vd 明天 -> "Từ chỉ thời gian Ngày mai"). Tách lại theo nhãn từ loại.
        if not mean and pos:
            for lab in POS_LABELS:
                if pos.startswith(lab) and len(pos) > len(lab):
                    pos, mean = lab, pos[len(lab):].strip(" ,")
                    break
        # "哪(哪儿)" -> giữ dạng gốc để hiện, thêm dạng rút gọn để tra
        out.append({
            "h": re.sub(r"\s+", "", hanzi),
            "p": re.sub(r"\s+", " ", pinyin).strip(),
            "pos": pos,
            "m": mean,
        })
    return out


def variants(w):
    """Các dạng hanzi có thể xuất hiện trong slide: '哪(哪儿)' -> ['哪哪儿','哪','哪儿']."""
    h = w["h"]
    out = {h}
    m = re.match(r"^([\u4e00-\u9fff]+)[(\uff08]([\u4e00-\u9fff]+)[)\uff09]$", h)
    if m:
        out.update([m.group(1), m.group(2)])
    return [x for x in out if x]


def pinyin_keys(w):
    """Pinyin có thể có nhiều dạng: 'zhè (zhèr) Zhèi ...' -> tách từng cụm."""
    parts = re.split(r"[(\uff08)\uff09/]|\s{2,}", w["p"])
    keys = set()
    for p in parts:
        p = p.strip()
        if p and PINYIN_RE.match(p.lower()):
            keys.add(norm_tone(p))
            keys.add(norm_plain(p))
    keys.add(norm_tone(w["p"]))
    keys.add(norm_plain(w["p"]))
    return {k for k in keys if len(k) >= 2}


# ──────────────────── 2. hanviet + ví dụ từ js/pinyin-data.js ────────────────────

def read_hsk1_js():
    src = io.open(PINYIN_JS, encoding="utf-8").read()
    extra = {}
    for m in re.finditer(r"\{hanzi:\s*\"([^\"]+)\"(.*?)\}", src, re.S):
        hanzi, body = m.group(1), m.group(2)

        def field(name):
            f = re.search(name + r':\s*"([^"]*)"', body)
            return f.group(1) if f else ""

        extra[hanzi] = {
            "hv": field("hanviet"),
            "ex_zh": field("example_zh"),
            "ex_p": field("example_pinyin"),
            "ex_vi": field("example_vi"),
        }
    return extra


# ───────────────────────── 3. Bóc từng bài từ .pptx ─────────────────────────

def slide_texts(slide):
    return [sh.text_frame.text for sh in slide.shapes
            if sh.has_text_frame and sh.text_frame.text.strip()]


def parse_lesson_pptx(zf, n):
    """Trả về (pinyin_candidates, raw_hanzi_text, dialogue, grammar) của bài n.

    Bố cục giáo trình: slide tiêu đề "生词 / New Words" nằm RIÊNG, pinyin của từ mới
    ở slide kế tiếp, còn hanzi của từ mới là ẢNH nên không bóc được. Vì vậy gom pinyin
    từ MỌI slide rồi lấy chính bảng 150 từ làm bộ lọc, thay vì lọc theo tiêu đề slide.
    """
    from pptx import Presentation

    prs = Presentation(io.BytesIO(zf.read("%s%d课.pptx" % (PPTX_PREFIX, n))))
    cands, raw, dialogue, grammar, topics = [], [], [], [], []

    for slide in prs.slides:
        texts = slide_texts(slide)
        blob = "\n".join(texts)
        raw.append(blob)

        # Slide ôn tập nhắc lại từ của bài TRƯỚC — không tính là từ mới của bài này
        if "复习" not in blob and "Review" not in blob:
            for t in texts:
                for line in t.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if HAN_RE.search(line):
                        # Dòng lẫn hanzi + pinyin (vd "火车站 huǒ chē zhàn") — gỡ hanzi ra
                        line = HAN_RE.sub(" ", line).strip()
                        if not line:
                            continue
                    cands.append(line)

        # 课文 N：<tiêu đề> → hội thoại (mỗi shape = 1 lượt thoại: pinyin / hanzi / Việt)
        mt = re.search(r"课文\s*(\d+)\s*[：:]\s*(\S+)", blob)
        if mt:
            topics.append({"part": int(mt.group(1)), "topic": mt.group(2)})
            for t in texts:
                lines = [l.strip() for l in t.split("\n") if l.strip()]
                if len(lines) >= 3 and HAN_RE.search(lines[1]) and not HAN_RE.search(lines[0]):
                    dialogue.append({
                        "part": int(mt.group(1)),
                        "topic": mt.group(2),
                        # Giáo trình gõ ɡ (U+0261) thay g thường — đổi lại cho khớp font
                        "p": re.sub(r"\s+", " ", lines[0].replace("ɡ", "g")).strip(),
                        "zh": norm_punct(re.sub(r"\s+", "", lines[1])),
                        "vi": lines[2],
                    })

        # 语言点 N：<mẫu câu>
        mg = re.search(r"语言点\s*(\d+)\s*[：:]\s*(.+)", blob)
        if mg:
            vi = ""
            for t in texts:
                m2 = re.search(r"Điểm ngôn ngữ\s*\d+\s*[：:]\s*(.+)", t)
                if m2:
                    vi = m2.group(1).strip()
                    break
            grammar.append({"zh": mg.group(2).strip(), "vi": vi})

    return cands, re.sub(r"\s+", "", "".join(raw)), dialogue, grammar, topics


# ───────────────────────────── 4. Ghép & xuất ─────────────────────────────

def main():
    dry = "--dry-run" in sys.argv

    if not os.path.isfile(ZIP_PATH):
        sys.exit("Không thấy %s" % ZIP_PATH)
    try:
        import pptx  # noqa: F401
    except ImportError:
        sys.exit("Thiếu thư viện python-pptx.\n  pip install python-pptx")

    zf = zipfile.ZipFile(ZIP_PATH)
    master = read_master(zf)
    extra = read_hsk1_js()
    print("Bảng gốc (docx): %d từ · js/pinyin-data.js: %d từ có Hán Việt/ví dụ\n"
          % (len(master), len(extra)))

    by_pinyin = {}
    for w in master:
        for k in pinyin_keys(w):
            by_pinyin.setdefault(k, w)

    decks = {}
    for n in range(1, TOTAL_LESSONS + 1):
        decks[n] = parse_lesson_pptx(zf, n)

    assigned = {}                                      # hanzi -> số bài
    lessons = {n: {"vocab": []} for n in decks}
    unmatched = {n: [] for n in decks}

    def take(n, w, how):
        if w["h"] in assigned:
            return
        assigned[w["h"]] = n
        e = extra.get(w["h"], {})
        lessons[n]["vocab"].append({
            "h": w["h"], "p": w["p"], "pos": w["pos"], "m": w["m"],
            "hv": e.get("hv", ""), "ex_zh": e.get("ex_zh", ""),
            "ex_p": e.get("ex_p", ""), "ex_vi": e.get("ex_vi", ""),
            "src": how,
        })

    # Lượt 1 — khớp theo pinyin (đáng tin nhất: chính là danh sách 生词 của bài)
    for n in range(1, TOTAL_LESSONS + 1):
        cands = decks[n][0]
        for c in cands:
            w = by_pinyin.get(norm_tone(c)) or by_pinyin.get(norm_plain(c))
            if w:
                take(n, w, "pinyin")
            elif PINYIN_RE.match(c.lower()) and " " in c:
                unmatched[n].append(c)

    # Lượt 2 — vét: từ chưa gán mà hanzi xuất hiện NGUYÊN CỤM trong slide của bài
    for n in range(1, TOTAL_LESSONS + 1):
        text = decks[n][1]
        for w in master:
            if w["h"] in assigned:
                continue
            if any(len(v) >= 1 and v in text for v in variants(w)):
                take(n, w, "hanzi")

    for n in decks:
        lessons[n]["dialogue"] = decks[n][2]
        lessons[n]["grammar"] = decks[n][3]
        lessons[n]["topics"] = decks[n][4]

    # ── Báo cáo ──
    print("Bài | từ vựng (pinyin/hanzi) | hội thoại | ngữ pháp")
    print("----|------------------------|-----------|---------")
    for n in range(1, TOTAL_LESSONS + 1):
        L = lessons[n]
        a = sum(1 for v in L["vocab"] if v["src"] == "pinyin")
        print(" %2d |  %3d   ( %3d / %3d )    |    %3d    |   %3d"
              % (n, len(L["vocab"]), a, len(L["vocab"]) - a, len(L["dialogue"]), len(L["grammar"])))

    total = sum(len(lessons[n]["vocab"]) for n in lessons)
    print("\nĐã gán: %d / %d từ" % (total, len(master)))

    left = [w for w in master if w["h"] not in assigned]
    if left:
        print("\n⚠ %d từ CHƯA gán được vào bài nào — cần điền tay:" % len(left))
        for w in left:
            print("   %-10s %-14s %s" % (w["h"], w["p"], w["m"]))

    no_hv = sorted(h for h in assigned if not extra.get(h, {}).get("hv"))
    if no_hv:
        print("\n⚠ %d từ thiếu Hán Việt + ví dụ (js/pinyin-data.js không có) — cần bổ sung:"
              % len(no_hv))
        print("   " + " ".join(no_hv))

    allmiss = sum(len(unmatched[n]) for n in unmatched)
    if allmiss:
        print("\nℹ %d cụm pinyin ở slide không tra được trong bảng 150 từ" % allmiss)
        print("  (thường là từ mở rộng 'New Word Expansion' ngoài phạm vi HSK1 — xem qua rồi bỏ):")
        for n in range(1, TOTAL_LESSONS + 1):
            if unmatched[n]:
                print("   bài %2d: %s" % (n, " · ".join(unmatched[n][:14])))

    if dry:
        print("\n--dry-run: KHÔNG ghi file.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    for n in range(1, TOTAL_LESSONS + 1):
        L = lessons[n]
        for v in L["vocab"]:
            # Giữ lại nguồn gán để giáo viên soát có trọng tâm:
            #   "pinyin" = lấy từ danh sách 生词 của đúng bài (đáng tin)
            #   "hanzi"  = suy ra vì hanzi xuất hiện trong slide (CẦN KIỂM TRA lại số bài)
            v["_src"] = v.pop("src", "")
        doc = {
            "lesson": n,
            "source": "HSK标准教程1 第%d课 (PPTX) + 150 Từ vựng HSK 1.docx" % n,
            "status": "REVIEW_REQUIRED",
            "title": L["topics"][0]["topic"] if L["topics"] else "",
            "topics": L["topics"],
            "vocab": L["vocab"],
            "grammar": L["grammar"],
            "dialogue": L["dialogue"],
        }
        with io.open(os.path.join(OUT_DIR, "lesson%02d.json" % n), "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=2))
    print("\n✓ Đã ghi %d file vào database/hsk1/" % TOTAL_LESSONS)
    print("  status = REVIEW_REQUIRED — cần giáo viên duyệt trước khi lên web.")


if __name__ == "__main__":
    main()
