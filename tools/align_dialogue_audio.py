"""
Cắt audio hội thoại (会話) từ file CD gốc Minna no Nihongo thành từng lượt thoại,
khớp với `lines[]` trong database/dialogue/n4|n5/lessonNN.json.

Cách làm: chuyển CD sang wav 16k -> Google Speech-to-Text (có word time offsets)
-> difflib khớp transcript STT với text JP mong đợi -> tinh chỉnh điểm cắt về
chỗ im lặng nhất -> xuất mp3 từng dòng bằng ffmpeg.

Khác với tools/gen_dialogue_audio.py (sinh giọng TTS máy): script này dùng
giọng đọc THẬT từ CD, nên cần file CD gốc và tốn quota STT.

Cần:
  GOOGLE_STT_API_KEY   API key Google Speech-to-Text
  MINNA_CD_DIR         thư mục chứa mp3 CD (tên file có "kaiwa" + "Bài <số>")
                       mặc định trỏ tới thư mục CD trong PROJECT/jlpt-lesson-generator
  ffmpeg / ffprobe     có trong PATH
  pip install requests pydub

Chạy:
  GOOGLE_STT_API_KEY=xxx python tools/align_dialogue_audio.py                 # tất cả bài
  GOOGLE_STT_API_KEY=xxx python tools/align_dialogue_audio.py n5              # cả cấp N5
  GOOGLE_STT_API_KEY=xxx python tools/align_dialogue_audio.py n5 lesson3      # 1 bài

Output: audio/_aligned/<n4|n5>/lesson<N>_<01,02,...>.mp3 — thư mục CHỜ DUYỆT,
không ghi thẳng vào audio/dialogue/. Nghe kiểm tra (xem
tools/verify_dialogue_cuts.py) rồi mới chép sang audio/dialogue/<lv>/.

Dòng nào cắt ra bị nghi sai (quá ngắn/dài so với số chữ, hoặc nội dung STT
không khớp) sẽ bị BỎ QUA thay vì xuất file rác — xem `bad_ratio=` ở output.
"""
import base64
import difflib
import json
import os
import re
import statistics
import subprocess
import sys
import unicodedata

# requests / pydub được import muộn (trong hàm dùng tới) để các kiểm tra tiền đề
# ở main() — thiếu API key, thiếu thư mục CD — báo lỗi rõ ràng trước, thay vì
# chết bằng ModuleNotFoundError ngay lúc nạp file.

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, "database", "dialogue")
OUT_DIR = os.path.join(ROOT, "audio", "_aligned")

DEFAULT_CD_DIR = os.path.join(
    "C:\\Users\\hoang\\Desktop\\PROJECT\\jlpt-lesson-generator\\input\\pdf\\N4",
    "Tài liệu nghe đầy đủ mina no nihongo-20260726T021607Z-1-001",
    "Tài liệu nghe đầy đủ mina no nihongo",
)
CD_DIR = os.environ.get("MINNA_CD_DIR") or DEFAULT_CD_DIR

KEY_STT = os.environ.get("GOOGLE_STT_API_KEY")
SIM_THRESHOLD = 0.55


def index_cd_files():
    """Map số bài -> đường dẫn mp3 CD (chỉ lấy file có 'kaiwa' trong tên)."""
    files_by_num = {}
    for f in os.listdir(CD_DIR):
        fn = unicodedata.normalize("NFC", f)
        if "kaiwa" not in fn.lower():
            continue
        m = re.match(r"Bài\s*(\d+)\s*[-–]", fn) or re.match(r"Bài\s*(\d+)", fn)
        if m:
            files_by_num[int(m.group(1))] = os.path.join(CD_DIR, f)
    return files_by_num


def strip_text(s):
    s = re.sub(r"\[[^\]]*\]", "", s or "")
    s = re.sub(r"[。、？！\s　……「」]", "", s)
    return s


def to_wav16k(src_path, wav_path):
    subprocess.run(["ffmpeg", "-y", "-i", src_path, "-ac", "1", "-ar", "16000", wav_path],
                    capture_output=True, check=True)


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                          capture_output=True, text=True)
    return float(out.stdout.strip())


