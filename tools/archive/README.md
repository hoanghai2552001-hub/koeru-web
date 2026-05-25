# tools/archive

Scripts one-off đã hoàn thành nhiệm vụ — giữ lại để tham khảo lịch sử, không chạy trong pipeline.

| Script | Việc đã làm |
|--------|------------|
| fix_all_english.py | Dịch 1341 nghĩa English → Vietnamese (tháng 5/2026) |
| fix_remaining39.py | Fix 39 lỗi còn lại sau fix_all_english |
| fix_taku.py | Fix reading sai của 宅 (帰宅→おたく) |
| fix_n5n4.py | Patch đợt đầu N5/N4 readings sai |
| fix_n2.py / fix_n1.py | Patch N2, N1 batch đầu |
| fix_words*.py | Fix words[] entries hàng loạt |
| fix_duplicates*.py | Xóa duplicate word entries |
| fix_kanji_data.py | Fix tổng hợp batch đầu tiên |
| fix_english_meanings.py | Phiên bản cũ (dictionary nhỏ hơn) |
| patch_*.py | Patch vi meanings từng đợt |
| apply_*_fixes.py | Apply các diff N3/N4/ref |
| compare_*.py | So sánh với reference data |
| batch_fix_kanji.py | Batch fix tool tổng hợp |

Để chạy pipeline data chính thức → dùng `tools/build.sh` hoặc `make all`.
