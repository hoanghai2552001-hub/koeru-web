# -*- coding: utf-8 -*-
"""QA dữ liệu nội dung HSK 1–3 trước khi sinh các file hsk<N>-data.js."""
import glob, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TONE = re.compile(r"[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]")

def examples_for(level_dir):
    path = os.path.join(level_dir, "curated_examples.json")
    return json.load(io.open(path, encoding="utf-8")) if os.path.isfile(path) else {}

def main():
    errors, warnings = [], []
    totals = {"lessons": 0, "vocab": 0, "examples": 0, "dialogue": 0}
    corrections = json.load(io.open(os.path.join(ROOT, "database", "hsk_corrections.json"), encoding="utf-8"))
    for lv in (1, 2, 3):
        folder = os.path.join(ROOT, "database", "hsk%d" % lv)
        curated = examples_for(folder)
        dialogue_path = os.path.join(folder, "curated_dialogue.json")
        dialogues = json.load(io.open(dialogue_path, encoding="utf-8")) if os.path.isfile(dialogue_path) else {}
        for path in sorted(glob.glob(os.path.join(folder, "lesson*.json"))):
            d = json.load(io.open(path, encoding="utf-8"))
            label = "HSK%d bài %d" % (lv, d.get("lesson", -1))
            totals["lessons"] += 1
            for v in d.get("vocab", []):
                v = dict(v)
                v.update({k: value for k, value in corrections.get("HSK%d" % lv, {}).get(v.get("h"), {}).items() if k != "why"})
                totals["vocab"] += 1
                h, p, m = v.get("h", ""), v.get("p", ""), v.get("m", "")
                if not h or not p or not m:
                    errors.append("%s: từ thiếu h/p/m: %r" % (label, h))
                if not TONE.search(p) and p.lower() not in {"ma", "ne", "de", "le", "ba", "a", "zhe", "guo"}:
                    warnings.append("%s: pinyin chưa có dấu thanh: %s (%s)" % (label, h, p))
                ex = curated.get(h, v)
                if ex and ex.get("ex_zh") and ex.get("ex_p") and ex.get("ex_vi"):
                    totals["examples"] += 1
                    main = h.split('(')[0].split('（')[0]
                    if main not in ex['ex_zh']:
                        errors.append("%s: ví dụ không chứa từ %s" % (label, h))
                else:
                    warnings.append("%s: thiếu ví dụ: %s" % (label, h))
            for line in dialogues.get(str(d.get("lesson")), {}).get("lines", d.get("dialogue", [])):
                totals["dialogue"] += 1
                if not line.get("zh"):
                    errors.append("%s: lời thoại thiếu chữ Hán" % label)
                elif not line.get("p") or not line.get("vi"):
                    missing = "/".join(k for k in ("pinyin", "nghĩa Việt") if not line.get("p" if k == "pinyin" else "vi"))
                    warnings.append("%s: lời thoại thiếu %s: %s" % (label, missing, line["zh"]))
    print("HSK: %(lessons)d bài · %(vocab)d từ · %(examples)d ví dụ · %(dialogue)d lời thoại" % totals)
    for item in errors: print("ERROR", item)
    for item in warnings: print("WARN ", item)
    print("Kết quả: %d lỗi · %d cảnh báo" % (len(errors), len(warnings)))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
