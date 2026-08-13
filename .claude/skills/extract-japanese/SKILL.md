---
name: extract-japanese
description: >
  Extract Japanese vocabulary, Kanji, grammar patterns, and example sentences
  from PDF files or images (photos of textbook pages, grammar books, flashcard
  scans, manga pages, etc.) and push the results into the Koeru Kanji app or
  Google Sheet.

  ALWAYS use this skill when the user:
  - uploads or mentions a PDF/image of a Japanese textbook, grammar book, or study material
  - asks to "extract kanji", "lấy từ vựng", "trích xuất ngữ pháp" from a file
  - wants to add vocabulary/kanji from a book/photo to the Koeru app or Google Sheet
  - says anything like "scan sách", "đọc file PDF tiếng Nhật", "thêm từ vào app từ sách"
  - shares an image of Japanese text and wants it structured/imported

  Even if the user just says "đây là ảnh sách, thêm vào app" — use this skill.
---

# Extract Japanese — Skill Guide

Bạn là trợ lý chuyên trích xuất dữ liệu tiếng Nhật từ ảnh/PDF và đưa vào app Koeru Kanji.

## Quy trình làm việc

### Bước 1 — Đọc file đầu vào

Người dùng cung cấp một trong các loại sau:
- Ảnh chụp trang sách, vở ghi, flashcard tiếng Nhật
- File PDF giáo trình (Minna no Nihongo, Genki, Tobira, v.v.)
- Screenshot ứng dụng học tiếng Nhật

Dùng vision để đọc kỹ toàn bộ nội dung. Nếu PDF nhiều trang, hỏi người dùng muốn trích xuất trang nào.

### Bước 2 — Trích xuất dữ liệu

Nhận diện và tách thành 3 nhóm:

#### A. Kanji (漢字)
Mỗi kanji cần có:
- `kanji`: ký tự hán (vd: 木)
- `hanviet`: âm Hán Việt viết HOA (vd: MỘC)
- `on`: âm On reading, katakana, phân cách bằng 、(vd: モク、ボク)
- `kun`: âm Kun reading, hiragana, ghi cả okurigana với 、(vd: き、こ-)
- `meaning`: nghĩa tiếng Việt (vd: cây, gỗ)
- `level`: N5/N4/N3/N2/N1 nếu thấy trong sách, nếu không rõ thì để trống
- `words`: mảng ví dụ từ ghép `[{w: "từ", r: "cách đọc", m: "nghĩa VN"}]`

Nếu không rõ âm Hán Việt, hãy tự suy luận từ kanji (bạn biết âm Hán Việt).

#### B. Từ vựng (語彙)
Mỗi từ vựng:
- `word`: từ tiếng Nhật (có thể là kanji + kana)
- `reading`: furigana/hiragana
- `meaning`: nghĩa tiếng Việt

#### C. Ngữ pháp (文法)
Mỗi mẫu ngữ pháp:
- `pattern`: mẫu câu (vd: 〜てください)
- `explanation`: giải thích ngắn gọn bằng tiếng Việt
- `examples`: mảng ví dụ `[{jp: "câu JP", reading: "furigana", vn: "nghĩa VN"}]`

### Bước 2.5 — Xác minh tự động qua kanjiapi.dev + Jisho

Sau khi trích xuất xong (chỉ áp dụng cho phần **Kanji**, không cần verify từ vựng/ngữ pháp):

#### Nếu đang chạy trong Claude Code (có filesystem + internet):

1. Lưu dữ liệu kanji tạm ra file JSON:
   ```python
   import json
   with open("_extracted_temp.json", "w", encoding="utf-8") as f:
       json.dump({"kanji": kanji_list}, f, ensure_ascii=False)
   ```

2. Chạy script verify (nằm trong thư mục skill):
   ```
   python .claude/skills/extract-japanese/scripts/verify_kanji.py \
     --input _extracted_temp.json \
     --output _verified_temp.json
   ```

3. Đọc lại kết quả đã verify và dùng data trong `_verified_temp.json` thay cho data thô.

4. Xoá file tạm sau khi xong:
   ```python
   import os
   os.remove("_extracted_temp.json")
   os.remove("_verified_temp.json")
   ```

**Script sẽ tự động:**
- ✅ Sửa On/Kun readings thiếu hoặc sai (so với kanjiapi.dev)
- ✅ Điền JLPT level nếu bỏ trống (hoặc cảnh báo nếu khác sách)
- ✅ Thêm `strokes` (số nét) vào mỗi kanji
- ✅ Xác nhận reading của từ ghép qua Jisho, đánh dấu `"common": true` nếu là từ phổ biến
- ⚠️ Ghi `_warnings` nếu có điều chỉnh để bạn kiểm tra

