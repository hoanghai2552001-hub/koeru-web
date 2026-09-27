"""So sánh database HSK1-3 với PDF từ vựng HSK 2.0 chính thức.

Nguồn mặc định: tmp/pdfs/hsk1-4-official.pdf
URL: https://www.chinesetest.cn/userfiles/file/cihui.pdf
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize(word):
    return re.sub(r"\s+", "", word).replace("（", "(").replace("）", ")")


def extract_sections(pdf_path):
    import pdfplumber

    sections = {1: [], 2: [], 3: []}
    active = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            heading = re.search(r"新\s*HSK[（(]([一二三])[级級]?[）)]词汇[（(](\d+)[）)]", text)
            if heading:
                active = {"一": 1, "二": 2, "三": 3}[heading.group(1)]
            if active not in sections:
                continue
            for line in text.splitlines():
                match = re.match(r"^\s*(\d+)[．.]\s*(.+?)\s*$", line)
                if match:
                    word = re.sub(r"\s*-\s*\d+\s*-\s*$", "", match.group(2)).strip()
                    sections[active].append((int(match.group(1)), normalize(word)))
    for level, rows in sections.items():
        expected = {1: 150, 2: 300, 3: 600}[level]
        by_number = {number: word for number, word in rows if number <= expected}
        if len(by_number) != expected or set(by_number) != set(range(1, expected + 1)):
            raise ValueError("HSK%d: bóc được %d/%d mục đánh số" % (level, len(by_number), expected))
        sections[level] = [by_number[i] for i in range(1, expected + 1)]
    return sections


def database_words(level):
    words = []
    for path in sorted((ROOT / "database" / ("hsk%d" % level)).glob("lesson*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        words.extend(normalize(row["h"]) for row in doc.get("vocab", []))
    return words


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path,
                        default=ROOT / "tmp" / "pdfs" / "hsk1-4-official.pdf")
    args = parser.parse_args()
    official = extract_sections(args.pdf)
    previous_count = 0
    report = {}
    has_missing = False
    for level in (1, 2, 3):
        cumulative = set(official[level])
        # PDF là danh sách tích lũy. Lấy đúng đoạn mới của từng cấp thay vì trừ
        # tập hợp, vì 长 và 还 xuất hiện lại ở HSK3 với cách đọc/nghĩa khác.
        expected_new = set(official[level][previous_count:])
        actual = set(database_words(level))
        report["HSK%d" % level] = {
            "official_cumulative_items": len(official[level]),
            "official_cumulative_unique": len(cumulative),
            "official_new": len(expected_new),
            "database_unique": len(actual),
            "missing_official": sorted(expected_new - actual),
            "supplemental_or_misleveled": sorted(actual - expected_new),
        }
        has_missing = has_missing or bool(expected_new - actual)
        previous_count = len(official[level])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if has_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
