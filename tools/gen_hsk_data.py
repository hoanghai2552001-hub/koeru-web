# -*- coding: utf-8 -*-
"""Gộp database/hsk1/lessonXX.json → hsk1-data.js

Chạy: python tools/gen_hsk_data.py
Nguồn dữ liệu do tools/extract_hsk_source.py sinh ra từ giáo trình HSK.
"""
import glob, io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, "database", "hsk1")
OUT = os.path.join(ROOT, "hsk1-data.js")
TOTAL_LESSONS = 15

lessons = {}
for p in sorted(glob.glob(os.path.join(DB_DIR, "lesson*.json"))):
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    lessons[d["lesson"]] = d

out = []
for n in range(1, TOTAL_LESSONS + 1):
    d = lessons.get(n, {})
    vocab = []
    for v in d.get("vocab", []):
        v = dict(v)
        v.pop("_src", None)      # cờ nội bộ để soát, không cần lên web
        vocab.append(v)
    out.append({
        "lesson": n,
        "status": d.get("status", "NO_DATA"),
        "title": d.get("title", ""),
        "topics": d.get("topics", []),
        "vocab": vocab,
        "grammar": d.get("grammar", []),
        "dialogue": d.get("dialogue", []),
    })

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("// AUTO-GENERATED từ database/hsk1/*.json — KHÔNG sửa tay.\n")
    f.write("// Chạy lại: python tools/gen_hsk_data.py\n")
    f.write("window.HSK1_LESSONS = ")
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

nv = sum(len(l["vocab"]) for l in out)
print("OK ->", OUT)
print("Bài có từ vựng: %d/%d | tổng %d từ | bài có hội thoại: %d | bài có ngữ pháp: %d"
      % (sum(1 for l in out if l["vocab"]), TOTAL_LESSONS, nv,
         sum(1 for l in out if l["dialogue"]), sum(1 for l in out if l["grammar"])))

pending = [l["lesson"] for l in out if l["status"] != "OK"]
if pending:
    print("⚠ Bài chưa được duyệt (status != OK): " + ", ".join(str(x) for x in pending))
