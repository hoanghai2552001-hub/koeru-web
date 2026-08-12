"""
Cắt 1 file audio ghi âm nguyên đoạn hội thoại (vd file CD gốc, hoặc bạn tự thu)
thành từng câu riêng theo đúng quy ước audio/dialogue/<n4|n5>/lesson<N>_<01,02>.mp3
mà minna.html đã tự dò sẵn.

Cách hoạt động: tách theo khoảng lặng (silence) giữa các lượt thoại — xử lý
hoàn toàn cục bộ bằng ffmpeg/pydub, KHÔNG cần mạng ngoài (khác với
gen_dialogue_audio.py cần gọi API TTS).

Yêu cầu: ffmpeg (`apt install ffmpeg`), pydub (`pip install pydub`).

Chạy:
  python tools/split_dialogue_audio.py <file_audio_goc> n4 lesson27

Script sẽ:
  1. Tách audio theo khoảng lặng
  2. So số đoạn tách được với số câu (`lines[]`) trong
     database/dialogue/n4/lesson27.json — nếu KHÔNG khớp, in cảnh báo và
     lưu vào thư mục review/ để bạn tự nghe kiểm tra thay vì ghi đè luôn
     (tách sai ranh giới câu rất dễ xảy ra nếu diễn viên ngừng giữa câu dài,
     hoặc nói liền 2 câu không nghỉ).
  3. Nếu khớp số lượng, lưu thẳng vào audio/dialogue/<level>/lessonN_01.mp3,
     _02.mp3, ...

Tinh chỉnh nếu tách sai (quá nhiều/quá ít đoạn):
  --min-silence-ms   độ dài khoảng lặng tối thiểu để coi là ranh giới câu
                      (mặc định 600ms — giảm nếu diễn viên nói nhanh/ít nghỉ,
                      tăng nếu 1 câu bị tách làm 2 vì có dấu phẩy/ngập ngừng)
  --silence-thresh-db độ chênh so với âm lượng trung bình để coi là "lặng"
                      (mặc định -16dB — giảm giá trị tuyệt đối nếu file ồn/
                      có nhạc nền làm sót ranh giới)
"""
import argparse
import glob
import io
import json
import os

from pydub import AudioSegment
from pydub.silence import split_on_silence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, "database", "dialogue")
OUT_DIR = os.path.join(ROOT, "audio", "dialogue")
REVIEW_DIR = os.path.join(ROOT, "audio", "dialogue", "_review")


def load_lesson(level, lesson_num):
    path = os.path.join(DB_DIR, level, f"lesson{lesson_num}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy {path} — bài này chưa có data hội thoại.")
    return json.load(io.open(path, encoding="utf-8"))


def split_audio(audio_path, min_silence_ms, silence_thresh_db):
    audio = AudioSegment.from_file(audio_path)
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_ms,
        silence_thresh=audio.dBFS + silence_thresh_db,
        keep_silence=150,
    )
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_file", help="File audio gốc (mp3/wav/m4a...) chứa nguyên đoạn hội thoại")
    ap.add_argument("level", choices=["n4", "n5"])
    ap.add_argument("lesson", help="vd: lesson27")
    ap.add_argument("--min-silence-ms", type=int, default=600)
    ap.add_argument("--silence-thresh-db", type=int, default=-16)
    args = ap.parse_args()

    lesson_num = int(args.lesson.replace("lesson", ""))
    d = load_lesson(args.level, lesson_num)
    expected = len(d["lines"])

    print(f"Bài {lesson_num} ({args.level}) — kỳ vọng {expected} câu thoại.")
    print("Đang tách audio theo khoảng lặng...")
    chunks = split_audio(args.audio_file, args.min_silence_ms, args.silence_thresh_db)
    print(f"Tách được {len(chunks)} đoạn.")

    if len(chunks) == expected:
        out_dir = os.path.join(OUT_DIR, args.level)
        os.makedirs(out_dir, exist_ok=True)
        for i, chunk in enumerate(chunks):
            out_path = os.path.join(out_dir, f"lesson{lesson_num}_{i+1:02d}.mp3")
            chunk.export(out_path, format="mp3")
            spk = d["lines"][i].get("spk", "")
            print(f"  ✓  lesson{lesson_num}_{i+1:02d}.mp3  ({len(chunk)}ms, {spk}: {d['lines'][i]['jp'][:20]}...)")
        print(f"\nKHỚP số câu — đã lưu vào {out_dir}/")
    else:
        out_dir = os.path.join(REVIEW_DIR, args.level, f"lesson{lesson_num}")
        os.makedirs(out_dir, exist_ok=True)
        for i, chunk in enumerate(chunks):
            chunk.export(os.path.join(out_dir, f"part_{i+1:02d}.mp3"), format="mp3")
        print(f"\n⚠ KHÔNG khớp: tách được {len(chunks)} đoạn nhưng bài có {expected} câu.")
        print(f"Đã lưu {len(chunks)} đoạn thô vào {out_dir}/ để bạn tự nghe đối chiếu —")
        print("KHÔNG ghi vào audio/dialogue/ để tránh gán sai câu.")
        print("Thử chỉnh --min-silence-ms (tăng nếu quá nhiều đoạn, giảm nếu quá ít) rồi chạy lại.")


if __name__ == "__main__":
    main()
