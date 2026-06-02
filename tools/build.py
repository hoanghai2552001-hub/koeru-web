#!/usr/bin/env python3
"""
KOERU — Master Build Script
============================
Dùng: python tools/build.py          ← full build (sync + version + excel + study HTML + check)
      python tools/build.py --quick   ← chỉ sync data + bump version (nhanh, không gen study HTML)
      python tools/build.py --check   ← chỉ chạy data quality check

Một lệnh duy nhất sau mỗi thay đổi data:
  python tools/build.py

Tự động thực hiện:
  1. Sync N-level files → kanji-data.js
  2. Bump ?v= cache-buster trong HTML + JS
  3. Cập nhật study/index.html counts
  4. Export Excel (input/excel/kanji_KOERU_full.xlsx)
  5. Regenerate study HTML (study/n5.html, n4.html, n3.html)
  6. Chạy data quality check
  7. Dọn backup cũ
"""

import re, sys, shutil, subprocess, time
from pathlib import Path
from datetime import datetime

PROJECT = Path(__file__).parent.parent
JS = PROJECT / "js"

LEVEL_ORDER = ["n5", "n4", "n3", "n2", "n1"]


# ── Helpers ────────────────────────────────────────────────────────────────

def log(msg, icon="→"):
    print(f"  {icon}  {msg}")


def section(title):
    print(f"\n{'═'*50}")
    print(f"  {title}")
    print(f"{'═'*50}")


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_suffix(f".{ts}.bak")
    shutil.copy2(path, bak)
    return bak


