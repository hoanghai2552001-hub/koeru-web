"""
KOERU — Fix English meanings in N4/N3 kanji data
Patch chính xác từng entry theo kanji character
"""
import re
from pathlib import Path

JS_DIR = Path(__file__).parent.parent / "js"

# ── Bảng dịch chính xác cho từng kanji ───────────────────────────────────────
FIXES = {
    # ── N4 (19 kanji) ──────────────────────────────────────────────────────────
    "業": "nghề nghiệp; công việc; ngành",
    "場": "nơi; địa điểm; sân; trường",
    "題": "chủ đề; đề tài; tiêu đề",
    "意": "ý nghĩa; ý kiến; tâm ý",
    "持": "giữ; nắm; có",
    "以": "bằng; do; vì",
    "院": "viện; tổ chức; bệnh viện",
    "品": "hàng hóa; phẩm chất; vật phẩm",
    "町": "thị trấn; phố; khu phố",
    "転": "xoay; quay; chuyển",
    "験": "kiểm nghiệm; thi; thử nghiệm",
    "写": "sao chép; chụp ảnh; viết lại",
    "悪": "xấu; ác; tồi tệ",
    "室": "phòng; gian; buồng",
    "風": "gió; phong cách; khí gió",
    "曜": "ngày trong tuần",
    "貸": "cho mượn; cho thuê",
    "堂": "hội trường; nhà hát; công đường",
    "勉": "nỗ lực; cố gắng; chuyên cần",

    # ── N3 (37 kanji) ──────────────────────────────────────────────────────────
    "議": "bàn bạc; thảo luận; nghị",
    "民": "nhân dân; dân; quốc dân",
    "部": "bộ phận; phòng ban; khoa",
    "回": "lần; vòng; lần lượt",
    "関": "liên quan; quan hệ; cửa ải",
    "最": "nhất; tối; cao nhất",
    "首": "cổ; đầu; người đứng đầu",
    "進": "tiến lên; tiến bộ; tiến",
    "記": "ghi chép; ký; ghi lại",
    "産": "sản phẩm; sinh ra; sản xuất",
    "所": "nơi; chỗ; địa điểm",
    "官": "quan chức; viên chức; cơ quan",
    "直": "thẳng; thật thà; trực tiếp",
    "確": "chắc chắn; đảm bảo; xác nhận",
    "位": "vị trí; hạng; cấp bậc",
    "格": "địa vị; tư cách; đẳng cấp",
    "球": "quả bóng; hình cầu; địa cầu",
    "割": "tỉ lệ; phần; chia cắt",
    "消": "tắt; xóa; tiêu",
    "規": "quy tắc; tiêu chuẩn; quy định",
    "葉": "lá; cánh hoa; từ",
    "非": "phi; không; sai",
    "観": "nhìn; quan sát; cảnh",
    "科": "môn học; khoa; khoa học",
    "客": "khách; khách hàng; hành khách",
    "座": "ghế ngồi; chỗ ngồi; tòa",
    "給": "lương; cung cấp; phát",
    "寄": "ghé lại; gần; gửi tới",
    "込": "chứa đựng; đông đúc; bao gồm",
    "便": "thuận tiện; tiện lợi; thư",
    "勤": "siêng năng; đi làm; chăm chỉ",
    "居": "ở; cư trú; tồn tại",
    "掛": "treo; mắc; khoác",
    "吸": "hút; hít; hút vào",
    "洗": "rửa; giặt; tẩy",
    "慣": "quen; thói quen; quen thuộc",
    "幾": "mấy; bao nhiêu; vài",
}

def patch_meaning(content, kanji, new_meaning):
    """Thay thế meaning của một kanji cụ thể trong JS file."""
    # Pattern: kanji:"X",...,meaning:"OLD"
    # Dùng lookahead để đảm bảo đúng kanji
    pattern = r'(kanji:"' + re.escape(kanji) + r'"(?:[^}]{0,50}?)meaning\s*:\s*)"[^"]*"'
    replacement = r'\g<1>"' + new_meaning.replace('"', '\\"') + '"'
    new_content, count = re.subn(pattern, replacement, content, count=1)
    return new_content, count

def main():
    files = {
        "n4": (JS_DIR / "kanji-data-n4.js").read_text(encoding="utf-8"),
        "n3": (JS_DIR / "kanji-data-n3.js").read_text(encoding="utf-8"),
        "n2": (JS_DIR / "kanji-data-n2.js").read_text(encoding="utf-8"),
    }

    stats = {"n4": 0, "n3": 0, "n2": 0}

    for kanji, meaning_vi in FIXES.items():
        patched = False
        for lv, content in files.items():
            if f'kanji:"{kanji}"' in content:
                new_content, count = patch_meaning(content, kanji, meaning_vi)
                if count:
                    files[lv] = new_content
                    stats[lv] += 1
                    patched = True
                    print(f"  ✓ {lv.upper()} {kanji} → \"{meaning_vi}\"")
                    break
        if not patched:
            print(f"  ✗ Không tìm thấy: {kanji}")

    # Write back
    for lv, content in files.items():
        (JS_DIR / f"kanji-data-{lv}.js").write_text(content, encoding="utf-8")

    print(f"\nĐã patch: N4={stats['n4']}, N3={stats['n3']}, N2={stats['n2']}")

    # Rebuild combined
    print("Rebuilding kanji-data.js...")
    parts = []
    for lv in ['n5','n4','n3','n2','n1']:
        c = (JS_DIR/f'kanji-data-{lv}.js').read_text(encoding='utf-8')
        start = c.index('[')
        end   = c.rindex(']') + 1
        inner = c[start+1:end-1].strip().rstrip(',')
        if inner: parts.append(inner)
    combined = 'window.KANJI_DATA = [\n' + ',\n'.join(parts) + '\n];\n'
    (JS_DIR/'kanji-data.js').write_text(combined, encoding='utf-8')
    print("Done!")

if __name__ == "__main__":
    main()
