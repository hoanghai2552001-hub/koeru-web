# KOERU — Master Project Brief
> Dùng để brief Claude / ChatGPT / designer / reviewer bất kỳ.
> Cập nhật: 2026-05-27

---

## 1. Định danh thương hiệu

| | |
|--|--|
| **Tên** | KOERU |
| **Tagline** | *"Tiếng Nhật · Tiếng Trung — dễ nhớ hơn. Dùng được hơn."* |
| **Mô tả** | Trung tâm học tiếng Nhật & tiếng Trung tại Bà Rịa – Vũng Tàu — kết hợp lớp học thật với công cụ luyện tập online miễn phí |
| **Mô hình** | Hybrid: lớp học thật (offline BR-VT) + công cụ online (toàn quốc) |
| **Concept** | Microlearning + AI hỗ trợ + giáo viên thật theo sát |
| **Ngôn ngữ** | Tiếng Nhật (JLPT N5→N1) — **sản phẩm chính** · Tiếng Trung (HSK 1→3) — nhánh mở rộng |

> ⚠️ **Quan trọng:** KOERU là **trung tâm có giáo viên thật**, không phải app học tự động.
> AI hỗ trợ ôn tập — giáo viên thật theo sát lộ trình.

---

## 2. Design System

```
Màu chính:   --navy   #2d3561  (heading, CTA, nav)
Màu phụ:     --accent #e8845a  (highlight, badge)
Màu vàng:    --yellow #f5c842  (streak, reward)
Nền cream:   --cream  #fdf8f4
Nền trắng:   --white  #ffffff
Border:      --border #e8e4f0
Ink:         --ink2   #5a5f7a  / --ink3 #9196ae

Border radius:  --r 14px | --rs 9px | --rl 22px
Shadow:         0 4px 24px rgba(45,53,97,.08)
Font:           Be Vietnam Pro, Plus Jakarta Sans, Noto Sans JP
```

---

## 3. Cấu trúc website

### `index.html` — Web chính (SPA, không dùng framework)

**Pages** (JS router, không reload):
`home` · `learn` · `flash` · `quiz` · `blog` · `lesson` · `register` · `admin`

**Landing sections** (thứ tự trên trang home):
1. Hero — tagline + 3 chip nhóm người học
2. Stats — 5 phút/bài · N5→N3 · AI · BR-VT
3. Bắt đầu từ đâu? — 5 use-case onboarding cards
4. Courses — 5 khóa + meta (thời lượng, hình thức, phù hợp ai)
5. Testimonials — 3 tình huống học viên thường gặp *(giả định, chưa phải review thật)*
6. Lộ trình JLPT/HSK — roadmap N5→N4→N3→Speaking→Business
7. AI Tools — 5 công cụ (Quiz, Flashcard, Kanji, Kana, Lộ trình)
8. AI hỗ trợ vs Giáo viên thật — grid 2 cột cân bằng
9. FAQ — 6 câu hỏi phổ biến
10. Blog — bài mới nhất
11. Lead Capture — Google Forms iframe + spinner skeleton fallback
12. CTA Band — đăng ký học thử

**Admin:** nằm trong SPA nhưng `display:none` với người dùng thường, có password lock.

---

## 4. Tool Ecosystem

| File | Tên | Vai trò | Target user | CTA chính |
|------|-----|---------|-------------|-----------|
| `kana.html` | Kana Speed | Luyện Hiragana/Katakana | Người mới hoàn toàn | Nhận lộ trình N5 |
| `kanji.html` | KOERU Kanji Lab | Game luyện Kanji N5→N1 | Đã biết kana | Nhận lộ trình Kanji/JLPT |
| `kanji-map.html` | Bản đồ Kanji | Khám phá liên kết Kanji | N4/N3 trở lên | Vào Kanji Lab / Nhận lộ trình N3 |

**Tiếng Trung — tool ecosystem:** Chưa có, đang dùng chung Quiz/Flashcard của index.
- Pinyin Speed: dự kiến (MVP)
- HSK Flashcard: dự kiến
- Hanzi Lab: giai đoạn sau

---

## 5. Phễu học thử (User Journey)

```
Facebook/TikTok content
    ↓
index.html → "Bạn nên bắt đầu từ đâu?"
    ↓
┌─ Mới bắt đầu    → kana.html    → CTA lộ trình N5    (source: kana_speed)
├─ Luyện Kanji    → kanji.html   → CTA lộ trình Kanji  (source: kanji_lab)
├─ N4/N3 khám phá → kanji-map    → CTA Kanji Lab/N3    (source: kanji_map)
└─ Học lại        → Kana + Kanji Lab N5 → form tư vấn  (source: main_site)
    ↓
Form tư vấn (Google Forms) → tư vấn 1-1 → lớp học nhóm nhỏ / 1-1
```

**Lead fields:** name · contact · current_level · goal · available_time · source · cta_location · createdAt

---

## 6. Khóa học

