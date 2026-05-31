"""
Tạo PDF học tập JLPT cho từng level N5→N1.
Output: output/KOERU_JLPT_N5.pdf, ..._N4.pdf, v.v.

Usage:
    python tools/gen_study_pdf.py          # tạo tất cả 5 level
    python tools/gen_study_pdf.py N5       # chỉ tạo N5
    python tools/gen_study_pdf.py N5 N4    # tạo N5 và N4
"""
import re, sys
from pathlib import Path
from fpdf import FPDF

ROOT       = Path(__file__).parent.parent
FONT_JP    = r"C:\Windows\Fonts\NotoSansJP-VF.ttf"
FONT_LATIN = r"C:\Windows\Fonts\NotoSans-Regular.ttf"
FONT_BOLD  = r"C:\Windows\Fonts\NotoSans-Bold.ttf"
OUT_DIR    = ROOT / "output"

# ── Màu theo level ──────────────────────────────────────────────────────────
LEVEL_STYLE = {
    "N5": {"bg": (34, 197, 94),   "light": (220, 252, 231), "label": "Sơ cấp"},
    "N4": {"bg": (59, 130, 246),  "light": (219, 234, 254), "label": "Sơ-Trung cấp"},
    "N3": {"bg": (249, 115, 22),  "light": (255, 237, 213), "label": "Trung cấp"},
    "N2": {"bg": (168, 85, 247),  "light": (243, 232, 255), "label": "Trung-Cao cấp"},
    "N1": {"bg": (239, 68, 68),   "light": (254, 226, 226), "label": "Cao cấp"},
}

KANJI_COUNTS = {"N5": 103, "N4": 116, "N3": 89, "N2": 545, "N1": 628}

# ── Parse kanji-data.js ──────────────────────────────────────────────────────
def parse_kanji_by_level(level):
    content = (ROOT / "js" / "kanji-data.js").read_text(encoding="utf-8")
    entries = []
    i = 0
    n = len(content)
    while i < n:
        while i < n and content[i] != "{":
            i += 1
        if i >= n:
            break
        depth, start = 0, i
        while i < n:
            if content[i] == "{":   depth += 1
            elif content[i] == "}": depth -= 1
            if depth == 0: break
            i += 1
        block = content[start : i + 1]
        i += 1

        lv = re.search(r'\blevel\s*:\s*"([^"]+)"', block)
        if not lv or lv.group(1) != level:
            continue

        def gs(key, b=block):
            m = re.search(rf'\b{key}\s*:\s*"((?:[^"\\]|\\.)*)"', b)
            return m.group(1).replace('\\"', '"') if m else ""

        def gn(key, b=block):
            m = re.search(rf'\b{key}\s*:\s*(\d+)', b)
            return m.group(1) if m else ""

        def gwords(b=block):
            m = re.search(r'\bwords\s*:\s*\[(.+?)\](?=\s*[,}])', b, re.DOTALL)
            if not m: return []
            ws = re.findall(r'"w"\s*:\s*"([^"]+)"', m.group(1))
            rs = re.findall(r'"r"\s*:\s*"([^"]+)"', m.group(1))
            ms = re.findall(r'"m"\s*:\s*"([^"]+)"', m.group(1))
            return [{"w": ws[j], "r": rs[j] if j < len(rs) else "",
                     "m": ms[j] if j < len(ms) else ""}
                    for j in range(min(len(ws), 4))]

        def gparts(b=block):
            m = re.search(r'\bparts\s*:\s*\[([^\]]*)\]', b)
            if not m: return []
            return re.findall(r'"([^"]+)"', m.group(1))

        entries.append({
            "kanji":      gs("kanji"),
            "hanviet":    gs("hanviet"),
            "on":         gs("on"),
            "kun":        gs("kun"),
            "meaning":    gs("meaning"),
            "meaning_en": gs("meaning_en"),
            "mn_vi":      gs("mn_vi"),
            "mnemonic":   gs("mnemonic"),
            "stroke":     gn("stroke"),
            "freq_rank":  gn("freq_rank"),
            "radical":    gs("radical").split("|")[0] if gs("radical") else "",
            "parts":      gparts(),
            "words":      gwords(),
        })
    return entries


