# -*- coding: utf-8 -*-
"""Parse 50 docx ngữ pháp KOERU_Minna (Bài 1-50) → minna-grammar-data.js
Nguồn: jlpt-lesson-generator/output/docs/grammar/{Bai01_25/Bài 1-25, Bai26_50}
Template docx: H "2. Ngữ pháp" > heading con mỗi mẫu "2.x ..." > sub Công thức/Ví dụ/
Nuance/Khi nào dùng/So sánh. Level heading lệch giữa các file → dò động.
Ví dụ nằm ở nhiều dạng: mục con "Ví dụ", bảng (Ví dụ | Dịch nghĩa), inline "JP。(VN)",
"JP — VN", "JP\\n→ VN", và mục H1 "4. Ví dụ câu" (pool chung, match về từng mẫu).
Chạy: python tools/gen_minna_grammar_data.py
"""
import io, os, re, glob, json
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = r"C:\Users\hoang\Desktop\PROJECT\jlpt-lesson-generator\output\docs\grammar"
OUT = os.path.join(ROOT, "minna-grammar-data.js")

MAX_EX = 5
MIN_EX = 3

def lesson_files():
    files = {}
    for pat, rng in [(os.path.join(SRC, "Bai01_25", "Bài 1-25", "KOERU_Minna_Bai*.docx"), range(1, 26)),
                     (os.path.join(SRC, "Bai26_50", "KOERU_Minna_Bai*.docx"), range(26, 51))]:
        for p in glob.glob(pat):
            if p.endswith(".bak") or "~$" in os.path.basename(p):
                continue
            m = re.search(r"Bai(\d+)_", os.path.basename(p))
            if m and int(m.group(1)) in rng:
                files[int(m.group(1))] = p
    return files

# phân loại heading/label mục con (tên biến thể giữa các file)
H3_MAP = [
    (re.compile(r"công thức|cách chia|cấu trúc", re.I), "formula"),
    (re.compile(r"ví dụ", re.I), "examples"),
    (re.compile(r"nuance|sắc thái|ý nghĩa|chức năng", re.I), "nuance"),
    (re.compile(r"khi nào|lỗi|không dùng|lưu ý", re.I), "usage"),
    (re.compile(r"so sánh|dễ nhầm|phân biệt", re.I), "compare"),
]

JP_RE = re.compile(r"[ぁ-ゖァ-ヺ一-鿿々]")
VN_LETTER_RE = re.compile(r"[A-Za-zÀ-ỹà-ỹĐđ]")

def classify_h3(text):
    for rx, key in H3_MAP:
        if rx.search(text):
            return key
    return None

def heading_level(style):
    m = re.match(r"Heading (\d)", style or "")
    return int(m.group(1)) if m else None

def iter_blocks(doc):
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield ("p", Paragraph(child, doc))
        elif child.tag.endswith("}tbl"):
            yield ("t", Table(child, doc))

def norm_jp(s):
    return re.sub(r"[\s。、！？!?・「」『』（）()＿_\-—–~～]", "", s)

def is_vn(s):
    return bool(VN_LETTER_RE.search(s)) and not JP_RE.search(s)

def clean_jp(s):
    s = re.sub(r"^[①-⑳㉑-㉟0-9０-９]+[.、．)）]?\s*", "", s.strip())
    return s.strip()

def clean_vn(s):
    s = s.strip()
    s = re.sub(r"^[→⇒—–\-:：]\s*", "", s)
    # bỏ chú thích "(Giải thích: ...)" và ghi chú sau " — "
    s = re.sub(r"\s*[（(]Giải thích.*$", "", s, flags=re.I | re.S)
    s = re.sub(r"\s+[—–]\s+[^—–]*$", "", s) if re.search(r"[.!?。」)）]\s+[—–]\s+", s) else s
    # bỏ chú thích ngữ pháp cuối câu "(...)" nếu chứa ký tự JP (VD: "(N＋に：…)")
    m = re.search(r"\s*[（(]([^()（）]*)[)）]\s*$", s)
    if m and JP_RE.search(m.group(1)) and s[:m.start()].strip():
        s = s[:m.start()]
    return s.strip()

def looks_sentence(jp):
    jp2 = jp.strip()
    return len(norm_jp(jp2)) >= 4 and (
        re.search(r"[。！？!?]", jp2) or
        re.search(r"(です|ます|ました|ません|ましょう|ください|でしょう|だ|よ|ね|か)\s*$", jp2))

BAD_JP_RE = re.compile(r"[+＋/／|｜=＿]|(^|[\s（(])[VNSA]\d?[\s）)＋]|(て|た|ない|ます|辞書)形|\bbỏ\b|\bthể\b|Giải thích", re.I)

