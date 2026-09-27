"""Đưa audio Qwen đã đạt kiểm tra kỹ thuật từ staging vào audio/hsk."""
import json
import shutil
from pathlib import Path

from gen_hsk_audio import load_texts

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "output" / "hsk-qwen-staging"
DEST = ROOT / "audio" / "hsk"
VARIANT_KEYS = ("长__zhang3", "还__huan2")


def main():
    manifest_path = STAGING / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records", {})
    required = [text for text, _ in load_texts([1, 2, 3], None, True, True)]
    required.extend(VARIANT_KEYS)
    missing = []
    ready = []
    for key in required:
        record = records.get(key, {})
        source = STAGING / record.get("file", "")
        if (record.get("status") != "pass" or not source.is_file()
                or source.stat().st_size != record.get("bytes")
                or source.stat().st_size <= 1000):
            missing.append(key)
        else:
            ready.append((key, record, source))
    if missing:
        raise SystemExit("Chưa thể đồng bộ; thiếu/lỗi %d mục: %s" %
                         (len(missing), " · ".join(missing[:20])))

    DEST.mkdir(parents=True, exist_ok=True)
    promoted = {}
    for key, record, source in ready:
        target = DEST / record["file"]
        shutil.copy2(source, target)
        promoted[key] = record
    release = {
        "engine": manifest.get("model"),
        "revision": manifest.get("revision"),
        "speaker": manifest.get("speaker"),
        "status": "technical_qa_passed_pronunciation_review_pending",
        "count": len(promoted),
        "records": promoted,
    }
    (DEST / "qwen-manifest.json").write_text(
        json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Đã đồng bộ %d file Qwen vào %s" % (len(promoted), DEST))


if __name__ == "__main__":
    main()
