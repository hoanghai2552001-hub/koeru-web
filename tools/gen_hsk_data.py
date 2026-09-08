# -*- coding: utf-8 -*-
"""Gộp database/hsk<N>/lessonXX.json → hsk<N>-data.js

Chạy: python tools/gen_hsk_data.py [hsk1|hsk2|hsk3]
Nguồn do tools/extract_hsk_source.py sinh ra từ giáo trình HSK.
"""
import glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSON_COUNT = {1: 15, 2: 15, 3: 20}
VAR_NAME = {1: "HSK1_LESSONS", 2: "HSK2_LESSONS", 3: "HSK3_LESSONS"}

USAGE = ("Cách dùng:\n"
         "  python tools/gen_hsk_data.py [hsk1|hsk2|hsk3]\n"
         "    bỏ trống = làm cả 3")


def build(lv):
    db_dir = os.path.join(ROOT, "database", "hsk%d" % lv)
    out = os.path.join(ROOT, "hsk%d-data.js" % lv)
    total_lessons = LESSON_COUNT[lv]

    if not os.path.isdir(db_dir):
        print("⚠ Bỏ qua HSK%d — chưa có %s (chạy extract_hsk_source.py trước)" % (lv, db_dir))
        return

    lessons = {}
    for p in sorted(glob.glob(os.path.join(db_dir, "lesson*.json"))):
        d = json.load(io.open(p, encoding="utf-8"))
        lessons[d["lesson"]] = d

    data = []
    for n in range(1, total_lessons + 1):
        d = lessons.get(n, {})
        vocab = []
        for v in d.get("vocab", []):
            v = dict(v)
            v.pop("_src", None)      # cờ nội bộ để soát, không cần lên web
            vocab.append(v)
        data.append({
            "lesson": n,
            "status": d.get("status", "NO_DATA"),
            "title": d.get("title", ""),
            "topics": d.get("topics", []),
            "vocab": vocab,
            "grammar": d.get("grammar", []),
            "dialogue": d.get("dialogue", []),
        })

    with io.open(out, "w", encoding="utf-8") as f:
        f.write("// AUTO-GENERATED từ database/hsk%d/*.json — KHÔNG sửa tay.\n" % lv)
        f.write("// Chạy lại: python tools/gen_hsk_data.py hsk%d\n" % lv)
        f.write("window.%s = " % VAR_NAME[lv])
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    nv = sum(len(l["vocab"]) for l in data)
    nd = sum(len(l["dialogue"]) for l in data)
    size = os.path.getsize(out) / 1024
    print("HSK%d → hsk%d-data.js  (%.0f KB)" % (lv, lv, size))
    print("   %d/%d bài có từ vựng · %d từ · %d lượt hội thoại · %d bài có mẫu câu"
          % (sum(1 for l in data if l["vocab"]), total_lessons, nv, nd,
             sum(1 for l in data if l["grammar"])))
    pending = [l["lesson"] for l in data if l["status"] != "OK"]
    if pending:
        print("   ⚠ chưa duyệt (status != OK): bài " + ", ".join(str(x) for x in pending))


def main():
    want = []
    for arg in sys.argv[1:]:
        if re.fullmatch(r"hsk[123]", arg.lower()):
            want.append(int(arg[-1]))
        else:
            sys.exit("Không hiểu tham số: %r\n\n%s" % (arg, USAGE))
    for lv in (want or [1, 2, 3]):
        build(lv)


if __name__ == "__main__":
    main()