def read_entries(path: Path) -> list[str]:
    """Đọc file N-level, trả về list raw entry strings."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'^.*?=\s*\[', '', content, count=1, flags=re.DOTALL)
    content = re.sub(r'\];\s*$', '', content.strip())
    entries = [line.strip() for line in content.split('\n') if line.strip()]
    entries = [e.rstrip(',') for e in entries if e and e != ',']
    return entries


# ── Step 1: Sync N-level → kanji-data.js ──────────────────────────────────

def sync_to_main(levels=None, verbose=True):
    """Merge N-level files → kanji-data.js. Returns True if changed."""
    levels = levels or LEVEL_ORDER
    target = JS / "kanji-data.js"

    if verbose:
        section(f"Step 1 · Sync {', '.join(l.upper() for l in levels)} → kanji-data.js")

    with open(target, encoding="utf-8") as f:
        main_content = f.read()

    main_entries = {}
    for line in main_content.split('\n'):
        km = re.search(r'kanji:"(.)"', line)
        if km:
            main_entries[km.group(1)] = line.rstrip().rstrip(',')

    updated = 0
    added = 0
    for level in levels:
        path = JS / f"kanji-data-{level}.js"
        if not path.exists():
            continue
        for entry in read_entries(path):
            km = re.search(r'kanji:"(.)"', entry)
            if not km:
                continue
            k = km.group(1)
            if k in main_entries:
                if main_entries[k] != entry:
                    main_entries[k] = entry
                    updated += 1
            else:
                main_entries[k] = entry
                added += 1

    log(f"Updated: {updated}, Added: {added}")

    if updated == 0 and added == 0:
        log("kanji-data.js đã đồng bộ", "✅")
        return False

    # Rebuild giữ thứ tự N5→N1
    all_levels_kanji = []
    for level in LEVEL_ORDER:
        path = JS / f"kanji-data-{level}.js"
        if not path.exists():
            continue
        for entry in read_entries(path):
            km = re.search(r'kanji:"(.)"', entry)
            if km:
                all_levels_kanji.append(km.group(1))

    ordered = []
    seen = set()
    for k in all_levels_kanji:
        if k not in seen and k in main_entries:
            ordered.append(main_entries[k])
            seen.add(k)
    for k, e in main_entries.items():
        if k not in seen:
            ordered.append(e)

    new_content = "window.KANJI_DATA = [\n"
    new_content += ',\n'.join(ordered)
    new_content += "\n];\nwindow.ALL_KANJI = window.KANJI_DATA;\n"

    backup(target)
    with open(target, 'w', encoding="utf-8") as f:
        f.write(new_content)

    log(f"kanji-data.js rebuilt: {len(ordered)} entries", "✅")
    return True


# ── Step 2: Bump version tags ─────────────────────────────────────────────

def bump_versions():
    """Cập nhật tất cả ?v= cache-buster thành ngày hôm nay."""
    section("Step 2 · Bump cache-buster ?v= tags")
    today = datetime.now().strftime("%Y%m%d")

    # Files có ?v= tags
    files_to_bump = [
        PROJECT / "kanji.html",
        PROJECT / "study.html",
        JS / "kanji-study.js",
    ]

    total = 0
    for fp in files_to_bump:
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8")
        new_text, n = re.subn(r'\?v=\d{8}[a-z]?', f'?v={today}', text)
        if n > 0:
            fp.write_text(new_text, encoding="utf-8")
            log(f"{fp.name}: {n} tags → ?v={today}")
            total += n
        else:
            log(f"{fp.name}: đã cập nhật", "○")

    if total == 0:
        log("Tất cả version tags đã đúng", "✅")
    else:
        log(f"Tổng: {total} tags đã bump", "✅")


# ── Step 3: Cập nhật study/index.html counts ─────────────────────────────

def update_study_index():
    """Đếm kanji + words thực tế, cập nhật study/index.html."""
    section("Step 3 · Cập nhật study/index.html")
    idx_path = PROJECT / "study" / "index.html"
    if not idx_path.exists():
        log("study/index.html không tồn tại, bỏ qua", "⚠")
        return

    # Đếm từ JS files
    counts = {}
    for lv in ["n5", "n4", "n3"]:
        text = (JS / f"kanji-data-{lv}.js").read_text(encoding="utf-8")
        kanji_n = len(re.findall(r'\{kanji:"', text))
        word_n = len(re.findall(r'"w":"', text))
        counts[lv] = (kanji_n, word_n)

    total_kanji = sum(v[0] for v in counts.values())

    html = idx_path.read_text(encoding="utf-8")
    changed = False

    # Update tổng
    html_new = re.sub(
        r'Tất cả \d+ kanji N5–N3',
        f'Tất cả {total_kanji} kanji N5–N3',
        html
    )
    if html_new != html:
        changed = True
    html = html_new

    # Update từng level card
    for lv, (kn, wn) in counts.items():
        level_upper = lv.upper()
        # Pattern: "103 kanji · ~309 từ mẫu"
        html_new = re.sub(
            rf'(\bhref="{lv}\.html".*?)\d+ kanji · ~\d+ từ mẫu',
            rf'\g<1>{kn} kanji · ~{wn} từ mẫu',
            html,
            flags=re.DOTALL
        )
        if html_new != html:
            changed = True
        html = html_new

    if changed:
        idx_path.write_text(html, encoding="utf-8")
        for lv, (kn, wn) in counts.items():
            log(f"{lv.upper()}: {kn} kanji · ~{wn} từ mẫu")
        log(f"Tổng: {total_kanji} kanji", "✅")
    else:
        log("study/index.html đã đúng", "✅")


# ── Step 4: Export Excel ──────────────────────────────────────────────────

def export_excel():
    """Gọi export_excel.py để sync Excel."""
    section("Step 4 · Export Excel")
    xlsx_path = PROJECT / "input" / "excel" / "kanji_KOERU_full.xlsx"
    try:
        sys.path.insert(0, str(PROJECT / "tools"))
        # Import và gọi trực tiếp thay vì subprocess
        from export_excel import main as export_main
        old_argv = sys.argv
        sys.argv = ["export_excel.py", str(xlsx_path)]
        export_main()
        sys.argv = old_argv
    except Exception as e:
        log(f"Export Excel lỗi: {e}", "⚠")
        log(f"Chạy thủ công: python tools/export_excel.py \"{xlsx_path}\"", "⚠")


# ── Step 5: Regenerate study HTML ─────────────────────────────────────────

def regen_study_html():
    """Gọi gen_study_html.py cho N5, N4, N3."""
    section("Step 5 · Regenerate study HTML (N5, N4, N3)")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT / "tools" / "gen_study_html.py"), "N5", "N4", "N3"],
            cwd=str(PROJECT),
            capture_output=True, text=True, timeout=120
        )
        # In output summary
        for line in result.stdout.split('\n'):
            if '✅' in line or 'Done' in line:
                print(f"  {line.strip()}")
        if result.returncode != 0 and result.stderr:
            log(f"stderr: {result.stderr[:200]}", "⚠")
    except Exception as e:
        log(f"Gen study HTML lỗi: {e}", "⚠")
        log("Chạy thủ công: python tools/gen_study_html.py N5 N4 N3", "⚠")


# ── Step 6: Data quality check ────────────────────────────────────────────

def run_quality_check():
    """Chạy koeru-data-check script."""
    checker = Path.home() / ".claude/skills/koeru-data-check/scripts/check_kanji_data.py"
    if not checker.exists():
        # Fallback: tìm trong project
        checker = PROJECT / ".claude" / "skills" / "koeru-data-check" / "scripts" / "check_kanji_data.py"
    if not checker.exists():
        log("Quality check script không tìm thấy, bỏ qua", "⚠")
        return
    section("Step 6 · Data Quality Check")
    result = subprocess.run(
        [sys.executable, str(checker), str(PROJECT)],
        capture_output=True, text=True
    )
    for line in result.stdout.split('\n'):
        if any(x in line for x in ['✅', '❌', 'TỔNG', '═══']):
            print(line)


# ── Step 7: Clean backups ─────────────────────────────────────────────────

def clean_backups():
    """Xóa .bak files cũ hơn 7 ngày."""
    removed = 0
    now = time.time()
    for pattern in ["*.*.bak", "*.xlsbak", "*.hvbak"]:
        for f in JS.glob(pattern):
            if now - f.stat().st_mtime > 7 * 86400:
                f.unlink()
                removed += 1
    # Cũng dọn backup ở root
    for f in PROJECT.glob("*.bak"):
        if now - f.stat().st_mtime > 7 * 86400:
            f.unlink()
            removed += 1
    if removed:
        log(f"Dọn {removed} file backup cũ", "🗑")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    t0 = time.time()

    print("\n🔨 KOERU Build")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    if "--check" in args:
        run_quality_check()
        return

    # Step 1: Sync data
    data_changed = sync_to_main()

    # Step 2: Bump versions (luôn chạy)
    bump_versions()

    if "--quick" in args:
        log("--quick: bỏ qua Excel + study HTML", "⏭")
        run_quality_check()
        clean_backups()
        print(f"\n  ⏱ Done in {time.time()-t0:.1f}s\n")
        return

    # Step 3: Update study/index.html counts
    update_study_index()

    # Step 4: Export Excel
    export_excel()

    # Step 5: Regenerate study HTML
    regen_study_html()

    # Step 6: Quality check
    run_quality_check()

    # Step 7: Clean
    clean_backups()

    elapsed = time.time() - t0
    print(f"\n  ⏱ Done in {elapsed:.1f}s")
    print(f"  ✅ Tất cả đã đồng bộ — chỉ cần git add + commit\n")


if __name__ == "__main__":
    main()
