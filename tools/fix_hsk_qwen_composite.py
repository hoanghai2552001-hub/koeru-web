"""Tạo mục Qwen ngắn bị im lặng bằng cách ghép các âm đã kiểm tra."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from gen_hsk_qwen_audio import encode_mp3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "hsk-qwen-staging"
MANIFEST = OUT / "manifest.json"


def trimmed(path, threshold=0.004):
    samples, rate = sf.read(path, dtype="float32")
    samples = np.asarray(samples, dtype=np.float32).reshape(-1)
    active = np.flatnonzero(np.abs(samples) >= threshold)
    if not len(active):
        raise ValueError("Audio nguồn không có tín hiệu: %s" % path.name)
    start = max(0, int(active[0]) - int(rate * 0.02))
    end = min(len(samples), int(active[-1]) + int(rate * 0.04))
    return samples[start:end], rate


def main():
    first, rate = trimmed(OUT / "谢谢.mp3")
    second, second_rate = trimmed(OUT / "你.mp3")
    if second_rate != rate:
        raise ValueError("Sample rate nguồn không khớp")
    pause = np.zeros(int(rate * 0.06), dtype=np.float32)
    samples = np.concatenate([first, pause, second])
    target = OUT / "谢谢你.mp3"
    payload = encode_mp3(samples, rate, target)
    peak = float(np.max(np.abs(samples)))
    if len(payload) <= 1000 or peak < 0.005:
        raise ValueError("Audio ghép không đạt kiểm tra kỹ thuật")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["records"]["谢谢你"] = {
        "key": "谢谢你",
        "text": "谢谢你",
        "label": "HSK1 bài 2 · ví dụ",
        "file": target.name,
        "status": "pass",
        "method": "qwen_composite",
        "composite_from": ["谢谢", "你"],
        "duration_seconds": round(len(samples) / rate, 3),
        "peak_amplitude": round(peak, 6),
        "sample_rate": rate,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    manifest["status"] = "complete"
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Đã tạo %s · %.2fs · peak %.3f" %
          (target.name, len(samples) / rate, peak))


if __name__ == "__main__":
    main()