def stt_sync_wav(wav_path):
    import requests

    with open(wav_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    body = {
        "config": {"encoding": "LINEAR16", "sampleRateHertz": 16000, "audioChannelCount": 1,
                   "languageCode": "ja-JP", "enableWordTimeOffsets": True, "model": "latest_long"},
        "audio": {"content": content},
    }
    r = requests.post(f"https://speech.googleapis.com/v1/speech:recognize?key={KEY_STT}", json=body, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return r.json()


def get_words_for_lesson(mp3_path):
    wav_full = mp3_path + ".16k.wav"
    to_wav16k(mp3_path, wav_full)
    dur = duration_of(wav_full)
    words = []
    if dur <= 55:
        resp = stt_sync_wav(wav_full)
        for r in resp.get("results", []):
            for w in r["alternatives"][0].get("words", []):
                words.append({"word": w["word"], "start": float(w["startTime"].rstrip("s")),
                               "end": float(w["endTime"].rstrip("s"))})
    else:
        chunk_len, overlap, t = 50, 2, 0
        while t < dur:
            seg_path = mp3_path + f".seg{t}.wav"
            subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-t", str(chunk_len + overlap), "-i", wav_full,
                             "-ac", "1", "-ar", "16000", seg_path], capture_output=True, check=True)
            resp = stt_sync_wav(seg_path)
            for r in resp.get("results", []):
                for w in r["alternatives"][0].get("words", []):
                    ws = float(w["startTime"].rstrip("s")) + t
                    we = float(w["endTime"].rstrip("s")) + t
                    if not words or ws > words[-1]["start"] + 0.05:
                        words.append({"word": w["word"], "start": ws, "end": we})
            os.remove(seg_path)
            t += chunk_len
    os.remove(wav_full)
    return words


def content_similarity(words, expected_lines):
    stt_text = "".join(w["word"] for w in words)
    expected_text = "".join(strip_text(l["jp"]) for l in expected_lines)
    return difflib.SequenceMatcher(None, expected_text, stt_text).ratio()


def align_lines(words, expected_lines):
    stt_text = "".join(w["word"] for w in words)
    char_to_word, word_char_start = [], []
    pos = 0
    for wi, w in enumerate(words):
        word_char_start.append(pos)
        char_to_word.extend([wi] * len(w["word"]))
        pos += len(w["word"])

    expected_full = "".join(strip_text(l["jp"]) for l in expected_lines)
    sm = difflib.SequenceMatcher(None, expected_full, stt_text)
    blocks = sm.get_matching_blocks()

    def expected_pos_to_stt_pos(p):
        best = None
        for b in blocks:
            if b.size == 0:
                continue
            if b.a <= p <= b.a + b.size:
                return b.b + (p - b.a)
            if best is None or abs(b.a - p) < abs(best.a - p):
                best = b
        if best is None:
            return None
        return max(0, min(len(stt_text) - 1, best.b + (p - best.a)))

    cuts = [0.0]
    cum = 0
    for line in expected_lines[:-1]:
        cum += len(strip_text(line["jp"]))
        spos = expected_pos_to_stt_pos(cum)
        if spos is None or not words:
            cuts.append(cuts[-1])
            continue
        wi = char_to_word[min(spos, len(char_to_word) - 1)] if char_to_word else 0
        wi = min(wi, len(words) - 1)
        if spos <= word_char_start[wi] and wi > 0:
            end_t, next_start = words[wi - 1]["end"], words[wi]["start"]
        else:
            end_t = words[wi]["end"]
            next_start = words[wi + 1]["start"] if wi + 1 < len(words) else end_t + 0.3
        cuts.append((end_t + next_start) / 2)
    total_dur = words[-1]["end"] + 0.5 if words else cuts[-1] + 1
    cuts.append(total_dur)
    return list(zip(cuts[:-1], cuts[1:]))


def silence_run_after(audio, t, max_extra=0.5, step_ms=20, thresh_offset=16):
    """Tu diem t (giay), keo dai ve sau CHI TRONG VUNG THUC SU IM LANG,
    tranh de padding lan sang cau ke tiep khi 2 cau lien mach khong co khoang lang."""
    thresh = audio.dBFS - thresh_offset
    start_ms = int(t * 1000)
    max_ms = min(len(audio), start_ms + int(max_extra * 1000))
    ms = start_ms
    while ms < max_ms:
        seg = audio[ms:ms + step_ms]
        db = seg.dBFS if seg.dBFS != float("-inf") else -120
        if db > thresh:  # het im lang, dung lai ngay truoc do
            break
        ms += step_ms
    return ms / 1000.0


