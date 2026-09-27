"""Vendor only the Hanzi Writer strokes used by HSK1–3, with upstream licenses.
Downloads npm archives as data; never installs or executes package scripts.
"""
import base64
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def package(name, version):
    meta = json.loads(fetch(f'https://registry.npmjs.org/{name}/{version}'))
    raw = fetch(meta['dist']['tarball'])
    integrity = meta['dist']['integrity']
    algorithm, digest = integrity.split('-', 1)
    assert base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() == digest
    return tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz'), meta


def main():
    chars = set()
    for level in (1, 2, 3):
        for path in (ROOT / 'database' / f'hsk{level}').glob('lesson*.json'):
            for word in json.loads(path.read_text(encoding='utf-8'))['vocab']:
                chars.update(re.findall(r'[一-鿿]', word['h']))
    dest = ROOT / 'data' / 'hanzi-strokes'
    dest.mkdir(parents=True, exist_ok=True)
    archive, meta = package('hanzi-writer-data', 'latest')
    members = {Path(m.name).name: m for m in archive.getmembers() if m.isfile()}
    missing = []
    for char in sorted(chars):
        member = members.get(char + '.json')
        if member is None:
            missing.append(char)
            continue
        raw = archive.extractfile(member).read()
        data = json.loads(raw)
        assert data['strokes'] and len(data['strokes']) == len(data['medians']), char
        (dest / (char + '.json')).write_bytes(raw)
    (dest / 'ARPHICPL.TXT').write_bytes(archive.extractfile(members['ARPHICPL.TXT']).read())
    manifest = {'source': 'https://github.com/chanind/hanzi-writer-data', 'version': meta['version'],
                'integrity': meta['dist']['integrity'], 'license': 'Arphic Public License',
                'characters': sorted(chars - set(missing)), 'missing': missing}
    (dest / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    archive.close()
    archive, meta = package('hanzi-writer', '3.5.0')
    vendor = ROOT / 'js' / 'vendor'
    vendor.mkdir(exist_ok=True)
    for source, target in [('package/dist/hanzi-writer.min.js', 'hanzi-writer.min.js'),
                           ('package/LICENSE', 'hanzi-writer-LICENSE.txt')]:
        (vendor / target).write_bytes(archive.extractfile(source).read())
    archive.close()
    print(json.dumps({'strokes': len(manifest['characters']), 'missing': missing,
                      'writer': meta['version']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
