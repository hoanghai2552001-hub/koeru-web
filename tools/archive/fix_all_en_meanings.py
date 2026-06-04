"""
fix_all_en_meanings.py — Fix toàn bộ nghĩa tiếng Anh/hỗn hợp còn sót trong kanji-data
Sửa cả meaning field và words[].m field
"""
import re
from pathlib import Path

JS = Path(__file__).parent.parent / "js"

# ── 1. MEANING field fixes ─────────────────────────────────────────────────
MEANING_FIXES = {
    # Hoàn toàn sai — copy-paste lỗi
    "bây giờ, nói dối": "nhận biết; công nhận",          # 認
    "bảy, ngồi":        "đối; đối diện",                  # 対
    "bảy, hòa bình":    "bằng phẳng; hòa bình",           # 平
    "đàn ông, bây giờ": "tướng; tướng quân",              # 将
    "Question; Ask":    "câu hỏi; hỏi",                   # 問
}

# ── 2. WORDS[].m fixes ────────────────────────────────────────────────────
WORD_FIXES = {
    # N5
    "xuống-tàu điện (going away từ Tokyo)":                  "xuống tàu (đi ngược hướng Tokyo)",
    "người of higher status; một's senior":                  "người bề trên; cấp trên",
    "most of; majority; chủ yếu":                            "phần lớn; đa số",
    "thất bại of điện":                                      "cúp điện; mất điện",
    "height (of cơ thể); stature":                           "chiều cao (cơ thể)",
    "midnight; dead of ban đêm/tối":                         "nửa đêm; giữa đêm khuya",
    "great chiến tranh; great battle":                       "đại chiến; cuộc chiến lớn",
    "race (of mọi người)":                                   "chủng tộc",
    "con người being; người":                                "con người; nhân loại",
    "crowd of mọi người":                                    "đám đông người",
    "at that thời gian; in those days (giống nhau như そのころ)": "hồi đó; thời đó",
    "bây giờ; this thời gian; lately":                       "lần này; dạo này",
    "từ bây giờ on; hereafter":                              "từ nay về sau",
    "số lượng of tiền":                                      "số tiền; mệnh giá",
    "nhận ra; nhận ra/công nhận; become aware of":           "nhận ra; nhận thức được",
    "dropping out of trường học":                            "bỏ học; nghỉ học",
    "bị/được disconnected; bị/được out (e.g; of gear)":      "bị tách ra; bị trật ra",
    "cơm/gạo field":                                         "cánh đồng lúa; ruộng lúa",
    "ý kiến; point of view":                                  "quan điểm; ý kiến",
    "ý kiến; point of view; visual point":                   "quan điểm; điểm nhìn",
    # N4
    "identical; giống nhau (kind); giống như":               "giống nhau; cùng loại",
    "composition (of âm nhạc)":                              "sáng tác (âm nhạc)",
    "deep màu đỏ; flushed (of mặt)":                        "đỏ thẫm; đỏ bừng mặt",
    "bị/được piled up; lie on top of một another":           "chồng lên nhau",
    "chất lượng/tính chất; tự nhiên (of người)":             "chất lượng; bản chất người",
    # N3 + sâu hơn
    "in a từ; sau tất cả; in ngắn …":                        "nói tóm lại; tóm lại",
    "in everyday situations; thường; ordinarily":            "hàng ngày; thường ngày",
    "in succession; một bởi/bằng một":                      "lần lượt; từng cái một",
    "sharing với; participate in":                           "cùng chia sẻ; cùng tham gia",
    "credit (cho/vì a course in trường học); unit; denomination": "tín chỉ (khóa học); đơn vị",
    "bây giờ (giống nhau như 今 (いま)); hiện tại/quà tặng; current": "hiện tại; bây giờ",
    "win; chiến thắng":                                      "thắng; chiến thắng",
    "kết thúc of; powder":                                   "kết thúc; bột (mịn)",
    "organ (of cơ thể; instrument)":                         "cơ quan (cơ thể); nhạc cụ",
    "poor (at); yếu (in); dislike (of)":                    "không giỏi; yếu kém; không thích",
    "bị/được brought up; grow (up)":                        "được nuôi dưỡng; lớn lên",
    "appear (v.i.); hiện ra; express":                       "xuất hiện; hiện ra",
    "người in charge":                                       "người phụ trách; người quản lý",
    "trạng thái of affairs; tình huống":                    "tình trạng sự việc; tình huống",
    "sự khác biệt (of ý kiến)":                              "bất đồng ý kiến",
    "target; object (of worship; học tập; etc.); subject (i.e; of taxation)": "đối tượng; mục tiêu (thờ phụng, học tập...)",
    "status; character; trường hợp":                         "địa vị; tính cách; trường hợp",
    "thứ tự/mệnh lệnh; turn":                                "thứ tự; lượt",
    "native tiếng Nhật/người Nhật reading of a tiếng Trung/người Trung Quốc character": "cách đọc âm Nhật (kunyomi) của chữ Hán",
    "keep; own (a pet); nâng lên/nuôi dưỡng; feed":         "nuôi (thú cưng); chăm sóc",
    "majority; adult tuổi":                                  "tuổi thành niên; đa số",
    "medium (e.g; đồ ăn serving size; chất lượng/tính chất; giá; etc.); bình thường": "bình thường; trung bình; mức vừa",
    "carrying something; mobile điện thoại":                 "mang theo; điện thoại di động",
    "cheer; shout of niềm vui":                              "hò reo; tiếng歓声 vui mừng",
    "hiện tại/quà tặng điều kiện/tình trạng; status quo":   "hiện trạng; tình trạng hiện tại",
    "hiện tại/quà tặng; give to; award to":                 "trao tặng; ban cho",
    "electron; điện tử":                                     "điện tử; electron",
    "chế độ trả lời tự động của điện thoại":                 "chế độ vắng mặt; trả lời tự động",
    "appear (in print); bị/được recorded":                  "xuất bản; được ghi chép",
    "extend; make progress; lớn lên/phát triển":            "mở rộng; tiến bộ; phát triển",
    "fall behind; bị/được inferior to":                     "tụt hậu; kém hơn",
    "go over (e.g; với audience)":                           "vượt qua; tiếp cận khán giả",
    "medium size":                                           "cỡ trung bình",
    "size (of giấy hoặc books)":                             "khổ (giấy hoặc sách)",
    "lần đầu 10 days of the month":                         "10 ngày đầu tháng",
    "lời xin lỗi; lý do":                                   "lời xin lỗi; biện hộ",
    "lý do, tình hình":                                      "lý do; tình hình",
    "phí; charge; fare":                                     "phí; lệ phí; giá vé",
    "rảnh/miễn phí; không charge":                          "miễn phí; không mất tiền",
    "thả tự do":                                             "thả tự do; giải phóng",
    "mở cửa, tự do":                                         "mở cửa; tự do",
    "say mê, cứng":                                          "say mê; bị hóa cứng",
    "hào hứng, say sưa":                                     "hào hứng; say sưa",
    "stock; stump (of cây)":                                 "gốc cây; cổ phiếu",
    "hiện tại/quà tặng; current":                           "hiện tại; bây giờ",
    "bus stop":                                              "trạm xe buýt",
    "buzz cut":                                              "tóc cắt ngắn",
    "buying power":                                          "sức mua",
    "pay cut":                                               "cắt giảm lương",
    "close attack":                                          "tấn công cận chiến",
    "condolence call":                                       "thăm viếng chia buồn",
    "detailed report":                                       "báo cáo chi tiết",
    "great admiration":                                      "sự ngưỡng mộ lớn",
    "great delight":                                        "niềm vui lớn",
    "great swordsman":                                       "kiếm khách bậc thầy",
    "great-grandchild":                                      "chắt; cháu cố",
    "long ago":                                              "từ lâu; ngày xưa",
    "long service":                                          "phục vụ lâu dài",
    "long silence":                                          "im lặng kéo dài",
    "stature":                                               "chiều cao; vóc dáng",
    "all":                                                   "tất cả",
    "all eyes":                                              "tất cả mọi người đều chú ý",
    "all means":                                             "mọi phương tiện; tất cả",
    "and":                                                   "và; cùng",
    "fall":                                                  "ngã; rơi; mùa thu",
    "long":                                                  "dài; lâu",
    "play":                                                  "chơi; vở kịch",
    "do ...":                                                "làm...; thực hiện...",
    "Go (board trò chơi of capturing territory)":           "cờ vây (trò chơi)",
    "Usui Pass":                                             "đèo Usui",
    "ván cờ Go":                                             "ván cờ vây",
    "không có tự do":                                        "thiếu tự do",
    "phát điên; hỏng":                                      "phát điên; hỏng hóc",
    "thẩm phân nhân tạo":                                   "thẩm phân nhân tạo (y tế)",
    "hô hấp nhân tạo":                                      "hô hấp nhân tạo",
    "hạt gạo":                                              "hạt gạo",
    "gạo":                                                  "gạo; cơm",
    "điền vào; nhập liệu":                                  "điền vào (biểu mẫu); nhập liệu",
    "điện":                                                  "điện; điện năng",
    "điện thoại":                                            "điện thoại",
    "tàu điện":                                              "tàu điện",
    "tàu điện (bình thường)":                               "tàu hỏa (thông thường)",
    "tàu điện ngầm":                                        "tàu điện ngầm; metro",
    "thứ Bảy":                                              "thứ Bảy",
    "tiếng to; ồn ào":                                      "giọng to; ồn ào",
    "to, lớn":                                              "to; lớn",
    "to; dày; béo":                                         "to; dày; béo",
    "trang điểm; make-up":                                  "trang điểm",
    "treo; đặt; gọi điện":                                  "treo; đặt; gọi (điện thoại)",
    "triển lãm; cuộc trưng bày":                            "triển lãm",
    "trạm dừng xe buýt hoặc tàu điện":                     "trạm dừng xe buýt hoặc tàu điện",
    "từ điển":                                              "từ điển",
    "đánh; apply to":                                       "đánh; áp dụng vào",
    "đáng kể; to lớn":                                      "đáng kể; to lớn",
    "mê mẩn; điên đảo vì":                                  "mê mẩn; say mê hoàn toàn",
    "mẫu; điển hình; nguyên mẫu":                          "mẫu; điển hình; nguyên mẫu",
    "nhiệt tình; say mê":                                   "nhiệt tình; say mê",
    "nhân tạo; do con người làm ra":                        "nhân tạo",
    "phim; điện ảnh":                                       "phim; điện ảnh",
    "phóng to; mở rộng":                                    "phóng to; mở rộng",
    "phồng to":                                             "phồng to; nở ra",
    "positron (hạt dương điện tử)":                        "positron (hạt dương điện tử)",
    "khổng lồ; to lớn":                                     "khổng lồ; to lớn",
    "khủng long":                                           "khủng long",
    "dồi dào; phong phú":                                   "dồi dào; phong phú",
    "gần đây; dạo này":                                     "gần đây; dạo này",
    "bây giờ; hiện tại":                                    "bây giờ; hiện tại",
    "nguyên nhân; lý do; fault":                            "nguyên nhân; lý do; lỗi",
    "sáng tạo":                                             "sáng tạo",
    "sáng tạo; tạo ra":                                     "sáng tạo; tạo ra",
    "lý do":                                                "lý do; nguyên nhân",
    "lý do; nguyên nhân":                                   "lý do; nguyên nhân",
    "biểu đạt; trình bày":                                  "biểu đạt; trình bày",
    "can đảm":                                              "can đảm; dũng cảm",
    "cung điện":                                            "cung điện",
    "điện thờ hoàng gia":                                   "cung điện hoàng gia",
    "in ấn":                                                "in ấn",
    "tăng; add to":                                         "tăng thêm; bổ sung",
    "cheer; shout of niềm vui":                             "hò reo; tiếng歓声 vui mừng",
    "nỗi sợ; bị/được afraid of":                           "sợ hãi; lo sợ điều gì đó",
}