def silence_run_before(audio, t, max_extra=0.3, step_ms=20, thresh_offset=16):
    """Tu diem t (giay), lui ve TRUOC chi trong vung thuc su im lang,
    tranh cat hut dau tu dau cau."""
    thresh = audio.dBFS - thresh_offset
    start_ms = int(t * 1000)
    min_ms = max(0, start_ms - int(max_extra * 1000))
    ms = start_ms
    while ms > min_ms:
        seg = audio[max(0, ms - step_ms):ms]
        db = seg.dBFS if seg.dBFS != float("-inf") else -120
        if db > thresh:
            break
        ms -= step_ms
    return ms / 1000.0


def refine_cut_point(audio, t, window=0.45, step_ms=20):
    center_ms = int(t * 1000)
    lo = max(0, center_ms - int(window * 1000))
    hi = min(len(audio), center_ms + int(window * 1000))
    best_ms, best_db = center_ms, 999
    ms = lo
    while ms < hi:
        seg = audio[ms:ms + step_ms]
        db = seg.dBFS if seg.dBFS != float("-inf") else -120
        if db < best_db:
            best_db, best_ms = db, ms + step_ms // 2
        ms += step_ms
    return best_ms / 1000.0


def process_lesson(level, lesson, files_by_num):
    from pydub import AudioSegment

    json_path = os.path.join(DB_DIR, level, f"lesson{lesson:02d}.json")
    if not os.path.exists(json_path):
        return ("NO_JSON", None)
    d = json.load(open(json_path, encoding="utf-8"))
    lines = d["lines"]
    mp3 = files_by_num.get(lesson)
    if not mp3:
        return ("NO_CD", None)

    words = get_words_for_lesson(mp3)
    if not words:
        return ("NO_WORDS", None)

    sim = content_similarity(words, lines)
    if sim < SIM_THRESHOLD:
        return ("CONTENT_MISMATCH", sim)

    title_line = {"jp": "会話" + (d.get("title") or "")}
    lines_ext = [title_line] + lines
    segs = align_lines(words, lines_ext)[1:]

    wav_full = mp3 + ".16k.wav"
    to_wav16k(mp3, wav_full)
    full_audio = AudioSegment.from_wav(wav_full)
    os.remove(wav_full)

    raw_cuts = [segs[0][0]] + [segs[i][1] for i in range(len(segs) - 1)] + [segs[-1][1]]
    refined = [raw_cuts[0]]
    for c in raw_cuts[1:-1]:
        refined.append(refine_cut_point(full_audio, c))
    refined.append(raw_cuts[-1] + 0.4)

    # kiem tra do dai am thanh vs do dai van ban truoc khi xuat -
    # phat hien dong bi loi diem cat (am/qua ngan so voi noi dung)
    durs = [(refined[i + 1] - refined[i]) for i in range(len(lines))]
    chars = [max(1, len(strip_text(lines[i]["jp"]))) for i in range(len(lines))]
    rates = [d / c for d, c in zip(durs, chars) if d > 0]
    med_rate = statistics.median(rates) if rates else 0.15

    # doi chieu NOI DUNG tung dong (khong chi ca bai) - bat cac truong hop
    # lech noi dung cuc bo (vd ban CD khac edition o 1 doan giua bai) ma
    # kiem tra tong the ca bai khong phat hien duoc
    def line_content_ok(i):
        s, e = refined[i], refined[i + 1]
        seg_words = [w["word"] for w in words if s - 0.3 <= w["start"] < e + 0.3]
        seg_text = "".join(seg_words)
        exp_text = strip_text(lines[i]["jp"])
        if not exp_text or not seg_text:
            return True  # khong du du lieu de danh gia, khong chan
        r = difflib.SequenceMatcher(None, exp_text, seg_text).ratio()
        return r >= 0.4

    out_dir = os.path.join(OUT_DIR, level)
    os.makedirs(out_dir, exist_ok=True)
    fail_lines, skipped_bad = [], []
    for i in range(len(lines)):
        s, e = refined[i], refined[i + 1]
        dur = e - s
        rate = dur / chars[i] if dur > 0 else 0
        ratio = rate / med_rate if med_rate else 0
        if dur <= 0 or ratio < 0.3 or ratio > 3.5 or not line_content_ok(i):
            skipped_bad.append(i + 1)
            continue
        start_pad = silence_run_before(full_audio, s, max_extra=0.3)
        end_pad = silence_run_after(full_audio, e, max_extra=0.5)
        out_path = os.path.join(out_dir, f"lesson{lesson}_{i+1:02d}.mp3")
        r = subprocess.run(
            ["ffmpeg", "-y", "-i", mp3, "-ss", str(max(0, start_pad)), "-to", str(end_pad), out_path],
            capture_output=True,
        )
        if r.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) < 500:
            fail_lines.append(i + 1)
    if fail_lines or skipped_bad:
        return (f"OK_SOME_SKIPPED fail={fail_lines} bad_ratio={skipped_bad}", sim)
    return ("OK", sim)


