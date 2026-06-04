"""Fill in empty radical/parts fields for N3, N4, N5 kanji."""
import re, shutil

PROJECT = r"C:\Users\hoang\Desktop\BUILD WEB KOERU"

# radical format: "KANGXI_CHAR|name_ja|meaning_en|meaning_vi"
# parts: list of component CJK chars

KANJI_DATA = {
    # ════ N4 — 44 kanji ════
    '自': ('⾃|みずから|self|bản thân',             ['自']),
    '発': ('⽨|はつがしら|outspread legs|khởi hành', ['癶', '弓']),
    '業': ('⽊|き|tree, wood|cây gỗ',               ['木', '羊']),
    '場': ('⼕|つち|earth|đất',                      ['土', '日', '勿']),
    '員': ('⼝|くち|mouth|miệng',                    ['口', '貝']),
    '問': ('⾨|もんがまえ|gate, door|cổng cửa',       ['門', '口']),
    '京': ('⼇|なべぶた|lid, top|nắp',               ['亠', '口', '小']),
    '理': ('⽟|たま|jewelry|ngọc quý',               ['王', '里']),
    '題': ('⾴|おおがい|head, page|cái đầu',          ['是', '頁']),
    '意': ('⼼|こころ|heart, mind|trái tim',          ['音', '心']),
    '度': ('⼴|まだれ|slanting roof|mái nghiêng',     ['广', '廿', '又']),
    '持': ('⼿|て|hand|tay',                         ['扌', '寺']),
    '野': ('⾥|さと|village|ngôi làng',               ['里', '予']),
    '以': ('⼈|ひと|person|người',                    ['人', '乙']),
    '院': ('⻖|こざとへん|hill, mound|đồi, gò',       ['阝', '宀', '儿']),
    '界': ('⽥|た|rice paddy|ruộng lúa',              ['田', '介']),
    '画': ('⽥|た|rice paddy|ruộng lúa',              ['一', '凵', '田']),
    '集': ('⾫|ふるとり|small bird|chim nhỏ',         ['隹', '木']),
    '品': ('⼝|くち|mouth|miệng',                     ['口', '口', '口']),
    '死': ('⽍|がつへん|death, decay|chết, phân hủy', ['歹', '匕']),
    '朝': ('⽉|つき|moon, month|mặt trăng',           ['月', '十', '早']),
    '台': ('⼝|くち|mouth|miệng',                     ['厶', '口']),
    '住': ('⺅|にんべん|person|người',                 ['亻', '主']),
    '真': ('⽬|め|eye|mắt',                           ['十', '目', '八']),
    '町': ('⽥|た|rice paddy|ruộng lúa',              ['田', '丁']),
    '料': ('⽶|こめ|rice|gạo',                        ['米', '斗']),
    '転': ('⾞|くるま|vehicle, wheel|xe',              ['車', '専']),
    '究': ('⽳|あな|hole, cave|hang lỗ',              ['穴', '九']),
    '質': ('⾙|かい|shell, property|tiền của',         ['斤', '斤', '貝']),
    '族': ('⽅|ほう|direction, flag|phương hướng',     ['方', '矢']),
    '験': ('⾺|うま|horse|ngựa',                      ['馬', '僉']),
    '英': ('⺾|くさかんむり|grass|cỏ',                 ['艹', '央']),
    '写': ('⼍|わかんむり|cover, crown|mái che',       ['冖', '与']),
    '悪': ('⼼|こころ|heart, mind|trái tim',           ['亜', '心']),
    '室': ('⼧|うかんむり|roof, house|mái nhà',        ['宀', '至']),
    '風': ('⾵|かぜ|wind|gió',                        ['几', '虫']),
    '屋': ('⼫|しかばね|corpse, awning|mái che',       ['尸', '至']),
    '洋': ('⺡|さんずい|water|nước',                   ['氵', '羊']),
    '夕': ('⼣|ゆうべ|evening|buổi tối',               ['夕']),
    '借': ('⺅|にんべん|person|người',                 ['亻', '昔']),
    '曜': ('⽇|ひ|sun, day|mặt trời',                 ['日', '隹', '羽']),
    '貸': ('⾙|かい|shell, property|tiền của',         ['代', '貝']),
    '堂': ('⼕|つち|earth|đất',                       ['口', '土']),
    '勉': ('⼒|ちから|power|sức mạnh',                ['力', '免']),

    # ════ N3 — 56 kanji ════
    '議': ('⾔|げん|words, to speak|lời nói',          ['言', '義']),
    '民': ('⽒|うじ|clan, family|họ tộc',              ['民']),
    '部': ('⾢|おおざと|village, city|làng thành',      ['立', '口', '阝']),
    '合': ('⼝|くち|mouth|miệng',                      ['人', '口']),
    '回': ('⼝|くち|mouth|miệng',                      ['囗', '口']),
    '実': ('⼧|うかんむり|roof, house|mái nhà',         ['宀', '貫']),
    '関': ('⾨|もんがまえ|gate, door|cổng cửa',         ['門', '糸']),
    '最': ('⽈|ひらび|to say|nói',                      ['冃', '耳', '又']),
    '首': ('⾸|くび|neck, head|đầu, cổ',               ['首']),
    '期': ('⽉|つき|moon, month|mặt trăng',             ['月', '其']),
    '都': ('⾢|おおざと|village, city|làng thành',      ['者', '阝']),
    '進': ('⻌|しんにょう|road, walk|con đường',         ['隹', '辶']),
    '数': ('⺙|ぼくづくり|activity, to strike|hành động', ['米', '女', '攵']),
    '記': ('⾔|げん|words, to speak|lời nói',           ['言', '己']),
    '産': ('⽣|うまれる|birth, live|sinh sống',          ['立', '彦', '生']),
    '求': ('⽔|みず|water|nước',                        ['求']),
    '所': ('⼾|と|door|cửa',                            ['戸', '斤']),
    '官': ('⼧|うかんむり|roof, house|mái nhà',          ['宀', '吕']),
    '直': ('⽬|め|eye|mắt',                             ['目', '十']),
    '式': ('⼯|たくみ|work, skill|công việc',            ['工', '弋']),
    '確': ('⽯|いし|stone|đá',                          ['石', '隹']),
    '位': ('⺅|にんべん|person|người',                   ['亻', '立']),
    '格': ('⽊|き|tree, wood|cây gỗ',                   ['木', '各']),
    '疑': ('⽢|やへん|arrow|mũi tên',                    ['矢', '匕', '疋']),
    '球': ('⽟|たま|jewelry|ngọc quý',                   ['王', '求']),
    '割': ('⼑|かたな|knife, sword|dao kiếm',            ['刀', '害']),
    '消': ('⺡|さんずい|water|nước',                     ['氵', '肖']),
    '規': ('⾒|みる|to see|nhìn thấy',                   ['夫', '見']),
    '害': ('⼧|うかんむり|roof, house|mái nhà',          ['宀', '丰', '口']),
    '声': ('⼠|さむらいかんむり|man, scholar|võ sĩ',      ['士', '口']),
    '葉': ('⺾|くさかんむり|grass|cỏ',                   ['艹', '世', '木']),
    '働': ('⺅|にんべん|person|người',                   ['亻', '動']),
    '非': ('⾮|あらず|not, wrong|không phải',            ['非']),
    '観': ('⾒|みる|to see|nhìn thấy',                   ['雚', '見']),
    '科': ('⽲|のぎへん|grain|ngũ cốc',                  ['禾', '斗']),
    '太': ('⼤|だい|large, big|lớn',                     ['大', '丶']),
    '客': ('⼧|うかんむり|roof, house|mái nhà',          ['宀', '各']),
    '号': ('⼝|くち|mouth|miệng',                        ['口', '亏']),
    '座': ('⼴|まだれ|slanting roof|mái nghiêng',        ['广', '坐']),
    '給': ('⽷|いと|thread|sợi chỉ',                    ['糸', '合']),
    '寄': ('⼧|うかんむり|roof, house|mái nhà',          ['宀', '奇']),
    '込': ('⻌|しんにょう|road, walk|con đường',          ['入', '辶']),
    '覚': ('⾒|みる|to see|nhìn thấy',                   ['学', '見']),
    '許': ('⾔|げん|words, to speak|lời nói',            ['言', '午']),
    '便': ('⺅|にんべん|person|người',                   ['亻', '更']),
    '勤': ('⼒|ちから|power|sức mạnh',                   ['堇', '力']),
    '居': ('⼫|しかばね|corpse, awning|mái che',          ['尸', '古']),
    '招': ('⺘|てへん|hand|bàn tay',                     ['扌', '召']),
    '願': ('⾴|おおがい|head, page|cái đầu',             ['原', '頁']),
    '絵': ('⽷|いと|thread|sợi chỉ',                    ['糸', '会']),
    '掛': ('⺘|てへん|hand|bàn tay',                     ['扌', '卦']),
    '吸': ('⼝|くち|mouth|miệng',                        ['口', '及']),
    '洗': ('⺡|さんずい|water|nước',                     ['氵', '先']),
    '慣': ('⺖|りっしんべん|heart, mind|tâm trí',         ['忄', '貫']),
    '皆': ('⽩|しろ|white|trắng',                        ['比', '白']),
    '幾': ('⼱|はば|cloth|vải',                          ['幺', '幺', '戍']),
}