# ── PDF Class ────────────────────────────────────────────────────────────────
class StudyPDF(FPDF):
    def __init__(self, level):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.level   = level
        self.style   = LEVEL_STYLE[level]
        self.set_margins(14, 14, 14)
        self.set_auto_page_break(True, margin=16)
        # Fonts
        self.add_font("JP",   "", FONT_JP,    uni=True)
        self.add_font("JP",   "B", FONT_JP,   uni=True)
        if Path(FONT_LATIN).exists():
            self.add_font("Latin", "",  FONT_LATIN, uni=True)
            self.add_font("Latin", "B", FONT_BOLD,  uni=True)
        else:
            self.add_font("Latin", "",  FONT_JP, uni=True)
            self.add_font("Latin", "B", FONT_JP, uni=True)

    def header(self):
        if self.page_no() == 1:
            return
        r, g, b = self.style["bg"]
        self.set_fill_color(r, g, b)
        self.rect(0, 0, 210, 8, "F")
        self.set_font("JP", "", 7)
        self.set_text_color(255, 255, 255)
        self.set_xy(14, 1)
        self.cell(0, 6, f"KOERU · JLPT {self.level} · {self.style['label']}", align="L")
        self.set_xy(0, 1)
        self.cell(196, 6, f"trang {self.page_no() - 1}", align="R")
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-10)
        self.set_font("Latin", "", 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 6, "koeru.vn · Dữ liệu: KanjiVG (CC BY-SA 3.0) · the-kanji-map (CC BY-SA 3.0)", align="C")
        self.set_text_color(0, 0, 0)

    # ── Cover page ─────────────────────────────────────────────────────────
    def cover_page(self, kanji_count):
        self.add_page()
        r, g, b = self.style["bg"]

        # Top band
        self.set_fill_color(r, g, b)
        self.rect(0, 0, 210, 90, "F")

        # KOERU label
        self.set_font("Latin", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 18)
        self.cell(210, 10, "KOERU  Tai lieu luyen thi JLPT", align="C")

        # Big level badge
        self.set_font("JP", "B", 72)
        self.set_xy(0, 28)
        self.cell(210, 40, f"JLPT {self.level}", align="C")

        # Subtitle
        self.set_font("Latin", "", 14)
        self.set_xy(0, 68)
        self.cell(210, 10, self.style["label"], align="C")

        # Stats strip
        self.set_fill_color(255, 255, 255)
        self.set_text_color(r, g, b)
        self.set_font("Latin", "B", 13)
        self.set_xy(40, 100)
        self.cell(130, 14, f"{kanji_count} Kanji", align="C", fill=True, border=0)

        # Description
        self.set_text_color(60, 60, 60)
        self.set_font("JP", "", 11)
        self.set_xy(20, 124)
        self.multi_cell(170, 7,
            "Tài liệu tổng hợp toàn bộ Kanji và từ vựng mẫu theo chuẩn JLPT.\n"
            "Mỗi kanji bao gồm: cách đọc On/Kun, nghĩa tiếng Việt, Hán Việt,\n"
            "gợi nhớ tiếng Việt và các từ vựng mẫu thường gặp trong kỳ thi.",
            align="C"
        )

        # How to use
        self.set_fill_color(*self.style["light"])
        self.set_draw_color(r, g, b)
        self.set_xy(20, 152)
        self.set_font("JP", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(170, 6.5,
            "Cach hoc hieu qua:\n"
            "1. Đọc kanji + nghĩa tiếng Việt → đoán cách đọc trước\n"
            "2. Xem phần gợi nhớ để tạo liên kết hình ảnh\n"
            "3. Luyện từ vựng mẫu để nhớ kanji trong ngữ cảnh thực tế\n"
            "4. Dùng KOERU Kanji Lab để luyện bằng game",
            border=1, fill=True
        )

        # Footer note
        self.set_font("Latin", "", 8)
        self.set_text_color(140, 140, 140)
        self.set_xy(0, 274)
        self.cell(210, 6, "koeru.vn  ·  Nguồn dữ liệu: KanjiVG (CC BY-SA 3.0), the-kanji-map (CC BY-SA 3.0)", align="C")

    # ── Section header ──────────────────────────────────────────────────────
    def section_header(self, text):
        r, g, b = self.style["bg"]
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font("JP", "B", 11)
        self.cell(0, 8, f"  {text}", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    # ── Kanji card (compact row) ────────────────────────────────────────────
    def kanji_row(self, idx, entry):
        r, g, b = self.style["light"]
        R, G, B = self.style["bg"]

        x0 = self.get_x()
        y0 = self.get_y()
        row_h = 28

        # Check page break
        if y0 + row_h > self.h - 20:
            self.add_page()
            y0 = self.get_y()

        # Alternating background
        if idx % 2 == 0:
            self.set_fill_color(r, g, b)
            self.rect(14, y0, 182, row_h, "F")

        # ── Kanji big character (col 1, w=18) ──
        self.set_xy(14, y0)
        self.set_font("JP", "B", 26)
        self.set_text_color(R, G, B)
        self.cell(18, row_h, entry["kanji"], align="C")

        # ── Hanviet + stroke (col 2, w=22) ──
        self.set_xy(32, y0 + 2)
        self.set_font("JP", "B", 9)
        self.set_text_color(40, 40, 40)
        self.cell(22, 5, entry["hanviet"], align="C")
        self.set_xy(32, y0 + 8)
        self.set_font("Latin", "", 7)
        self.set_text_color(120, 120, 120)
        stroke_txt = f"{entry['stroke']} nét" if entry["stroke"] else ""
        if entry["freq_rank"]:
            stroke_txt += f"  #{entry['freq_rank']}"
        self.cell(22, 5, stroke_txt, align="C")

        # ── Meaning VI (col 3, w=36) ──
        self.set_xy(54, y0 + 2)
        self.set_font("JP", "B", 9)
        self.set_text_color(10, 10, 10)
        meaning = entry["meaning"][:40]
        self.multi_cell(36, 5, meaning)

        # ── On / Kun (col 4, w=42) ──
        self.set_xy(90, y0 + 2)
        self.set_font("JP", "", 8)
        self.set_text_color(60, 60, 60)
        on_txt = f"音: {entry['on']}" if entry["on"] else ""
        kun_txt = f"訓: {entry['kun']}" if entry["kun"] else ""
        self.cell(42, 5, on_txt)
        self.set_xy(90, y0 + 8)
        self.cell(42, 5, kun_txt)

        # ── Gợi nhớ (col 5, w=60) ──
        mn = entry.get("mn_vi") or entry.get("mnemonic") or ""
        if mn:
            self.set_xy(132, y0 + 1)
            self.set_font("JP", "", 7.5)
            self.set_text_color(80, 80, 80)
            self.multi_cell(64, 4.5, mn[:100], align="L")

        # ── Words (below, full width) ──
        words = entry.get("words", [])
        if words:
            self.set_xy(14, y0 + 16)
            self.set_font("JP", "", 7.5)
            self.set_text_color(50, 80, 50)
            word_strs = []
            for w in words[:4]:
                word_strs.append(f"{w['w']}（{w['r']}）{w['m']}")
            self.cell(182, 5, "   ".join(word_strs))

        # ── Divider line ──
        self.set_draw_color(200, 200, 200)
        self.line(14, y0 + row_h, 196, y0 + row_h)
        self.set_draw_color(0, 0, 0)

        self.set_xy(14, y0 + row_h)
        self.set_text_color(0, 0, 0)

    # ── Vocabulary index ────────────────────────────────────────────────────
    def vocab_section(self, entries):
        self.add_page()
        self.section_header(f"Tu vung mau — JLPT {self.level}")
        self.ln(2)

        # Collect all unique words
        all_words = {}
        for e in entries:
            for w in e.get("words", []):
                key = w["w"]
                if key not in all_words:
                    all_words[key] = {**w, "kanji": e["kanji"]}

        words_list = sorted(all_words.values(), key=lambda x: x["w"])
        r, g, b = self.style["light"]
        R, G, B = self.style["bg"]

        # 2-column layout
        col_w = 88
        cols = [14, 110]
        col_idx = 0
        y_starts = [self.get_y(), self.get_y()]

        for i, w in enumerate(words_list):
            cx = cols[col_idx]
            cy = y_starts[col_idx]

            if cy + 12 > self.h - 18:
                if col_idx == 0:
                    col_idx = 1
                    cy = y_starts[0]
                    y_starts[1] = cy
                else:
                    self.add_page()
                    y_starts = [self.get_y(), self.get_y()]
                    col_idx = 0
                    cy = y_starts[0]

            if i % 2 == 0:
                self.set_fill_color(r, g, b)
                self.rect(cx, cy, col_w, 12, "F")

            # Word
            self.set_xy(cx + 1, cy + 1)
            self.set_font("JP", "B", 10)
            self.set_text_color(R, G, B)
            self.cell(26, 5, w["w"])

            # Reading
            self.set_xy(cx + 27, cy + 1)
            self.set_font("JP", "", 8)
            self.set_text_color(60, 60, 60)
            self.cell(26, 5, f"（{w['r']}）")

            # Meaning
            self.set_xy(cx + 1, cy + 7)
            self.set_font("JP", "", 8)
            self.set_text_color(40, 40, 40)
            self.cell(col_w - 2, 4.5, w["m"][:40])

            y_starts[col_idx] = cy + 12
            col_idx = 1 - col_idx  # alternate columns


# ── Main ────────────────────────────────────────────────────────────────────
def generate(level):
    print(f"\n📄 Đang tạo JLPT {level}...")
    entries = parse_kanji_by_level(level)
    print(f"   Parsed {len(entries)} kanji")

    pdf = StudyPDF(level)

    # Cover
    pdf.cover_page(len(entries))

    # Kanji pages
    pdf.add_page()
    pdf.section_header(f"Bang Kanji — JLPT {level}  ({len(entries)} chu)")
    pdf.ln(2)

    # Column headers
    y = pdf.get_y()
    pdf.set_fill_color(*LEVEL_STYLE[level]["bg"])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Latin", "B", 8)
    for (x, w, txt) in [
        (14, 18, "Kanji"), (32, 22, "Han Viet"), (54, 36, "Nghia VI"),
        (90, 42, "Cach doc"), (132, 64, "Goi nho / Tu mau")
    ]:
        pdf.set_xy(x, y)
        pdf.cell(w, 7, txt, align="C", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    for i, entry in enumerate(entries):
        pdf.kanji_row(i, entry)

    # Vocabulary index
    pdf.vocab_section(entries)

    # Save
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"KOERU_JLPT_{level}.pdf"
    pdf.output(str(out))
    print(f"   ✅ Saved → {out}  ({out.stat().st_size // 1024} KB)")


def main():
    levels = [a.upper() for a in sys.argv[1:] if a.upper() in LEVEL_STYLE]
    if not levels:
        levels = ["N5", "N4", "N3", "N2", "N1"]

    print(f"Tạo PDF cho: {', '.join(levels)}")
    for lv in levels:
        generate(lv)
    print(f"\n✅ Xong! Files ở thư mục: {OUT_DIR}")


if __name__ == "__main__":
    main()
