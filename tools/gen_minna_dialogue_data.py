# -*- coding: utf-8 -*-
"""Gộp database/dialogue/n4|n5/lessonXX.json → minna-dialogue-data.js
Chạy: python tools/gen_minna_dialogue_data.py"""
import json, io, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIRS = [
    os.path.join(ROOT, "database", "dialogue", "n5"),
    os.path.join(ROOT, "database", "dialogue", "n4"),
]
OUT = os.path.join(ROOT, "minna-dialogue-data.js")

out = {}
for db_dir in DB_DIRS:
    for p in sorted(glob.glob(os.path.join(db_dir, "lesson*.json"))):
        with io.open(p, encoding="utf-8") as f:
            d = json.load(f)
        out[str(d["lesson"])] = {
            "status": d.get("status", "REVIEW_REQUIRED"),
            "title": d.get("title", ""),
            "characters": d.get("characters", []),
            "lines": d.get("lines", []),
        }

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("// AUTO-GENERATED từ database/dialogue/n4|n5/*.json — KHÔNG sửa tay.\n")
    f.write("// Chạy lại: python tools/gen_minna_dialogue_data.py\n")
    f.write("window.MINNA_DIALOGUE = ")
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

print("OK ->", OUT)
print("Số bài có hội thoại:", len(out), "-", sorted(out.keys(), key=int))
