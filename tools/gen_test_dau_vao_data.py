# -*- coding: utf-8 -*-
"""Sinh test-dau-vao-data.js từ SOURCE_OF_TRUTH_exam_data.json (đã QA, frozen).
Chạy: python tools/gen_test_dau_vao_data.py"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "KOERU_5_De_Dau_Vao_N4_N5_Level", "Test đầu vào N3",
                   "KOERU_5_De_Dau_Vao_N3_Nen_Tang_N4_v4_ACADEMIC_QA_FINAL",
                   "SOURCE_OF_TRUTH_exam_data.json")
OUT = os.path.join(ROOT, "test-dau-vao-data.js")

with io.open(SRC, encoding="utf-8") as f:
    data = json.load(f)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("// AUTO-GENERATED từ SOURCE_OF_TRUTH_exam_data.json — KHÔNG sửa tay.\n")
    f.write("// Chạy lại: python tools/gen_test_dau_vao_data.py\n")
    f.write("window.EXAM_N3 = ")
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

print("OK ->", OUT, os.path.getsize(OUT), "bytes,", len(data["sets"]), "sets")
