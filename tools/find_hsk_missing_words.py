# -*- coding: utf-8 -*-
"""Tìm từ giáo trình có dạy nhưng danh sách từ vựng không có.

Bối cảnh: slide 生词 chỉ in PINYIN dạng chữ (hanzi là ảnh), nên có những từ
giáo trình dạy mà extract_hsk_source.py không tra được — bài 13-15 của HSK2
chỉ ra 2-4 từ là vì vậy.

Cách tìm, hoàn toàn dựa trên bằng chứng, KHÔNG đoán:
  1. Lấy các cụm pinyin ở slide mà danh sách từ vựng không có.
  2. Tìm trong CHÍNH slide của bài đó những chuỗi chữ Hán mà pypinyin đọc ra
     đúng cụm pinyin ấy. Slide 生词拓展 có chữ Hán dạng text thật
     ("拿东西--拿铅笔", "左手--右手--手里") nên tìm được.
  3. Nghĩa tiếng Việt CHỈ lấy từ file nguồn "(9 cấp)" trong zip — không tự
     viết. Từ nào không tra được nghĩa thì báo để người dùng tự điền.

Ra: database/hsk_missing_words.json (đề xuất, KHÔNG tự đưa vào dữ liệu chính)

⚠ ĐỪNG NHẬP HÀNG LOẠT. Đã thử và kiểm chứng: phần lớn kết quả KHÔNG phải từ
vựng của bài, mà là:
  - từ ở slide luyện phát âm ("看图片朗读下列双音节词语") — 奶奶, 裙子, 耳朵…
    xuất hiện ở HSK1 bài 2 chỉ để tập đọc, không phải 生词 của bài;
  - nghĩa SAI trong chính bản "(9 cấp)" — 比 "gần đây" (phải là so sánh),
    回 "quanh co" (phải là trở về), 者 ghi nghĩa văn ngôn;
  - âm Hán Việt bị nhầm thành nghĩa — 心 "tâm", 力 "lực", 白 "bạch".
Chỉ nên dùng file này để RÀ TAY: đọc, chọn mục đúng, chép sang
database/hsk_corrections.json. Số thật sự dùng được rất ít (vd HSK2 bài 13:
拿, 铅笔, 宾馆, 往, 一直 — đều là từ mới thật của bài đó).

Chạy:
  python tools/find_hsk_missing_words.py           # cả 3 cấp
  python tools/find_hsk_missing_words.py hsk2
"""
import glob, io, json, os, re, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_hsk_source as EX          # dùng lại cấu hình + hàm chuẩn hoá

OUT = os.path.join(ROOT, "database", "hsk_missing_words.json")
USAGE = ("Cách dùng:\n"
         "  python tools/find_hsk_missing_words.py [hsk1|hsk2|hsk3]\n"
         "    bỏ trống = cả 3 cấp")

# Các bản "(9 cấp)" là kho nghĩa tiếng Việt rộng nhất có trong zip
VN_SOURCES = [
    ("HSK2.zip", "HSK2 (9 cấp)_19_03_2026 15_19_07.xlsx"),
    ("HSK3.zip", "HSK3 (9 cấp)_19_03_2026 15_19_21.xlsx"),
]


def load_vn_pool():
    """Gộp mọi bảng nghĩa tiếng Việt có trong các zip -> {hanzi: (pinyin, nghĩa, hánviệt)}"""
    pool = {}
    for zname, suf in VN_SOURCES:
        zpath = os.path.join(EX.SRC_DIR, zname)
        if not os.path.isfile(zpath):
            continue
        zf = zipfile.ZipFile(zpath)
        try:
            for h, p, m, hv in EX._xlsx_rows(zf, suf):
                h = re.sub(r"\s+", "", h)
                if h and m and h not in pool:
                    pool[h] = (p.strip(), m.strip(), hv.strip())
        except KeyError:
            pass
    return pool


