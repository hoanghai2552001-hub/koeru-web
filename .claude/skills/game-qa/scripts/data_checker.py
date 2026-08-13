"""
data_checker.py — Kiểm tra chất lượng dữ liệu kanji-data.js

Kiểm tra:
  - words[].m có nghĩa tiếng Anh không (Latin không dấu)
  - Kanji thiếu trường bắt buộc (on/kun/meaning/level)
  - on không phải katakana, kun không phải hiragana
  - words[].r không phải kana

Whitelist format:
  - kun/on cho phép dấu gạch ngang '-' làm ranh giới okurigana,
    ví dụ: おく-る, -のみ, -ノウ, たか-い  → hợp lệ, không phải lỗi

Chạy:
    python data_checker.py --data js/kanji-data.js --out qa_data_report.json
"""

import re, json, os, argparse

VIET_MARKS = re.compile(
    r'[àáảãạăắặẳẵâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
    r'ÀÁẢÃẠĂẮẶẲẴÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]'
)
KATAKANA = re.compile(r'^[ァ-ヶーA-Zａ-ｚ、・\s]+$')
HIRAGANA = re.compile(r'^[ぁ-ん・ーA-Za-zａ-ｚ（）()\.\s]+$')
KANA     = re.compile(r'^[ぁ-ん々一-鿿ァ-ヶー\s・ゞ]+$')

VIET_NO_MARK_OK = {
    'an','ba','ca','co','cu','da','di','du','ha','ho','la','le','li','lo','lu',
    'ma','me','mi','mo','mu','na','ne','ni','no','nu','oi','om','on','or',
    'ra','re','ri','ro','ru','sa','se','si','so','su','ta','te','ti','to','tu',
    'ut','va','ve','vi','vo','vu','xa','xe','xi','xo','xu',
    # Hán Việt viết thường
    'hoa','mua','hai','tay','mat','tai','chan','vai','mot','tue','boc',
}

def is_english(s):
    if not s: return False
    if VIET_MARKS.search(s): return False
    if re.search(r'[ぁ-んァ-ヶ一-鿿]', s): return False
    if not re.match(r'^[a-zA-Z\s\-\(\)\/\.,\'\"0-9%]+$', s.strip()):
        return False
    words = re.split(r'[\s\-\(\)\/,\.]+', s.strip().lower())
    words = [w for w in words if w]
    if len(s.strip()) <= 4: return False
    if all(w in VIET_NO_MARK_OK for w in words): return False
    EN_MARKERS = {
        'the','a','an','of','in','on','at','to','for','with','by','from','and','or',
        'not','is','are','was','were','be','been','have','has','that','this','which',
        'one','two','three','year','make','take','get','go','come','see','know',
        'good','bad','big','small','large','new','old','high','low',
        'national','general','special','main','local','original',
        'school','university','company','government','family',
    }
    if any(w in EN_MARKERS for w in words): return True
    if len(words) >= 3: return True
    return False


def parse_kanji_js(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries = []
    for line in content.splitlines():
        s = line.strip().rstrip(',')
        if s.startswith('{kanji:'):
            try:
                j = re.sub(r'(?<!["\w])([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*:)', r'"\1"', s)
                obj = json.loads(j)
                entries.append(obj)
            except:
                pass
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='js/kanji-data.js')
    parser.add_argument('--out', default='qa_data_report.json')
    args = parser.parse_args()

    print(f'📂 Đọc {args.data}...')
    entries = parse_kanji_js(args.data)
    print(f'   {len(entries)} kanji\n')

    issues = {
        'english_meanings': [],
        'missing_fields': [],
        'wrong_reading_format': [],
        'total_kanji': len(entries),
    }

    en_count = 0
    missing_count = 0
    fmt_count = 0

    for obj in entries:
        k = obj.get('kanji', '?')
        level = obj.get('level', '')

        # Kiểm tra trường bắt buộc
        for field in ['on', 'kun', 'meaning', 'level']:
            val = obj.get(field, '')
            if not val or val == '—':
                missing_count += 1
                issues['missing_fields'].append({
                    'kanji': k, 'level': level, 'missing': field
                })

        # Kiểm tra định dạng on/kun
        on = obj.get('on', '')
        kun = obj.get('kun', '')
        # Strip separator chars before matching:
        #   '、' = reading delimiter, '.' / '-' = okurigana boundary marker (e.g. おく-る, -ノウ)
        on_norm  = on.replace('、', '').replace('.', '').replace('-', '').replace('ー', '')
        kun_norm = kun.replace('、', '').replace('.', '').replace('-', '')
        if on and on != '—' and not KATAKANA.match(on_norm):
            fmt_count += 1
            issues['wrong_reading_format'].append({
                'kanji': k, 'field': 'on', 'value': on[:30]
            })
        if kun and kun != '—' and not HIRAGANA.match(kun_norm):
            fmt_count += 1
            issues['wrong_reading_format'].append({
                'kanji': k, 'field': 'kun', 'value': kun[:30]
            })

        # Kiểm tra words
        for w in obj.get('words', []):
            wm = w.get('m', '')
            if is_english(wm):
                en_count += 1
                issues['english_meanings'].append({
                    'kanji': k, 'level': level,
                    'word': w.get('w', ''), 'meaning': wm[:60]
                })
            wr = w.get('r', '')
            if wr and not KANA.match(wr):
                fmt_count += 1
                issues['wrong_reading_format'].append({
                    'kanji': k, 'field': 'word_reading',
                    'word': w.get('w', ''), 'value': wr[:20]
                })

    # Summary
    issues['summary'] = {
        'total_kanji': len(entries),
        'english_meanings': en_count,
        'missing_fields': missing_count,
        'wrong_reading_format': fmt_count,
        'total_issues': en_count + missing_count + fmt_count,
        'clean_kanji': sum(
            1 for obj in entries
            if not any(is_english(w.get('m','')) for w in obj.get('words', []))
            and obj.get('meaning') and obj.get('level')
        ),
    }

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)

    s = issues['summary']
    print(f'{"="*50}')
    print(f'Kết quả data check:')
    print(f'  🔵 English meanings  : {s["english_meanings"]}')
    print(f'  🟡 Missing fields    : {s["missing_fields"]}')
    print(f'  🟡 Wrong format      : {s["wrong_reading_format"]}')
    print(f'  ✅ Clean kanji       : {s["clean_kanji"]}/{s["total_kanji"]}')
    print(f'\n💾 Báo cáo → {args.out}')


if __name__ == '__main__':
    main()