# Fix ⼕ → ⼕ is はこがまえ (box). For 場/堂 radical is 土 = ⼕
# Actually from our verified list: ⼕ U+2F15 = はこがまえ, ⼕ U+2F1F = つち
# We need ⼕ for earth. Let me correct:
KANJI_DATA['場'] = ('⼕|つち|earth|đất', ['土', '日', '勿'])
KANJI_DATA['堂'] = ('⼕|つち|earth|đất', ['口', '土'])
# Note: ⼕ in the dict above may be U+2F15 or U+2F1F depending on system rendering
# We confirmed ⼕ U+2F1F = つち in our radicals scan - using that char explicitly:
earth_radical = '⼟'  # ⼕ KANGXI RADICAL EARTH U+2F1F
KANJI_DATA['場'] = (f'{earth_radical}|つち|earth|đất', ['土', '日', '勿'])
KANJI_DATA['堂'] = (f'{earth_radical}|つち|earth|đất', ['口', '土'])


def make_parts_str(parts):
    return ', '.join(f'"{p}"' for p in parts)


def apply_to_file(path, target_kanji):
    shutil.copy2(path, path + '.bak2')
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    fixed = []
    changed = 0

    for line in lines:
        km = re.search(r'kanji:"(.)"', line)
        if km:
            k = km.group(1)
            if k in target_kanji and k in KANJI_DATA:
                radical_str, parts_list = KANJI_DATA[k]
                parts_str = make_parts_str(parts_list)

                rad_empty = re.search(r'radical:""', line)
                parts_empty = re.search(r'parts:\[\]', line)

                if rad_empty:
                    line = line.replace('radical:""', f'radical:"{radical_str}"')
                if parts_empty:
                    line = line.replace('parts:[]', f'parts:[{parts_str}]')
                if rad_empty or parts_empty:
                    changed += 1

        fixed.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(fixed)

    return changed


N4 = set('自発業場員問京理題意度持野以院界画集品死朝台住真町料転究質族験英写悪室風屋洋夕借曜貸堂勉')
N3 = set('議民部合回実関最首期都進数記産求所官直式確位格疑球割消規害声葉働非観科太客号座給寄込覚許便勤居招願絵掛吸洗慣皆幾')

n4 = apply_to_file(f"{PROJECT}/js/kanji-data-n4.js", N4)
n3 = apply_to_file(f"{PROJECT}/js/kanji-data-n3.js", N3)
print(f"kanji-data-n4.js: {n4} entries updated")
print(f"kanji-data-n3.js: {n3} entries updated")
