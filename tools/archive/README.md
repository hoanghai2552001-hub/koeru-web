# tools/archive — Legacy Scripts

Các script này đã được dùng trong quá trình xây dựng data ban đầu.
Không dùng trong workflow hiện tại — giữ lại để tham khảo nếu cần.

## Lý do archive

| File | Lý do |
|------|-------|
| `fix_english_meanings.py` | One-off: fix nghĩa tiếng Anh batch đầu |
| `fix_on_readings.py` | One-off: sửa on-reading sai |
| `fix_14_words.py` | One-off: fix 14 từ cụ thể |
| `fix_words_en.py` | One-off: fix words[].m còn tiếng Anh |
| `fix_all_en_meanings.py` | One-off: batch fix English meanings |
| `fix_words_meanings.py` | One-off: fix meanings words |
| `fill_kanji.py` | One-off: fill trường kanji bị thiếu |
| `fill_vocab_missing.py` | One-off: fill từ vựng bị missing |
| `fill_radical_parts.py` | One-off: fill radical/parts fields |
| `patch_vi_meanings.py` | One-off: patch nghĩa Việt hàng loạt |
| `patch_n3_excel.py` | One-off: patch N3 trong Excel |
| `vi_n3_translations.py` | One-off: dịch N3 sang Việt |
| `vi_n4_extra.py` | One-off: dịch N4 extra |
| `merge_translate.py` | One-off: merge bản dịch |
| `export_translate.py` | One-off: export để dịch |
| `enrich_words_from_excel.py` | One-off: enrich từ Excel |
| `clean_schema.py` | One-off: dọn schema cũ |
| `build_unified_db.py` | Migration: thiết kế lại schema (đã xong) |
| `import_excel.py` | Superseded bởi `sync_kanji_excel.py` |
| `gen_final_excel.py` | Superseded bởi `export_excel.py` |
| `build_kanji_data.py` | Superseded: data nay từ Excel, không từ API |
| `build_compounds.py` | Superseded: compounds đã có trong Excel |
| `export_to_csv.py` | Ít dùng: dùng `export_excel.py` thay thế |

## Nếu cần khôi phục

```bash
# Move file trở lại tools/
mv tools/archive/<file>.py tools/<file>.py
```
