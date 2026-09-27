# -*- coding: utf-8 -*-
"""Áp dụng gói xuất từ hsk-teacher-qa.html vào database và audio HSK.

Usage:
  python tools/apply_hsk_teacher_qa.py path/to/koeru-hsk-qa.json --dry-run
  python tools/apply_hsk_teacher_qa.py path/to/koeru-hsk-qa.json
"""
import argparse, base64, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS = ROOT / "database" / "hsk_corrections.json"
AUDIO_DIR = ROOT / "audio" / "hsk"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    if bundle.get("schema") != "koeru-hsk-teacher-qa-v1":
        raise SystemExit("Sai schema: cần koeru-hsk-teacher-qa-v1")
    corrections = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
    accepted = [r for r in bundle.get("records", []) if r.get("status") == "approved"]
    conflicts, seen = [], {}
    for row in accepted:
        token = (row["level"], row["h"])
        values = (row.get("p", ""), row.get("m", ""), row.get("hv", ""))
        if token in seen and seen[token] != values:
            conflicts.append("HSK%d %s" % token)
        seen[token] = values
    if conflicts:
        raise SystemExit("Có chỉnh sửa mâu thuẫn: " + ", ".join(sorted(set(conflicts))))
    print("Gói QA: %d mục · %d mục đạt · %d bản thu" % (len(bundle.get("records", [])), len(accepted), sum(bool(r.get("audio")) for r in accepted)))
    if args.dry_run:
        return
    ffmpeg = shutil.which("ffmpeg")
    for row in accepted:
        level_key = "HSK%d" % row["level"]
        patch = corrections.setdefault(level_key, {}).setdefault(row["h"], {})
        for field in ("p", "m", "hv", "note"):
            if field in row:
                patch[field] = str(row.get(field, "")).strip()
        patch["why"] = "Giáo viên QA: %s · %s" % (row.get("reviewer") or bundle.get("reviewer") or "không ghi tên", row.get("reviewed_at", ""))
        audio = row.get("audio")
        if not audio:
            continue
        raw = base64.b64decode(audio["base64"])
        output = AUDIO_DIR / ((row.get("audio_key") or row["h"]) + ".mp3")
        mime = audio.get("mime", "")
        if "mpeg" in mime or "mp3" in mime:
            output.write_bytes(raw)
        else:
            if not ffmpeg:
                raise SystemExit("Cần ffmpeg để chuyển bản thu %s sang MP3" % row["h"])
            suffix = ".ogg" if "ogg" in mime else ".webm"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
                handle.write(raw); source = Path(handle.name)
            try:
                subprocess.run([ffmpeg, "-y", "-v", "error", "-i", str(source), "-ac", "1", "-ar", "24000", "-b:a", "96k", str(output)], check=True)
            finally:
                source.unlink(missing_ok=True)
    CORRECTIONS.write_text(json.dumps(corrections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_hsk_data.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(ROOT / "tools" / "bump_cache.py")], check=True, cwd=ROOT)
    print("Đã áp dụng gói QA. Chạy tools/qa_hsk_content.py trước khi commit.")

if __name__ == "__main__":
    main()
