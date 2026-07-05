# -*- coding: utf-8 -*-
"""Gộp database/n5/lessonXX.json + N5_grammar_summary.md → minna-n5-data.js
Chạy: python tools/gen_minna_n5_data.py"""
import json, io, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAMMAR_MD = os.path.join(ROOT, "N5_grammar_summary.md")
DB_DIR = os.path.join(ROOT, "database", "n5")
OUT = os.path.join(ROOT, "minna-n5-data.js")
TOTAL_LESSONS = 25

# 1) Ngữ pháp: parse "## Bài N" + các dòng "- pattern"
grammar = {}
cur = None
with io.open(GRAMMAR_MD, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"##\s*Bài\s*(\d+)", line)
        if m:
            cur = int(m.group(1))
            grammar[cur] = []
        elif cur and line.strip().startswith("- "):
            grammar[cur].append(line.strip()[2:].strip())

# 2) Từ vựng: đọc các lesson JSON đã có
lessons = {}
for p in sorted(glob.glob(os.path.join(DB_DIR, "lesson*.json"))):
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    lessons[d["lesson"]] = d

# 3) Gộp đủ 25 bài
out = []
for n in range(1, TOTAL_LESSONS + 1):
    d = lessons.get(n, {})
    out.append({
        "lesson": n,
        "status": d.get("status", "NO_DATA"),
        "vocab": d.get("vocab", []),
        "expressions": d.get("expressions", []),
        "grammar": grammar.get(n, []),
    })

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("// AUTO-GENERATED từ database/n5/*.json + N5_grammar_summary.md — KHÔNG sửa tay.\n")
    f.write("// Chạy lại: python tools/gen_minna_n5_data.py\n")
    f.write("window.MINNA_N5 = ")
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

done = sum(1 for l in out if l["vocab"])
print("OK ->", OUT)
print("Bài có từ vựng: %d/%d | Bài có ngữ pháp: %d/%d" %
      (done, TOTAL_LESSONS, sum(1 for l in out if l["grammar"]), TOTAL_LESSONS))
