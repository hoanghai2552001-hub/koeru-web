import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

ref = {
    '力': {'on':'リョク', 'meaning':'sức mạnh'},
    '工': {'on':'コウ', 'meaning':'công việc, xây dựng'},
    '元': {'on':'ゲン', 'meaning':'ban đầu, nguyên gốc'},
    '止': {'on':'シ', 'meaning':'dừng lại'},
    '引': {'on':'イン', 'meaning':'kéo, dẫn'},
    '牛': {'on':'ギュウ', 'meaning':'bò, trâu'},
    '犬': {'on':'ケン', 'meaning':'chó'},
    '不': {'on':'フ、ブ', 'meaning':'không, bất'},
    '文': {'on':'ブン', 'meaning':'văn, chữ'},
    '方': {'on':'ホウ', 'meaning':'hướng, cách'},
    '心': {'on':'シン', 'meaning':'trái tim, tâm trí'},
    '切': {'on':'セツ', 'meaning':'cắt, quan trọng'},
    '代': {'on':'ダイ', 'meaning':'thay thế, đời'},
    '世': {'on':'セ、セイ', 'meaning':'đời, thế giới'},
    '正': {'on':'セイ', 'meaning':'đúng, chính xác'},
    '田': {'on':'デン', 'meaning':'ruộng'},
    '冬': {'on':'トウ', 'meaning':'mùa đông'},
    '兄': {'on':'ケイ', 'meaning':'anh trai'},
    '用': {'on':'ヨウ', 'meaning':'sử dụng'},
    '去': {'on':'キョ', 'meaning':'qua, đi'},
    '市': {'on':'シ', 'meaning':'thành phố'},
    '広': {'on':'コウ', 'meaning':'rộng'},
    '主': {'on':'シュ', 'meaning':'chủ, chính'},
    '字': {'on':'ジ', 'meaning':'chữ, ký tự'},
    '考': {'on':'コウ', 'meaning':'suy nghĩ'},
    '光': {'on':'コウ', 'meaning':'ánh sáng'},
    '好': {'on':'コウ', 'meaning':'thích'},
    '有': {'on':'ユウ', 'meaning':'có'},
    '同': {'on':'ドウ', 'meaning':'giống nhau, cùng'},
    '肉': {'on':'ニク', 'meaning':'thịt'},
    '色': {'on':'ショク', 'meaning':'màu sắc'},
    '早': {'on':'ソウ', 'meaning':'sớm, nhanh'},
    '地': {'on':'チ', 'meaning':'đất, vùng'},
    '村': {'on':'ソン', 'meaning':'làng'},
    '体': {'on':'タイ', 'meaning':'cơ thể'},
    '低': {'on':'テイ', 'meaning':'thấp'},
    '弟': {'on':'テイ', 'meaning':'em trai'},
    '走': {'on':'ソウ', 'meaning':'chạy'},
    '赤': {'on':'セキ', 'meaning':'màu đỏ'},
    '売': {'on':'バイ', 'meaning':'bán'},
    '別': {'on':'ベツ', 'meaning':'riêng biệt, chia tay'},
    '医': {'on':'イ', 'meaning':'bác sĩ, y học'},
    '近': {'on':'キン', 'meaning':'gần'},
    '私': {'on':'シ', 'meaning':'tôi, riêng tư'},
    '作': {'on':'サク', 'meaning':'làm, tạo'},
    '者': {'on':'シャ', 'meaning':'người'},
    '事': {'on':'ジ', 'meaning':'việc, sự'},
    '使': {'on':'シ', 'meaning':'dùng, sứ giả'},
    '始': {'on':'シ', 'meaning':'bắt đầu'},
    '姉': {'on':'シ', 'meaning':'chị gái'},
    '妹': {'on':'マイ', 'meaning':'em gái'},
    '味': {'on':'ミ', 'meaning':'vị, hương vị'},
    '服': {'on':'フク', 'meaning':'quần áo'},
    '物': {'on':'ブツ', 'meaning':'đồ vật'},
    '歩': {'on':'ホ', 'meaning':'đi bộ'},
    '門': {'on':'モン', 'meaning':'cổng, môn'},
    '夜': {'on':'ヤ', 'meaning':'ban đêm'},
    '明': {'on':'メイ', 'meaning':'sáng, rõ'},
    '林': {'on':'リン', 'meaning':'rừng thưa'},
    '青': {'on':'セイ', 'meaning':'xanh'},
    '注': {'on':'チュウ', 'meaning':'chú ý, đổ'},
    '知': {'on':'チ', 'meaning':'biết'},
    '昼': {'on':'チュウ', 'meaning':'ban ngày, trưa'},
    '茶': {'on':'チャ', 'meaning':'trà'},
    '待': {'on':'タイ', 'meaning':'chờ'},
    '送': {'on':'ソウ', 'meaning':'gửi'},
    '海': {'on':'カイ', 'meaning':'biển'},
    '音': {'on':'オン', 'meaning':'âm thanh'},
    '急': {'on':'キュウ', 'meaning':'gấp, khẩn cấp'},
    '計': {'on':'ケイ', 'meaning':'kế hoạch, đo'},
    '建': {'on':'ケン', 'meaning':'xây dựng'},
    '県': {'on':'ケン', 'meaning':'tỉnh'},
    '思': {'on':'シ', 'meaning':'nghĩ'},
    '乗': {'on':'ジョウ', 'meaning':'lên (xe)'},
    '重': {'on':'ジュウ、チョウ', 'meaning':'nặng, quan trọng'},
    '春': {'on':'シュン', 'meaning':'mùa xuân'},
    '秋': {'on':'シュウ', 'meaning':'mùa thu'},
    '弱': {'on':'ジャク', 'meaning':'yếu'},
    '紙': {'on':'シ', 'meaning':'giấy'},
    '帰': {'on':'キ', 'meaning':'về'},
    '起': {'on':'キ', 'meaning':'thức dậy'},
    '夏': {'on':'カ', 'meaning':'mùa hè'},
    '家': {'on':'カ', 'meaning':'nhà'},
    '病': {'on':'ビョウ', 'meaning':'bệnh'},
    '特': {'on':'トク', 'meaning':'đặc biệt'},
    '旅': {'on':'リョ', 'meaning':'du lịch'},
    '通': {'on':'ツウ', 'meaning':'đi qua, thông'},
    '鳥': {'on':'チョウ', 'meaning':'chim'},
    '動': {'on':'ドウ', 'meaning':'chuyển động'},
    '強': {'on':'キョウ', 'meaning':'mạnh'},
    '教': {'on':'キョウ', 'meaning':'dạy'},
    '黒': {'on':'コク', 'meaning':'màu đen'},
    '終': {'on':'シュウ', 'meaning':'kết thúc'},
    '習': {'on':'シュウ', 'meaning':'học, tập'},
    '寒': {'on':'カン', 'meaning':'lạnh'},
    '軽': {'on':'ケイ', 'meaning':'nhẹ'},
    '運': {'on':'ウン', 'meaning':'vận chuyển, may mắn'},
    '開': {'on':'カイ', 'meaning':'mở'},
    '飯': {'on':'ハン', 'meaning':'cơm'},
    '答': {'on':'トウ', 'meaning':'trả lời'},
    '森': {'on':'シン', 'meaning':'rừng'},
    '暑': {'on':'ショ', 'meaning':'nóng'},
    '着': {'on':'チャク', 'meaning':'mặc, đến'},
    '短': {'on':'タン', 'meaning':'ngắn'},
    '楽': {'on':'ガク', 'meaning':'vui, dễ chịu'},
}

diffs = []
for k, r in ref.items():
    m = re.search(r'\{kanji:"' + re.escape(k) + r'",hanviet:[^}]+\}', content)
    if not m:
        diffs.append({'k': k, 'issues': ['NOT FOUND']})
        continue
    entry = m.group(0)
    on_m = re.search(r'on:"([^"]+)"', entry)
    meaning_m = re.search(r',meaning:"([^"]+)"', entry)
    cur_on = on_m.group(1) if on_m else '?'
    cur_meaning = meaning_m.group(1) if meaning_m else '?'

    issues = []
    if r['on'] != cur_on:
        issues.append(f'on: "{cur_on}" → "{r["on"]}"')
    if r['meaning'] != cur_meaning:
        issues.append(f'meaning: "{cur_meaning}" → "{r["meaning"]}"')
    if issues:
        diffs.append({'k': k, 'issues': issues})

print(f'Cần sửa: {len(diffs)} kanji')
for d in diffs:
    print(f'  {d["k"]}: {" | ".join(d["issues"])}')
