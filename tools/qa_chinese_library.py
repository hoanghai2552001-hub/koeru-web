"""Validate local library links/assets; report release blockers separately."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/chinese-library'


def main():
    read = lambda name: json.loads((OUT / name).read_text(encoding='utf-8'))
    vocab, sentences, chars = [read(n + '.json') for n in ('vocabulary', 'sentences', 'characters')]
    errors = []
    ids = [r['id'] for r in vocab + sentences]
    if len(ids) != len(set(ids)):
        errors.append('duplicate_record_ids')
    word_ids = {r['id'] for r in vocab}
    sentence_ids = {r['id'] for r in sentences}
    char_ids = {r['hanzi'] for r in chars}
    for word in vocab:
        if not all(word.get(k) for k in ('hanzi', 'pinyin', 'meaning_vi', 'level_system')):
            errors.append(word['id'] + ': missing required fields')
        if not set(word['character_ids']) <= char_ids or not set(word['example_ids']) <= sentence_ids:
            errors.append(word['id'] + ': broken links')
    for row in sentences:
        if row.get('vocab_id') and row['vocab_id'] not in word_ids:
            errors.append(row['id'] + ': missing vocabulary')
    for row in vocab + sentences:
        if row['audio']['path']:
            path = (ROOT / row['audio']['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or not path.stat().st_size:
                errors.append(row['id'] + ': invalid audio path')
    for char in chars:
        path = char.get('stroke_data_path')
        if not path:
            errors.append(char['hanzi'] + ': missing strokes')
            continue
        stroke = json.loads((ROOT / path).read_text(encoding='utf-8'))
        if not stroke.get('strokes') or len(stroke['strokes']) != len(stroke.get('medians', [])):
            errors.append(char['hanzi'] + ': invalid stroke data')
    report = {
        'errors': errors, 'vocab_records': len(vocab), 'sentence_records': len(sentences),
        'characters': len(chars),
        'missing_audio_records': sum(not r['audio']['path'] for r in vocab + sentences),
        'unreviewed_records': sum(r.get('review_status') != 'approved' for r in vocab + sentences),
        'public_release_ready': False,
        'limitations': ['File checks do not verify pronunciation.', 'Source rights and teaching review remain required.']
    }
    (OUT / 'qa-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
