#!/usr/bin/env python3
"""
Download pinyin audio MP3 files for KOERU Pinyin Speed.
Source: https://github.com/davinfifield/mp3-chinese-pinyin-sound (Unlicense)

Usage (from project root):
    python tools/download_pinyin_audio.py

Downloads only the syllables actually used in js/pinyin-data.js.
Output: audio/pinyin/<key>.mp3  (e.g. ni3.mp3, hao3.mp3)
"""
import re, os, time, urllib.request, urllib.error, string

PINYIN_DATA_FILE = 'js/pinyin-data.js'
AUDIO_DIR = 'audio/pinyin'
BASE_URL = 'https://raw.githubusercontent.com/davinfifield/mp3-chinese-pinyin-sound/master/mp3/'

TONE_MAP = {
    'ā':('a',1),'á':('a',2),'ǎ':('a',3),'à':('a',4),
    'ē':('e',1),'é':('e',2),'ě':('e',3),'è':('e',4),
    'ī':('i',1),'í':('i',2),'ǐ':('i',3),'ì':('i',4),
    'ō':('o',1),'ó':('o',2),'ǒ':('o',3),'ò':('o',4),
    'ū':('u',1),'ú':('u',2),'ǔ':('u',3),'ù':('u',4),
    'ǖ':('v',1),'ǘ':('v',2),'ǚ':('v',3),'ǜ':('v',4),
}

import re as _re
_PUNCT = str.maketrans('', '', '!?.,。！？、·')

def syllable_to_key(syl):
    syl = syl.translate(_PUNCT).lower()
    tone, bare = 5, ''
    for ch in syl:
        if ch in TONE_MAP:
            bare += TONE_MAP[ch][0]
            tone = TONE_MAP[ch][1]
        else:
            bare += ch
    return f'{bare}{tone}'

def pinyin_to_keys(pinyin_str):
    # strip punctuation, split on spaces, skip keys > 7 chars (unsplit multi-syllable)
    cleaned = pinyin_str.translate(_PUNCT).strip()
    return [k for k in (syllable_to_key(p) for p in cleaned.split()) if len(k) <= 7]

def extract_keys_from_data(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    pinyin_vals = re.findall(r'pinyin:"([^"]+)"', content)
    keys = set()
    for py in pinyin_vals:
        for k in pinyin_to_keys(py):
            keys.add(k)
    return sorted(keys)

def download_file(key, dest):
    url = BASE_URL + f'{key}.mp3'
    try:
        urllib.request.urlretrieve(url, dest)
        return 'ok'
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 'missing'
        return f'error:{e.code}'
    except Exception as e:
        return f'error:{e}'

def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    keys = extract_keys_from_data(PINYIN_DATA_FILE)
    print(f'Found {len(keys)} unique audio keys from pinyin-data.js\n')

    ok = skip = missing = fail = 0
    for key in keys:
        dest = os.path.join(AUDIO_DIR, f'{key}.mp3')
        if os.path.exists(dest):
            skip += 1
            continue
        result = download_file(key, dest)
        if result == 'ok':
            print(f'  ✓  {key}.mp3')
            ok += 1
        elif result == 'missing':
            print(f'  -  {key}.mp3  (not in source repo)')
            missing += 1
        else:
            print(f'  ✗  {key}.mp3  ({result})')
            fail += 1
        time.sleep(0.05)  # be polite to GitHub

    print(f'\nDone: {ok} downloaded, {skip} already existed, {missing} not in source, {fail} errors')
    if missing:
        print('\nNote: missing files are usually neutral-tone syllables (e.g. men5).')
        print('The game gracefully skips missing audio.')

if __name__ == '__main__':
    main()