def bad_jp(jp):
    return bool(BAD_JP_RE.search(jp))

def pairs_inline(text):
    """Tách cặp 'JP。(VN)' / 'JP — VN' / 'JP → VN' nằm trong 1 dòng."""
    out = []
    # dạng JP ... ( VN )
    for m in re.finditer(r"([ぁ-ゖァ-ヺ一-鿿々][^（()）|｜]*?)\s*[（(]([^()（）]+)[)）]", text):
        jp, vn = m.group(1).strip(), m.group(2).strip()
        if JP_RE.search(jp) and is_vn(vn) and len(vn) >= 4 and looks_sentence(jp) and not bad_jp(jp):
            out.append({"jp": clean_jp(jp), "vn": clean_vn(vn)})
    if out:
        return out
    # dạng JP — VN / JP → VN / JP: VN
    m = re.match(r"^(.*?[ぁ-ゖァ-ヺ一-鿿々][。？！]?)\s*[—–→⇒:：]\s*(.+)$", text)
    if m and JP_RE.search(m.group(1)) and looks_sentence(m.group(1)) and not bad_jp(m.group(1)):
        vn = clean_vn(m.group(2))
        if is_vn(vn):
            out.append({"jp": clean_jp(m.group(1)), "vn": vn})
    return out

def valid_pair(e):
    """jp phải thực sự là câu tiếng Nhật (đa số ký tự JP, không dấu tiếng Việt), vn thuần Việt."""
    jp, vn = e["jp"], e["vn"]
    if not jp or not vn or re.search(r"[À-ỹà-ỹĐđ]", jp):
        return False
    letters = re.findall(r"\S", jp)
    njp = len(JP_RE.findall(jp))
    return njp >= 4 and njp / max(len(letters), 1) >= 0.5 and is_vn(vn)

def pairs_from_lines(lines):
    """Ghép danh sách dòng thành cặp {jp, vn}: inline hoặc JP theo sau bởi dòng Việt."""
    exs, cur_jp = [], None
    flat = []
    for ln in lines:
        flat.extend(ln.splitlines())
    for ln in flat:
        ln = ln.strip()
        if not ln or re.match(r"^Giải thích", ln, re.I):
            continue
        # dòng "→ VN (Giải thích: ... có thể chứa JP)" — là bản dịch cho JP đang chờ
        if re.match(r"^[→⇒]", ln) and cur_jp:
            vn = clean_vn(ln)
            if is_vn(vn):
                exs.append({"jp": cur_jp, "vn": vn})
                cur_jp = None
                continue
        inl = pairs_inline(ln)
        if inl:
            cur_jp = None
            exs.extend(inl)
            continue
        if cur_jp and not JP_RE.search(re.sub(r"[（(][^()（）]*[)）]", "", ln)):
            # dòng Việt (có thể kèm chú thích JP trong ngoặc) → bản dịch cho JP đang chờ
            vn = clean_vn(ln)
            if is_vn(vn):
                exs.append({"jp": cur_jp, "vn": vn})
            cur_jp = None
        elif JP_RE.search(ln):
            cur_jp = clean_jp(ln) if not bad_jp(ln) else None
    return [e for e in exs if valid_pair(e)]

def row_cell_texts(row):
    """Đọc text từng cell trực tiếp từ XML — một số docx sinh máy làm cell.text rỗng."""
    out = []
    for tc in row._tr.iter():
        if tc.tag.endswith("}tc"):
            txt = "".join(t.text or "" for t in tc.iter() if t.tag.endswith("}t")).strip()
            out.append(txt)
    return out

def pairs_from_table(tbl):
    """Bảng ví dụ: tìm trong mỗi row cặp cell (JP câu, VN thuần) cạnh nhau,
    hoặc cell chứa inline 'JP (VN)'."""
    out = []
    for row in tbl.rows:
        raw = [c.text.strip() for c in row.cells]
        if not any(raw):
            raw = row_cell_texts(row)
        cells, seen = [], set()
        for t in raw:
            if t and t not in seen:
                cells.append(t); seen.add(t)
        found = False
        for i in range(len(cells) - 1):
            jp, vn = cells[i], cells[i + 1]
            if JP_RE.search(jp) and looks_sentence(jp) and is_vn(vn) and len(vn) >= 4:
                out.append({"jp": clean_jp(jp), "vn": clean_vn(vn)})
                found = True
                break
        if not found:
            for c in cells:
                out.extend(pairs_inline(c))
    return [e for e in out if valid_pair(e)]

