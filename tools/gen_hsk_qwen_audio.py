"""Sinh audio HSK từ vựng + câu ví dụ bằng Qwen3-TTS chạy local.

Chạy bằng môi trường pilot đã cài Qwen:
  output/tts-pilot/venv/Scripts/python.exe tools/gen_hsk_qwen_audio.py

Kết quả staging nằm trong output/hsk-qwen-staging. Chạy lại sẽ tiếp tục từ
manifest và bỏ qua các MP3 đã vượt qua kiểm tra kỹ thuật.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "output" / "tts-pilot"
OUT = ROOT / "output" / "hsk-qwen-staging"
MANIFEST = OUT / "manifest.json"
os.environ["HF_HOME"] = str(PILOT / "hf-cache")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
sys.path.insert(0, str(ROOT / "tools"))

from gen_hsk_audio import load_texts

MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
MODEL_REVISION = "85e237c12c027371202489a0ec509ded67b5e4b5"
SPEAKER = "Serena"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Chỉ xử lý N mục đầu để kiểm thử")
    parser.add_argument("--dialogue", action="store_true",
                        help="Sinh thêm audio cho toàn bộ câu hội thoại")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "model": MODEL_ID,
        "revision": MODEL_REVISION,
        "speaker": SPEAKER,
        "dtype": "bfloat16",
        "status": "generating",
        "records": {},
    }


def save_manifest(report):
    temp = MANIFEST.with_suffix(".json.tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(MANIFEST)


def valid_existing(path, record):
    return (
        record
        and record.get("status") == "pass"
        and path.is_file()
        and path.stat().st_size == record.get("bytes")
        and path.stat().st_size > 1000
    )


def encode_mp3(samples, sample_rate, path):
    import lameenc
    import numpy as np

    pcm = np.clip(samples, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2").tobytes()
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(96)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    payload = encoder.encode(pcm) + encoder.flush()
    temp = path.with_suffix(".mp3.tmp")
    temp.write_bytes(payload)
    temp.replace(path)
    return payload


def main():
    args = parse_args()
    base_items = load_texts([1, 2, 3], None, args.dialogue, True)
    # key khác text cho chữ đa âm: giao diện chọn file theo pinyin của mục từ.
    items = [(text, text, label, None) for text, label in base_items]
    items.extend([
        ("长__zhang3", "长", "HSK3 · zhǎng · lớn lên",
         "Pronounce the Chinese character 长 as zhǎng, third tone. Speak only the character, clearly and naturally."),
        ("还__huan2", "还", "HSK3 · huán · trả lại",
         "Pronounce the Chinese character 还 as huán, second tone. Speak only the character, clearly and naturally."),
    ])
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit phải lớn hơn 0")
        items = items[:args.limit]
    if args.dry_run:
        print("Sẽ xử lý %d mục (%d ký tự)." %
              (len(items), sum(len(text) for _, text, _, _ in items)))
        return

    import numpy as np
    import torch
    from qwen_tts import Qwen3TTSModel

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; không chạy âm thầm bằng CPU.")

    OUT.mkdir(parents=True, exist_ok=True)
    report = load_manifest()
    records = report["records"]
    todo = [(key, text, label, instruct) for key, text, label, instruct in items
            if not valid_existing(OUT / (key + ".mp3"), records.get(key))]
    print("Tổng %d · đạt sẵn %d · cần sinh %d" % (len(items), len(items) - len(todo), len(todo)), flush=True)
    if not todo:
        report["status"] = "complete"
        save_manifest(report)
        return

    loaded_at = time.perf_counter()
    model = Qwen3TTSModel.from_pretrained(
        str(PILOT / "model"), device_map="cuda:0", dtype=torch.bfloat16,
        attn_implementation="sdpa", revision=MODEL_REVISION)
    print("Đã nạp model trong %.1fs · GPU %s" %
          (time.perf_counter() - loaded_at, torch.cuda.get_device_name()), flush=True)

    passed = failed = 0
    run_started = time.perf_counter()
    for index, (key, text, label, instruct) in enumerate(todo, 1):
        path = OUT / (key + ".mp3")
        started = time.perf_counter()
        try:
            seed = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16)
            torch.manual_seed(seed)
            torch.cuda.reset_peak_memory_stats()
            if text == "谢谢你" and not instruct:
                instruct = "Speak clearly in standard Mandarin with natural volume."
            wavs, sample_rate = model.generate_custom_voice(
                text=text, language="Chinese", speaker=SPEAKER,
                instruct=instruct,
                max_new_tokens=512, do_sample=False)
            samples = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
            duration = len(samples) / sample_rate
            peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
            finite = bool(np.isfinite(samples).all())
            if not finite or duration < 0.25 or peak < 0.005 or peak > 1.0:
                raise ValueError("waveform bất thường: finite=%s duration=%.3f peak=%.4f" %
                                 (finite, duration, peak))
            payload = encode_mp3(samples, sample_rate, path)
            if len(payload) <= 1000 or not payload.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
                path.unlink(missing_ok=True)
                raise ValueError("MP3 không hợp lệ (%d bytes)" % len(payload))
            elapsed = time.perf_counter() - started
            records[key] = {
                "key": key, "text": text, "label": label, "file": path.name, "status": "pass",
                "duration_seconds": round(duration, 3), "generation_seconds": round(elapsed, 2),
                "peak_amplitude": round(peak, 6), "sample_rate": sample_rate,
                "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "peak_vram_mib": round(torch.cuda.max_memory_allocated() / 1024**2),
            }
            passed += 1
            print("[%d/%d] OK  %.1fs  %s" % (index, len(todo), elapsed, text), flush=True)
        except Exception as exc:
            records[key] = {"key": key, "text": text, "label": label,
                            "status": "error", "error": str(exc)}
            failed += 1
            print("[%d/%d] ERR %s — %s" % (index, len(todo), text, exc), flush=True)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        report["status"] = "generating"
        report["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        save_manifest(report)

    report["status"] = "complete" if failed == 0 else "completed_with_errors"
    report["summary"] = {
        "requested": len(items), "passed": sum(r.get("status") == "pass" for r in records.values()),
        "failed_this_run": failed, "run_seconds": round(time.perf_counter() - run_started, 1),
    }
    save_manifest(report)
    print("Xong lượt chạy: đạt %d · lỗi %d · %s" % (passed, failed, MANIFEST), flush=True)


if __name__ == "__main__":
    main()