def _has_module(name):
    import importlib.util

    return importlib.util.find_spec(name) is not None


def parse_args(argv):
    """[n4|n5] [lessonN] — cùng convention với gen_vocab_audio.py / gen_dialogue_audio.py."""
    level, lesson = None, None
    for a in argv:
        al = a.lower()
        if al in ("n4", "n5"):
            level = al
        else:
            m = re.fullmatch(r"lesson(\d+)", al) or re.fullmatch(r"(\d+)", al)
            if m:
                lesson = int(m.group(1))
            else:
                sys.exit(f"Tham số không hiểu: {a!r}. Dùng: [n4|n5] [lessonN]")
    return level, lesson


def main():
    if not KEY_STT:
        sys.exit(
            "Thiếu GOOGLE_STT_API_KEY.\n"
            "  Lấy key tại https://console.cloud.google.com/apis/credentials (bật Speech-to-Text API)\n"
            "  PowerShell: $env:GOOGLE_STT_API_KEY='xxx'; python tools/align_dialogue_audio.py n5 lesson3"
        )
    if not os.path.isdir(CD_DIR):
        sys.exit(
            f"Không thấy thư mục CD: {CD_DIR}\n"
            "  Đặt biến MINNA_CD_DIR trỏ tới thư mục chứa mp3 CD Minna."
        )

    missing = [m for m in ("requests", "pydub") if not _has_module(m)]
    if missing:
        sys.exit(f"Thiếu thư viện: {', '.join(missing)}\n  pip install {' '.join(missing)}")

    level, lesson = parse_args(sys.argv[1:])
    files_by_num = index_cd_files()
    if not files_by_num:
        sys.exit(f"Không thấy file CD nào có 'kaiwa' trong tên tại: {CD_DIR}")

    targets = [("n5", n) for n in range(1, 26)] + [("n4", n) for n in range(27, 51)]
    if level:
        targets = [t for t in targets if t[0] == level]
    if lesson is not None:
        targets = [t for t in targets if t[1] == lesson]
    if not targets:
        sys.exit("Không có bài nào khớp bộ lọc (N5 = bài 1-25, N4 = bài 27-50).")

    results = []
    for lv, ls in targets:
        status, sim = process_lesson(lv, ls, files_by_num)
        simtxt = f"{sim:.3f}" if sim is not None else "-"
        print(f"{status:18s} {lv} bai {ls:2d}  sim={simtxt}")
        results.append((lv, ls, status, sim))
        sys.stdout.flush()

    print("\n=== TONG KET ===")
    for st in ("OK", "CONTENT_MISMATCH", "NO_CD", "NO_JSON", "NO_WORDS"):
        items = [r for r in results if r[2] == st]
        print(f"{st}: {len(items)}  ->", [(r[0], r[1]) for r in items])
    print(f"\nFile cắt ra nằm ở: {OUT_DIR}")
    print("Nghe kiểm tra rồi mới chép sang audio/dialogue/<lv>/ — script này KHÔNG tự ghi đè.")


if __name__ == "__main__":
    main()