def table_text(tbl):
    rows = []
    for row in tbl.rows:
        cells = [c.text.strip() for c in row.cells]
        if not any(cells):
            cells = row_cell_texts(row)
        seen, outc = set(), []
        for c in cells:
            if c and c not in seen:
                outc.append(c); seen.add(c)
        if outc:
            rows.append(" | ".join(outc))
    return rows

# label đầu dòng chuyển mục (không phải heading)
LABEL_RE = re.compile(r"^(công thức|cách chia|ví dụ|nuance|ý nghĩa|so sánh[^:：]*|khi nào dùng[^:：]*|lỗi thường gặp|lưu ý)\s*[:：]?\s*", re.I)

def title_fragments(title):
    """Trích các cụm JP trong title mẫu để match ví dụ."""
    frags = []
    for run in re.findall(r"[ぁ-ゖァ-ヺ一-鿿々ー]+", title):
        run = run.strip("ー")
        # bỏ token generic
        for tok in re.split(r"[／/・]", run):
            if len(tok) >= 2 and tok not in ("動詞", "名詞", "形容詞", "普通形", "辞書形", "意向形", "命令形", "禁止形", "条件形", "受身", "尊敬語", "謙譲語", "丁寧語"):
                frags.append(tok)
    # ưu tiên cụm dài trước
    return sorted(set(frags), key=len, reverse=True)

def parse_lesson(path):
    doc = Document(path)
    blocks = list(iter_blocks(doc))

    # dò level heading của mục "2. Ngữ pháp"
    sec_level = None
    for kind, b in blocks:
        if kind == "p":
            lv = heading_level(b.style.name if b.style is not None else "")
            if lv and re.match(r"^2[\.．]?\s*", b.text.strip()) and "Ngữ pháp" in b.text:
                sec_level = lv
                break
    if sec_level is None:
        sec_level = 1

    patterns = []
    pool_lines, pool_tables = [], []   # mục "4. Ví dụ câu"
    state = None  # None | 'grammar' | 'pool'
    cur, cur_key, buf = None, None, {}
    cur_tables = []  # bảng thuộc mẫu hiện tại

    def flush_pattern():
        nonlocal cur, buf, cur_tables
        if cur is None:
            return
        cur["formula"] = "\n".join(buf.get("formula", [])).strip()
        cur["explain"] = "\n".join(buf.get("nuance", [])).strip()
        cur["usage"] = "\n".join(buf.get("usage", [])).strip()
        cur["compare"] = "\n".join(buf.get("compare", [])).strip()
        cur["_ex_lines"] = list(buf.get("examples", []))
        cur["_other_lines"] = sum((buf.get(k, []) for k in ("formula", "nuance", "usage", "compare")), [])
        cur["_tables"] = cur_tables
        patterns.append(cur)
        cur, buf, cur_tables = None, {}, []

    for kind, block in blocks:
        if kind == "t":
            if state == "grammar" and cur is not None:
                cur_tables.append((cur_key, block))
                if cur_key and cur_key != "examples":
                    buf.setdefault(cur_key, []).extend(table_text(block))
            elif state == "pool":
                pool_tables.append(block)
            continue
        p = block
        style = (p.style.name if p.style is not None else "") or ""
        text = p.text.strip()
        if not text:
            continue
        lv = heading_level(style)
        if lv is not None and lv <= sec_level:
            # heading cấp mục lớn
            flush_pattern()
            if re.match(r"^2[\.．]?\s", text) or "Ngữ pháp" in text:
                state = "grammar"
            elif re.match(r"^4[\.．]?\s", text) or "Ví dụ câu" in text:
                state = "pool"
            else:
                state = None
            continue
        if state == "pool":
            if lv is None:
                pool_lines.append(text)
            continue
        if state != "grammar":
            continue
        if lv == sec_level + 1:
            # heading cấp mẫu — nhưng nếu là tên mục con (Công thức/Nuance...) không đánh số → chuyển mục
            k = classify_h3(text)
            if k and not re.match(r"^2[\.．]?\d", text):
                cur_key = k
                continue
            flush_pattern()
            title = re.sub(r"^2[\.．]?\d+[\.．]?\s*", "", text)
            cur = {"title": title}
            cur_key = "nuance"
            buf, cur_tables = {}, []
            continue
        if lv is not None and lv >= sec_level + 2:
            cur_key = classify_h3(text) or cur_key
            continue
        if cur is None:
            continue
        m = LABEL_RE.match(text)
        if m:
            k = classify_h3(m.group(1))
            if k:
                cur_key = k
                rest = text[m.end():].strip()
                if rest:
                    buf.setdefault(cur_key, []).append(rest)
                continue
        buf.setdefault(cur_key or "nuance", []).append(text)
    flush_pattern()

    # ---- gom ví dụ cho từng mẫu ----
    def add(pt, exs, cap=MAX_EX):
        for e in exs:
            if len(pt["examples"]) >= cap:
                return
            key = norm_jp(e["jp"])
            if not key or not e["vn"] or key in pt["_seen"]:
                continue
            pt["_seen"].add(key)
            pt["examples"].append(e)

    for pt in patterns:
        pt["examples"], pt["_seen"] = [], set()
        # 1) mục "Ví dụ" của mẫu
        add(pt, pairs_from_lines(pt["_ex_lines"]))
        # 2) bảng trong mẫu (bảng ví dụ hoặc bảng công thức có cột ví dụ)
        for _k, tbl in pt["_tables"]:
            add(pt, pairs_from_table(tbl))

    # pool mục 4
    pool = pairs_from_lines(pool_lines)
    for tbl in pool_tables:
        pool.extend(pairs_from_table(tbl))
    used = set()

    # 3) match pool theo cụm JP trong title — 1 câu có thể minh hoạ nhiều mẫu (VD: mẫu "So sánh A vs B")
    frag_map = [(pt, title_fragments(pt["title"])) for pt in patterns]
    for i, e in enumerate(pool):
        if not e["vn"]:
            continue
        key = norm_jp(e["jp"])
        for pt, frags in frag_map:
            if any(f in key for f in frags):
                if len(pt["examples"]) < MAX_EX and key not in pt["_seen"]:
                    pt["_seen"].add(key)
                    pt["examples"].append(e)
                    used.add(i)

    # 4) mẫu còn thiếu: đào inline trong text còn lại của chính mẫu đó
    for pt in patterns:
        if len(pt["examples"]) < MIN_EX:
            add(pt, pairs_from_lines(pt["_other_lines"]), cap=MIN_EX)

    # 5) phân bổ pool còn dư cho mẫu ít ví dụ nhất
    leftover = [e for i, e in enumerate(pool) if i not in used]
    for e in leftover:
        if not e["vn"]:
            continue
        key = norm_jp(e["jp"])
        cands = [pt for pt in patterns if len(pt["examples"]) < MIN_EX and key not in pt["_seen"]]
        if not cands:
            continue
        pt = min(cands, key=lambda x: len(x["examples"]))
        pt["_seen"].add(key)
        pt["examples"].append(e)

    # 6) vét cuối: mẫu vẫn <3 → mượn lại ví dụ trong pool của bài (cùng chủ đề bài học)
    for pt in patterns:
        if len(pt["examples"]) >= MIN_EX:
            continue
        for e in pool:
            if len(pt["examples"]) >= MIN_EX:
                break
            key = norm_jp(e["jp"])
            if e["vn"] and key and key not in pt["_seen"]:
                pt["_seen"].add(key)
                pt["examples"].append(e)

    for pt in patterns:
        for k in ("_ex_lines", "_other_lines", "_tables", "_seen"):
            pt.pop(k, None)
    return patterns