def main():
    want = []
    for a in sys.argv[1:]:
        if re.fullmatch(r"hsk[123]", a.lower()):
            want.append(int(a[-1]))
        else:
            sys.exit("Không hiểu tham số: %r\n\n%s" % (a, USAGE))
    want = sorted(set(want)) or [1, 2, 3]

    try:
        from pypinyin import pinyin, Style
    except ImportError:
        sys.exit("Thiếu thư viện pypinyin.\n  pip install pypinyin")

    def py_tone(s):
        """Pinyin CÓ dấu thanh. Bắt buộc dùng làm khoá chính: bỏ dấu thanh thì
        拿(ná) lẫn với 那(nà), 班(bān) lẫn với 办(bàn), 国(guó) lẫn với 过(guò)."""
        return EX.norm_tone("".join(x[0] for x in pinyin(s, style=Style.TONE)))

    def py_plain(s):
        return EX.norm_plain("".join(x[0] for x in pinyin(s, style=Style.TONE)))

    vn_pool = load_vn_pool()
    print("Kho nghĩa tiếng Việt gộp từ các bản '(9 cấp)': %d từ\n" % len(vn_pool))

    result = {}
    for lv in want:
        cfg = EX.LEVELS[lv]
        zpath = os.path.join(EX.SRC_DIR, cfg["zip"])
        if not os.path.isfile(zpath):
            print("⚠ Bỏ qua HSK%d — không thấy %s" % (lv, cfg["zip"]))
            continue
        zf = zipfile.ZipFile(zpath)

        kind, suffix = cfg["master"]
        master = (EX.read_master_docx(zf, suffix) if kind == "docx"
                  else EX.read_master_xlsx(zf, suffix, cfg["vn"]))
        known_py = set()
        known_h = set()
        for w in master:
            known_h.add(w["h"])
            known_py |= EX.pinyin_keys(w)

        print("=" * 70)
        print("HSK%d" % lv)
        found, need_meaning = [], []
        for n in range(1, cfg["lessons"] + 1):
            try:
                cands, raw, _dlg, _gr, _tp = EX.parse_lesson_pptx(zf, cfg["pptx"](n))
            except KeyError:
                continue

            # 1) cụm pinyin ở slide mà danh sách từ không có
            miss_py = []
            for c in cands:
                c = c.strip()
                if not EX.PINYIN_RE.match(c.lower()):
                    continue
                if not any(ch in EX.CN_TONE_CHARS for ch in c):
                    continue
                if EX.norm_tone(c) in known_py or EX.norm_plain(c) in known_py:
                    continue
                if 2 <= len(c) <= 14:
                    miss_py.append(c)
            miss_py = sorted(set(miss_py))
            if not miss_py:
                continue

            # 2) mọi chuỗi hanzi 1-4 chữ xuất hiện trong slide của CHÍNH bài này
            hanzi_seqs = set()
            for run in re.findall(r"[一-鿿]+", raw):
                for size in (1, 2, 3, 4):
                    for i in range(len(run) - size + 1):
                        hanzi_seqs.add(run[i:i + size])
            by_tone, by_plain = {}, {}
            for hz in hanzi_seqs:
                by_tone.setdefault(py_tone(hz), []).append(hz)
                by_plain.setdefault(py_plain(hz), []).append(hz)

            for c in miss_py:
                # Khớp có dấu thanh trước; chỉ khi không có mới hạ chuẩn xuống
                # bỏ dấu, và khi đó phải đánh dấu là kém chắc chắn.
                exact = True
                cands_hz = [h for h in by_tone.get(EX.norm_tone(c), []) if h not in known_h]
                if not cands_hz:
                    exact = False
                    cands_hz = [h for h in by_plain.get(EX.norm_plain(c), []) if h not in known_h]
                if not cands_hz:
                    continue
                # ưu tiên chữ có mặt trong kho nghĩa -> gần như chắc chắn đúng từ
                with_vn = [h for h in cands_hz if h in vn_pool]
                pick = with_vn[0] if with_vn else None
                rec = {"lesson": n, "pinyin_slide": c,
                       "khớp_dấu_thanh": exact,
                       "hanzi_ứng_viên": sorted(set(cands_hz))}
                if pick:
                    p, m, hv = vn_pool[pick]
                    rec.update({"hanzi": pick, "p": p or c, "m": m, "hv": hv})
                    found.append(rec)
                else:
                    need_meaning.append(rec)

        # bỏ trùng theo hanzi
        seen = set()
        uniq = []
        for r in found:
            if r["hanzi"] in seen:
                continue
            seen.add(r["hanzi"])
            uniq.append(r)

        print("✓ %d từ tra được ĐỦ hanzi + nghĩa từ file nguồn:" % len(uniq))
        for r in uniq:
            amb = (" ⚠ còn ứng viên khác: %s" % " ".join(x for x in r["hanzi_ứng_viên"] if x != r["hanzi"])
                   if len(r["hanzi_ứng_viên"]) > 1 else "")
            if not r.get("khớp_dấu_thanh"):
                amb += " ⚠ CHỈ khớp khi bỏ dấu thanh — kém chắc chắn"
            print("   bài %2d  %-6s %-10s %s%s" % (r["lesson"], r["hanzi"], r["p"], r["m"][:34], amb))

        if need_meaning:
            print("\n⚠ %d cụm tìm được chữ Hán nhưng KHÔNG có nghĩa trong file nguồn"
                  " — cần bạn tự điền:" % len(need_meaning))
            for r in need_meaning[:25]:
                print("   bài %2d  pinyin %-12s ứng viên: %s"
                      % (r["lesson"], r["pinyin_slide"], " ".join(r["hanzi_ứng_viên"][:6])))

        result["HSK%d" % lv] = {"tra_được": uniq, "thiếu_nghĩa": need_meaning}

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "_note": ["ĐỀ XUẤT do tools/find_hsk_missing_words.py sinh ra — CHƯA vào dữ liệu chính.",
                      "⚠ ĐỪNG NHẬP HÀNG LOẠT — đa số không phải từ vựng của bài. Xem docstring của script.",
                      "hanzi lấy từ chính slide của bài (khớp pinyin bằng pypinyin).",
                      "nghĩa lấy từ bản '(9 cấp)' trong zip — KHÔNG tự viết.",
                      "Duyệt xong thì chép sang database/hsk_corrections.json mục 'them'."],
            "levels": result}, ensure_ascii=False, indent=2))
    print("\n✓ Đã ghi đề xuất ra %s" % os.path.relpath(OUT, ROOT))
    print("\n⚠ ĐỪNG NHẬP HÀNG LOẠT. Đã kiểm chứng: đa số kết quả KHÔNG phải từ vựng của")
    print("  bài — mà là từ ở slide luyện phát âm (奶奶, 裙子, 耳朵…), hoặc nghĩa sai sẵn")
    print("  trong file nguồn (比 'gần đây', 回 'quanh co'), hoặc âm Hán Việt bị nhầm")
    print("  thành nghĩa (心 'tâm', 力 'lực'). Hãy đọc rồi chọn tay, chép mục đúng sang")
    print("  database/hsk_corrections.json.")


if __name__ == "__main__":
    main()
