---
name: minna-audio
description: Sinh, cắt và kiểm tra audio cho app Minna (minna.html) — TTS từ vựng, TTS hội thoại, cắt audio từ CD gốc, verify chất lượng file đã cắt. Dùng khi người dùng nói "sinh audio", "tạo TTS", "làm audio bài X", "audio hội thoại", "cắt audio CD", "align audio", "kiểm tra audio", "audio bị lệch", "audio sai/thiếu", hoặc sau khi thêm từ vựng/hội thoại mới cần audio đi kèm.
---

# Minna Audio — pipeline audio cho minna.html

Toàn bộ logic đã nằm trong `tools/`. Skill này **chỉ điều phối**: chọn đúng luồng,
chạy đúng thứ tự, dừng lại cho người dùng duyệt. Không viết thêm script mới.

## Context

- **Root**: `C:\Users\hoang\Desktop\BUILD WEB KOERU`
- **Branch**: `dev`
- Nguồn dữ liệu: `database/n4|n5/lessonNN.json` (từ vựng), `database/dialogue/n4|n5/lessonNN.json` (hội thoại)
- Tên file audio là **hợp đồng ngầm** với hàm dò audio trong `minna.html` — không được đổi.
- Không có file audio thật thì `minna.html` tự fallback sang giọng đọc trình duyệt. Nghĩa là **thiếu audio không phải lỗi chặn**, đừng vội sinh bừa.

## Bước 0 — Xác định luồng

Hỏi/suy ra từ yêu cầu người dùng để chọn đúng 1 trong 4 luồng dưới. Nếu mơ hồ, hỏi trước khi chạy — mỗi luồng tốn quota API khác nhau.

| Người dùng muốn | Luồng |
|---|---|
| Audio cho từ vựng mới | 1 |
| Audio hội thoại, chấp nhận giọng máy | 2 |
| Audio hội thoại giọng thật, có file CD | 3 → bắt buộc 4 |
| Nghi audio hiện tại bị lệch/cắt sai | 4 |

---

## Luồng 1 — TTS từ vựng

```bash
python tools/gen_vocab_audio.py [n4|n5] [lessonN]
```

- **Cần** `GOOGLE_TTS_API_KEY` (giọng Neural2). PowerShell: `$env:GOOGLE_TTS_API_KEY='xxx'`
- Output: `audio/vocab/<kana thuần>.mp3`
- Script tự dedup toàn N4+N5 và **skip file đã có** → chạy lại an toàn, không sợ trùng.
- Bỏ hết tham số = sinh cho tất cả bài. Chỉ làm vậy khi người dùng yêu cầu rõ (tốn quota lớn).

## Luồng 2 — TTS hội thoại

```bash
python tools/gen_dialogue_audio.py [n4|n5] [lessonN]                    # soundoftext, KHÔNG cần key
python tools/gen_dialogue_audio.py --engine google [n4|n5] [lessonN]    # cần GOOGLE_TTS_API_KEY
```

- Mặc định engine `soundoftext`: không cần key, giọng ja-JP đơn, **không phân biệt nhân vật**.
- `--engine google`: mỗi nhân vật một giọng nam/nữ riêng, tự nhiên hơn — dùng khi hội thoại có từ 2 nhân vật rõ rệt.
- Output: `audio/dialogue/<n4|n5>/lesson<N>_<01,02,...>.mp3` (1 file / lượt thoại, đánh số theo thứ tự `lines[]`).

## Luồng 3 — Cắt audio từ CD gốc

```bash
python tools/align_dialogue_audio.py [n4|n5] [lessonN]
```

- **Cần** `GOOGLE_STT_API_KEY` + `MINNA_CD_DIR` (thư mục mp3 CD) + `ffmpeg`/`ffprobe` + `pip install requests pydub`.
  Script kiểm tra đủ 3 tiền đề này và báo lỗi rõ ràng nếu thiếu — đọc thông báo, đừng đoán.
- Output vào **thư mục chờ duyệt** `audio/_aligned/<lv>/`, **không** ghi thẳng vào `audio/dialogue/`.
- Đọc cột trạng thái ở output:
  - `OK` — cắt trọn bài
  - `OK_SOME_SKIPPED fail=[...] bad_ratio=[...]` — có dòng bị bỏ vì nghi cắt sai; **báo lại danh sách dòng này cho người dùng**
  - `CONTENT_MISMATCH` — bản CD không khớp transcript trong JSON (khác edition). **Không** cố ép chạy tiếp; báo người dùng kiểm tra lại nguồn CD.
  - `NO_CD` / `NO_JSON` / `NO_WORDS` — thiếu đầu vào, nêu rõ thiếu cái gì.
- Chạy xong **bắt buộc** sang luồng 4 với cờ `--staging`, rồi mới chép sang `audio/dialogue/`. Việc chép do người dùng quyết định sau khi nghe.

## Luồng 4 — Verify

```bash
python tools/verify_dialogue_cuts.py [n4|n5] [lessonN]              # soát audio/dialogue/
python tools/verify_dialogue_cuts.py --staging [n4|n5] [lessonN]    # soát audio/_aligned/
```

- Đối chiếu độ dài mp3 với số ký tự thoại thật; dòng nào lệch xa trung vị tốc độ đọc của chính bài đó thì bị nêu tên.
- Exit code 1 nếu có dòng bất thường — đây là **cảnh báo, không phải lỗi**. Script không tự sửa gì.
- Báo lại cho người dùng danh sách dòng nghi ngờ kèm gợi ý nghe thử; không tự xoá hay tự sinh lại.

---

## Bước cuối — bump cache & dừng

```bash
python tools/bump_cache.py
git status --short
```

- `bump_cache.py` băm md5 nội dung file, idempotent — **không tự gõ `?v=YYYYMMDD` bằng tay**.
- In `git status --short`, tóm tắt: đã sinh bao nhiêu file audio mới, luồng nào, dòng nào bị cảnh báo.
- **DỪNG Ở ĐÂY. Không commit.** Nhắc người dùng nghe thử vài file rồi tự chốt commit.

## Không làm

- Không sửa `database/**/*.json` — phạm vi skill này chỉ là audio. Sai transcript thì báo, để `minna-lesson` hoặc `minna-dialogue` xử lý.
- Không đổi tên file audio, không đổi quy ước đánh số.
- Không ghi đè file audio đã tồn tại trừ khi người dùng yêu cầu rõ.
- Không chép `audio/_aligned/` sang `audio/dialogue/` khi chưa verify và chưa được người dùng đồng ý.
- Không chạy toàn bộ N4+N5 (bỏ hết tham số) nếu người dùng chỉ nhắc tới một bài — tốn quota vô ích.
- Không commit.