def main():
    files = lesson_files()
    data, report, short = {}, [], []
    tot_p = tot_e = n_ge3 = 0
    for n in range(1, 51):
        p = files.get(n)
        if not p:
            report.append(f"B{n}: KHÔNG CÓ FILE")
            continue
        pats = parse_lesson(p)
        data[n] = pats
        counts = [len(pt["examples"]) for pt in pats]
        tot_p += len(pats)
        tot_e += sum(counts)
        n_ge3 += sum(1 for c in counts if c >= MIN_EX)
        few = [(pt["title"][:30], len(pt["examples"])) for pt in pats if len(pt["examples"]) < MIN_EX]
        short.extend((n, t, c) for t, c in few)
        report.append(f"B{n}: {len(pats)} mẫu, ví dụ/mẫu={counts}" + (f" | <3vd: {few}" if few else ""))
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("// AUTO-GENERATED — KHÔNG sửa tay. Regen: python tools/gen_minna_grammar_data.py\n")
        f.write("// Nguồn: 50 docx KOERU_Minna (jlpt-lesson-generator/output/docs/grammar)\n")
        f.write("window.MINNA_GRAMMAR = ")
        f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")
    print("\n".join(report))
    print(f"\nTổng: {tot_p} mẫu, {tot_e} ví dụ | ≥3 ví dụ: {n_ge3}/{tot_p} ({100*n_ge3/tot_p:.0f}%)")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