| Khóa | Thời lượng | Hình thức | Phù hợp |
|------|-----------|-----------|---------|
| JLPT N5 → N3 Prep | 8–16 tuần | Online nhóm / 1-1 | Người mới & ôn thi |
| Business Japanese | 8 tuần | Online nhóm / 1-1 | Đi làm / du học |
| HSK 1 → HSK 3 | 10–18 tuần | Online nhóm / 1-1 | Người mới tiếng Trung |
| Giao tiếp tiếng Trung | 8 tuần | Nhóm nhỏ | Giao tiếp & du lịch |
| AI Learning Tools | Linh hoạt | Online tự do | Mọi trình độ — Miễn phí |

---

## 7. Brand Signature — 5 điểm khác biệt

1. **Công cụ miễn phí thật sự** — người dùng học Kanji, Kana trước khi đăng ký
2. **AI hỗ trợ — không thay giáo viên** — định vị rõ, tránh e ngại
3. **Microlearning 5 phút** — phù hợp người đi làm bận
4. **Gamification** — Kanji Lab có dungeon, boss, XP, streak, combo, fever
5. **Data chất lượng** — 1,470 kanji (N5–N1), 3,441 từ vựng reading + nghĩa Việt đã QA

---

## 8. Đã hoàn thành (tháng 5/2026)

| Hạng mục | Trạng thái |
|----------|-----------|
| Form tư vấn/đăng ký "Loading…" | ✅ Spinner skeleton + fallback link |
| Course cards thiếu thông tin | ✅ Thêm meta: thời lượng / hình thức / phù hợp ai |
| Cân bằng AI vs giáo viên thật | ✅ Section grid 2 cột |
| N3 claim "hiểu phim không sub" quá mạnh | ✅ Điều chỉnh mềm hơn |
| Kana Speed thiếu branding + CTA | ✅ "by KOERU Japanese" + guide + CTA N5 |
| Kanji Map fallback quá nghèo | ✅ Full fallback page + loading skeleton |
| 32 từ vựng sai reading/meaning | ✅ Fix kanji-data.js |
| 26 kanji dùng 込 thay ⻌ | ✅ Fix kanji-map-data.js |
| Meta description chưa rõ mô hình | ✅ Cập nhật "trung tâm + công cụ online" |
| Source tracking kanji_map còn thiếu | ✅ Thêm localStorage lead_source |

---

## 9. Điểm còn cần cải thiện

| Ưu tiên | Hạng mục | Lý do |
|---------|----------|-------|
| P1 | Testimonial thật (tên, kết quả, feedback) | Tăng trust trước khi chạy ads |
| P1 | Tracking source đa kênh (facebook, tiktok) | Biết kênh nào tạo lead tốt nhất |
| P2 | Trang riêng từng khóa học (SEO URL) | index SPA không được Google index tốt |
| P2 | Open Graph meta cho kana/kanji/kanji-map | Tăng chất lượng chia sẻ social |
| P3 | Mobile UX Kanji Lab — test màn nhỏ thực tế | Nhiều lớp modal/overlay |
| P3 | N1 mnemonic tiếng Việt (~475 kanji) | Low priority vì tệp N1 ít người học hơn |
| P3 | Pinyin Speed MVP cho tiếng Trung | Hiện tool ecosystem lệch hẳn về tiếng Nhật |

---

## 10. Strategic Priority — 90 ngày tới

### P1 — Chốt nền tuyển sinh tiếng Nhật
- Tập trung N5/N4 tiếng Nhật
- Kana Speed + Kanji Lab làm tool học thử chính
- Hoàn thiện tracking source (main_site, kana_speed, kanji_lab, kanji_map)
- Thu thập testimonial thật từ học viên đầu tiên

### P2 — Tối ưu conversion
- Tạo trang riêng JLPT N5/N4 (hoặc modal chi tiết)
- Test mobile Kanji Lab
- Thêm Open Graph cho 3 tool pages

### P3 — Mở rộng tiếng Trung nhẹ
- Pinyin Speed MVP (luyện thanh điệu + HSK1)
- Chưa làm Hanzi Map cho đến khi có lead tiếng Trung thật

---

## 11. Claude Guardrails — Luật an toàn khi sửa code

```
✋ KHÔNG làm:
- Không refactor toàn bộ file
- Không đổi framework (plain HTML/JS/CSS — không chuyển React/Vite/Next)
- Không đổi id/class/function global nếu không bắt buộc
- Không đổi thứ tự script (thứ tự load quan trọng)
- Không xóa onclick/global function khi chưa có replacement
- Không sửa nhiều tính năng cùng lúc
- Không push mà chưa test

✅ PHẢI làm:
- Trước khi sửa: liệt kê phạm vi ảnh hưởng
- Sau khi sửa: báo cáo file đã thay đổi + checklist test
- Mỗi lần sửa: 1 git commit với message rõ ràng
- Verify bằng static analyzer trước khi push
```

---

## 12. Tech Stack

```
Frontend:   HTML5 + CSS3 + Vanilla JS (no bundler)
Data:       kanji-data.js (1,470 kanji), kanji-map-data.js (853 kanji)
Tools:      React 18 + D3 (kanji-map.html only — standalone CDN)
Forms:      Google Forms iframe (embedded)
Hosting:    GitHub Pages (branch: dev)
Repo:       https://github.com/hoanghai2552001-hub/koeru-web
Live:       https://hoanghai2552001-hub.github.io/koeru-web/
```
