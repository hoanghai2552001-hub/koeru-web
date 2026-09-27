"""Gộp các từ được đối chiếu từ slide 生词 vào database HSK, theo cách idempotent."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "database" / "hsk_supplements.json"


def main():
    supplements = json.loads(SOURCE.read_text(encoding="utf-8"))
    added = skipped = 0
    for level in (1, 2, 3):
        level_key = "HSK%d" % level
        lesson_groups = supplements.get(level_key, {})
        db = ROOT / "database" / ("hsk%d" % level)
        existing = {}
        for path in db.glob("lesson*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            for word in doc.get("vocab", []):
                existing[word.get("h")] = path.name
        for lesson_text, words in lesson_groups.items():
            path = db / ("lesson%02d.json" % int(lesson_text))
            doc = json.loads(path.read_text(encoding="utf-8"))
            changed = False
            for word in words:
                hanzi = word["h"]
                if hanzi in existing:
                    print("Bỏ qua %s: đã có trong %s" % (hanzi, existing[hanzi]))
                    skipped += 1
                    continue
                entry = dict(word)
                entry["_src"] = "pptx-supplement-reviewed"
                doc.setdefault("vocab", []).append(entry)
                existing[hanzi] = path.name
                changed = True
                added += 1
                print("Thêm HSK%d bài %s: %s" % (level, lesson_text, hanzi))
            if changed:
                path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Hoàn tất: thêm %d · đã có %d" % (added, skipped))


if __name__ == "__main__":
    main()