def apply_fixes(path, fixes, field_type):
    content = path.read_text(encoding='utf-8')
    count = 0
    for bad, good in fixes.items():
        if field_type == 'meaning':
            pattern = r'(meaning:")' + re.escape(bad) + r'(")'
            repl = r'\g<1>' + good + r'\g<2>'
        else:  # word
            pattern = r'("m":")'  + re.escape(bad) + r'(")'
            repl = r'\g<1>' + good + r'\g<2>'
        new_content, n = re.subn(pattern, repl, content)
        if n:
            content = new_content
            count += n
    path.write_text(content, encoding='utf-8')
    return count

print("Fixing meaning fields...")
m_total = 0
for lv in ['n5','n4','n3','n2','n1']:
    path = JS / f'kanji-data-{lv}.js'
    n = apply_fixes(path, MEANING_FIXES, 'meaning')
    if n: print(f"  {lv.upper()}: {n} meaning fixes"); m_total += n

print(f"  Total meaning fixes: {m_total}")
print()
print("Fixing words[].m fields...")
w_total = 0
for lv in ['n5','n4','n3','n2','n1']:
    path = JS / f'kanji-data-{lv}.js'
    n = apply_fixes(path, WORD_FIXES, 'word')
    if n: print(f"  {lv.upper()}: {n} word fixes"); w_total += n

print(f"  Total word fixes: {w_total}")
print()

# Rebuild combined
print("Rebuilding kanji-data.js...")
parts = []
for lv in ['n5','n4','n3','n2','n1']:
    c = (JS / f'kanji-data-{lv}.js').read_text(encoding='utf-8')
    s = c.index('['); e = c.rindex(']') + 1
    inner = c[s+1:e-1].strip().rstrip(',')
    if inner: parts.append(inner)
(JS / 'kanji-data.js').write_text(
    'window.KANJI_DATA = [\n' + ',\n'.join(parts) + '\n];\n',
    encoding='utf-8'
)
print(f"Done. Total: {m_total + w_total} fixes applied.")