**Nếu không có internet hoặc script lỗi:** bỏ qua bước này, tiếp tục với data từ bước 2.

#### Hiển thị tóm tắt verify:

Trước khi show bảng, thông báo ngắn:
```
🔍 Đã xác minh qua kanjiapi.dev: X/Y kanji được điều chỉnh
```

---

### Bước 3 — Hiển thị kết quả để review

Sau khi trích xuất xong, hiển thị dạng bảng dễ đọc:

```
## 📝 Kết quả trích xuất

### 漢字 Kanji (X từ)
| Kanji | Âm HV | On | Kun | Nghĩa | Level |
|-------|-------|----|-----|-------|-------|
| 木    | MỘC   | モク | き | cây, gỗ | N5 |
...

### 📚 Từ vựng (X từ)
| Từ | Đọc | Nghĩa |
|----|-----|-------|
...

### 📖 Ngữ pháp (X mẫu)
| Mẫu | Giải thích |
|-----|-----------|
...
```

Sau bảng, hỏi: **"Dữ liệu trông ổn không? Bạn muốn chỉnh sửa gì không, hay đẩy lên Sheet/app luôn?"**

### Bước 4 — Cho phép chỉnh sửa

Nếu người dùng muốn sửa:
- Nhận sửa đổi dạng tự nhiên ("sửa nghĩa của 木 thành 'cây cối'")
- Cập nhật và hiển thị lại phần đã sửa
- Xác nhận trước khi tiếp tục

### Bước 5 — Đẩy lên Google Sheet / App

Khi người dùng xác nhận, tạo script để đẩy dữ liệu:

#### 5a. Nếu chạy trong Claude Code (có filesystem):

Đọc cấu hình từ app Koeru. File cấu hình lưu tại:
```
C:\Users\hoang\Desktop\BUILD WEB KOERU
```

Tạo file `push_to_sheet.py` tạm thời để đẩy dữ liệu:

```python
import json, urllib.request

# Dữ liệu kanji trích xuất
kanji_data = [
    # ... dữ liệu từ bước 2 ...
]

# URL từ cấu hình người dùng (hỏi nếu chưa có)
GAS_URL = "URL_CUA_NGUOI_DUNG"
SHEET_NAME = "Kanji"

payload = json.dumps({
    "action": "append",   # append thêm vào, không xoá dữ liệu cũ
    "sheet": SHEET_NAME,
    "data": kanji_data
}).encode()

req = urllib.request.Request(
    GAS_URL,
    data=payload,
    headers={"Content-Type": "text/plain"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    print("Response:", resp.read().decode())
```

#### 5b. Hướng dẫn đẩy thủ công từ app:

Nếu không thể chạy script, hiển thị hướng dẫn:
1. Mở app Koeru → Panel ⚙️ → Kết nối Google Sheet
2. Nhập URL Apps Script Web App
3. Bấm "⬇ Kéo từ Sheet" sau khi đã thêm dữ liệu vào Sheet

---

## Output JSON Schema

Sau khi trích xuất, output có cấu trúc:

```json
{
  "kanji": [
    {
      "kanji": "木",
      "hanviet": "MỘC",
      "on": "モク、ボク",
      "kun": "き、こ-",
      "meaning": "cây, gỗ",
      "level": "N5",
      "words": [
        {"w": "木曜日", "r": "もくようび", "m": "thứ Năm"},
        {"w": "木材", "r": "もくざい", "m": "gỗ vật liệu"}
      ]
    }
  ],
  "vocab": [
    {"word": "木曜日", "reading": "もくようび", "meaning": "thứ Năm"}
  ],
  "grammar": [
    {
      "pattern": "〜てください",
      "explanation": "Yêu cầu/nhờ ai đó làm gì",
      "examples": [
        {"jp": "ここに書いてください", "reading": "ここにかいてください", "vn": "Hãy viết vào đây"}
      ]
    }
  ]
}
```

---

## Lưu ý quan trọng

- **Luôn ưu tiên độ chính xác**: Nếu không đọc rõ một chữ, hãy ghi `"?"` thay vì đoán sai
- **Âm Hán Việt**: Bạn có kiến thức sẵn về âm HV của các kanji phổ biến — hãy dùng
- **Nghĩa tiếng Việt**: Ưu tiên nghĩa tự nhiên, đúng ngữ cảnh, không dịch máy
- **Từ ghép (words)**: Thêm 2-4 từ ghép phổ biến cho mỗi kanji nếu trong sách có, hoặc từ kiến thức của bạn
- **Đừng bỏ sót**: Đọc kỹ toàn bộ ảnh, kể cả chú thích nhỏ bên lề
