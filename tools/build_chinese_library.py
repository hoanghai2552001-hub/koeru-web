"""Build a local, reviewable Chinese library without changing teaching data.

python tools/build_chinese_library.py [--with-cedict]
Outputs stay in gitignored output/chinese-library. No paid API calls.
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'chinese-library'
CEDICT_URL = 'https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz'
HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def audio(text):
    # Existing generator names vocabulary audio using the primary spelling.
    text = text.split('(')[0].split('（')[0].strip()
    if not text or re.search(r'[<>:"/\\|?*\x00-\x1f]', text):
        return {'path': None, 'status': 'missing'}
    path = ROOT / 'audio' / 'hsk' / (text + '.mp3')
    exists = path.is_file() and path.stat().st_size > 0
    return {'path': path.relative_to(ROOT).as_posix() if exists else None,
            'status': 'present_unverified' if exists else 'missing'}


def inventory():
    sources = []
    for path in sorted((ROOT / 'Tiếng Trung').rglob('*')):
        if not path.is_file():
            continue
        record = {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                  'public_rights': 'not_verified'}
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                record['members'] = [{'path': i.filename, 'bytes': i.file_size}
                                     for i in archive.infolist() if not i.is_dir()]
            record['types'] = dict(Counter(Path(i['path']).suffix.lower() for i in record['members']))
            record['inventory_scope'] = 'direct_members_only; nested archives not expanded'
        sources.append(record)
    return sources


def dictionary_reference(needed, download):
    path = OUT / 'cedict-source.txt.gz'
    if download and not path.exists():
        request = urllib.request.Request(CEDICT_URL, headers={'User-Agent': 'KOERU-local-library/1.0'})
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read()
        gzip.decompress(raw)  # Validate before saving the cache.
        path.write_bytes(raw)
    matches = {}
    if path.exists():
        for line in gzip.decompress(path.read_bytes()).decode('utf-8-sig').splitlines():
            m = re.match(r'^(\S+) (\S+) \[([^]]+)\] /(.+)/$', line)
            if m and m[2] in needed:
                matches.setdefault(m[2], []).append({'traditional': m[1], 'pinyin_numbered': m[3],
                                                     'definitions_en': m[4].split('/')})
    write_json('dictionary-reference.json', {
        'source': 'CC-CEDICT / MDBG', 'url': CEDICT_URL,
        'license': 'CC BY-SA 4.0', 'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
        'note': 'Reference candidates only. No automatic selection of reading or Vietnamese translation.',
        'entries': matches})
    return matches


def build(with_cedict=False):
    OUT.mkdir(parents=True, exist_ok=True)
    sources, vocab, sentences, grammar, lessons = inventory(), [], [], [], []
    corrections = read_json(ROOT / 'database' / 'hsk_corrections.json')
    for level in (1, 2, 3):
        folder = ROOT / 'database' / f'hsk{level}'
        curated_path = folder / 'curated_examples.json'
        curated = read_json(curated_path) if curated_path.exists() else {}
        dialogue_path = folder / 'curated_dialogue.json'
        dialogues = read_json(dialogue_path) if dialogue_path.exists() else {}
        for path in sorted(folder.glob('lesson*.json')):
            data = read_json(path)
            base = {'level': level, 'lesson': data['lesson'], 'source': path.relative_to(ROOT).as_posix(),
                    'source_description': data.get('source', ''), 'status': data.get('status', 'REVIEW_REQUIRED')}
            lessons.append({**base, 'title': data.get('title', ''), 'topics': data.get('topics', [])})
            for index, item in enumerate(data.get('vocab', [])):
                word = dict(item)
                patch = corrections.get(f'HSK{level}', {}).get(word.get('h'), {})
                word.update({k: value for k, value in patch.items() if k != 'why'})
                example_source = base['source']
                if word.get('h') in curated:
                    word.update(curated[word['h']])
                    example_source = curated_path.relative_to(ROOT).as_posix()
                rid = f'hsk{level}-l{data["lesson"]:02d}-v{index + 1:03d}'
                issues = [f'missing_{k}' for k in ('h', 'p', 'm') if not word.get(k)]
                if not all(word.get(k) for k in ('ex_zh', 'ex_p', 'ex_vi')):
                    issues.append('incomplete_example')
                if re.search(r'\b(eyes|the|and|to)\b', word.get('p', ''), re.I):
                    issues.append('possible_english_in_pinyin')
                vocab.append({**base, 'id': rid, 'hanzi': word.get('h', ''), 'pinyin': word.get('p', ''),
                              'meaning_vi': word.get('m', ''), 'han_viet': word.get('hv', ''),
                              'pos': word.get('pos', ''), 'audio': audio(word.get('h', '')),
                              'issues': issues, 'review_status': 'needs_review'})
                if patch:
                    vocab[-1]['correction_source'] = 'database/hsk_corrections.json'
                if word.get('ex_zh'):
                    sentences.append({**base, 'source': example_source, 'id': rid + '-example',
                                      'kind': 'example', 'vocab_id': rid, 'zh': word['ex_zh'],
                                      'pinyin': word.get('ex_p', ''), 'meaning_vi': word.get('ex_vi', ''),
                                      'audio': audio(word['ex_zh']), 'review_status': 'needs_review'})
            authored = dialogues.get(str(data['lesson']))
            for index, line in enumerate(authored['lines'] if authored else data.get('dialogue', [])):
                sentences.append({**base, 'id': f'hsk{level}-l{data["lesson"]:02d}-d{index + 1:03d}',
                                  'kind': 'dialogue', 'zh': line.get('zh', ''), 'pinyin': line.get('p', ''),
                                  'meaning_vi': line.get('vi', ''), 'speaker': line.get('spk', ''),
                                  'part': line.get('part'), 'topic': line.get('topic', ''),
                                  'audio': audio(line.get('zh', '')), 'review_status': 'needs_review'})
                if authored:
                    sentences[-1]['source'] = dialogue_path.relative_to(ROOT).as_posix()
                    sentences[-1]['source_description'] = authored['source']
            for index, item in enumerate(data.get('grammar', [])):
                grammar.append({**base, 'id': f'hsk{level}-l{data["lesson"]:02d}-g{index + 1:03d}',
                                'content': item, 'review_status': 'needs_review'})
    characters = {}
    for word in vocab:
        for char in sorted(set(HAN.findall(word['hanzi']))):
            characters.setdefault(char, {'hanzi': char, 'vocab_ids': [], 'levels': [],
                                        'stroke_data_status': 'not_downloaded'})
            characters[char]['vocab_ids'].append(word['id'])
            characters[char]['levels'] = sorted(set(characters[char]['levels'] + [word['level']]))
    needed = {v['hanzi'].split('(')[0].split('（')[0].strip() for v in vocab} | set(characters)
    for char, entry in characters.items():
        path = ROOT / 'data' / 'hanzi-strokes' / (char + '.json')
        if path.is_file():
            entry['stroke_data_status'] = 'available_local'
            entry['stroke_data_path'] = path.relative_to(ROOT).as_posix()
    refs = dictionary_reference(needed, with_cedict)
    for word in vocab:
        word['dictionary_key'] = word['hanzi'].split('(')[0].split('（')[0].strip()
        word['dictionary_candidates'] = len(refs.get(word['dictionary_key'], []))
        word['level_system'] = 'source_textbook_hsk; not_mapped_to_2021_or_2026'
        word['character_ids'] = sorted(set(HAN.findall(word['hanzi'])))
        word['example_ids'] = [s['id'] for s in sentences if s.get('vocab_id') == word['id']]
        word['dictionary_refs'] = refs.get(word['dictionary_key'], [])
    for char, entry in characters.items():
        if entry.get('stroke_data_path'):
            stroke = read_json(ROOT / entry['stroke_data_path'])
            entry['stroke_count'] = len(stroke.get('strokes', []))
            entry['stroke_license'] = 'Arphic Public License'
        entry['dictionary_refs'] = refs.get(char, [])
    write_json('manifest.json', {
        'schema_version': 1,
        'level_system': 'source_textbook_hsk; not_mapped_to_2021_or_2026',
        'public_release_ready': False,
        'files': ['vocabulary.json', 'sentences.json', 'characters.json', 'grammar.json', 'lessons.json'],
        'review_policy': 'No automatic promotion from needs_review to approved.',
        'dictionary_license': 'CC BY-SA 4.0',
        'dictionary_attribution': 'CC-CEDICT / MDBG',
        'dictionary_source': CEDICT_URL,
        'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / 'database').glob('hsk*/*.json'))}
    })
    summary = []
    for level in (1, 2, 3):
        words = [v for v in vocab if v['level'] == level]
        lines = [s for s in sentences if s['level'] == level]
        summary.append({'level': level, 'vocab_records': len(words),
                        'unique_words': len({v['hanzi'] for v in words}),
                        'complete_examples': sum(s['kind'] == 'example' and bool(s['pinyin'] and s['meaning_vi']) for s in lines),
                        'dialogue_lines': sum(s['kind'] == 'dialogue' for s in lines),
                        'vocab_audio_present': sum(v['audio']['path'] is not None for v in words),
                        'dictionary_matched': sum(v['dictionary_candidates'] > 0 for v in words)})
    write_json('sources.json', sources)
    write_json('vocabulary.json', vocab)
    write_json('sentences.json', sentences)
    write_json('characters.json', list(characters.values()))
    write_json('grammar.json', grammar)
    write_json('lessons.json', lessons)
    write_json('summary.json', summary)
    missing = {}
    for entry in vocab + sentences:
        text = entry.get('hanzi', entry.get('zh', '')).split('(')[0].split('（')[0].strip()
        if text and not entry['audio']['path']:
            missing.setdefault(text, []).append(entry['id'])
    write_json('missing-audio.json', [{'text': text, 'record_ids': ids, 'status': 'review_text_before_synthesis'}
                                      for text, ids in sorted(missing.items())])
    with (OUT / 'vocabulary-review.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        fields = ['id', 'level', 'lesson', 'hanzi', 'pinyin', 'meaning_vi', 'han_viet', 'source', 'review_status']
        writer = csv.DictWriter(stream, fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(vocab)
    report = ['# Kho học liệu tiếng Trung — bản nội bộ cần duyệt', '',
              'Dựng từ dữ liệu đã trích xuất trong máy; không ghi đè bài học đang chạy.',
              'HSK là cấp của tài liệu nguồn hiện có, không quy đổi tự động sang HSK 3.0.', '',
              '| Cấp | Mục từ | Ví dụ đủ 3 trường | Lượt thoại | Audio từ có file | Từ đối chiếu CC-CEDICT |',
              '|---|---:|---:|---:|---:|---:|']
    for row in summary:
        report.append('| HSK {level} | {vocab_records} | {complete_examples} | {dialogue_lines} | {vocab_audio_present} | {dictionary_matched} |'.format(**row))
    report += ['', f'- {len(characters)} Hán tự khác nhau từ các mục từ; không suy âm đọc riêng từ pinyin của cả từ.',
               f'- {len(missing)} văn bản khác nhau chưa tìm thấy audio, gồm từ/ví dụ/hội thoại. Đây không phải số lượt API đã duyệt.',
               '- Audio có file chưa đồng nghĩa đã nghe kiểm tra đúng phát âm/ngữ cảnh.',
               '- Giữ các lần xuất hiện theo bài và các nghĩa khác nhau; không tự gộp từ đa âm.',
               '- Toàn bộ mục giữ trạng thái needs_review; đủ trường không đồng nghĩa đúng ngữ nghĩa.',
               '- Pinyin không có dấu có thể là thanh nhẹ hợp lệ; cần xét ngữ cảnh.', '',
               '## Tệp để sử dụng', '',
               '- vocabulary-review.csv: mở Excel để duyệt pinyin và nghĩa Việt.',
               '- vocabulary.json / sentences.json / grammar.json / characters.json: kho liên kết bằng ID.',
               '- sources.json: tài liệu và mục bên trong ZIP, chưa bóc các ZIP/RAR lồng nhau.',
               '- dictionary-reference.json: tham chiếu CC-CEDICT độc lập; chưa tự sửa nghĩa Việt.',
               '- missing-audio.json: hàng đợi cần duyệt trước khi tạo giọng đọc.', '',
               '## Nguồn bổ sung và quyền sử dụng', '',
               '- CC-CEDICT / MDBG: https://www.mdbg.net/chinese/dictionary?page=cc-cedict — CC BY-SA 4.0. Ghi nguồn, giữ giấy phép và chia sẻ phần dữ liệu phái sinh theo giấy phép.',
               '- Hanzi Writer Data: https://github.com/chanind/hanzi-writer-data — Arphic Public License. Trạng thái và đường dẫn local theo từng chữ trong characters.json; giấy phép trong data/hanzi-strokes/ARPHICPL.TXT.',
               '- Tài liệu/MP3 giáo trình trong máy: chưa xác minh quyền phân phối công khai; chỉ lập chỉ mục nội bộ.', '',
               '## Phần cần hoàn thiện', '',
               '1. Duyệt nghĩa Việt và pinyin theo từng từ trong ngữ cảnh; ưu tiên mục có cờ issues.',
               '2. Biên soạn ví dụ/hội thoại đời sống còn thiếu, đối chiếu âm đọc đa âm/thanh nhẹ.',
               '3. Tải nét chữ phù hợp danh sách characters.json, kèm giấy phép.',
               '4. Nghe kiểm tra audio có sẵn; chỉ tạo audio từ danh sách đã duyệt.',
               '5. HSK6/thương mại và các nguồn bổ sung mới được kiểm kê, chưa trích nội dung.', '']
    (OUT / 'README.md').write_text('\n'.join(report), encoding='utf-8')
    print(json.dumps({'levels': summary, 'characters': len(characters), 'missing_audio_texts': len(missing)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-cedict', action='store_true', help='Download free CC-CEDICT reference once; use cache subsequently')
    build(parser.parse_args().with_cedict)
