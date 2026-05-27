// kanji-romaji.js — Romaji → Kana converter + fuzzy match helpers.
// Vanilla JS (no React, no Babel needed). Exposes window.KMRomaji.

(function () {
  // Hepburn romaji → hiragana (covers basic + youon + sokuon)
  const ROMAJI_TABLE = {
    'a':'あ','i':'い','u':'う','e':'え','o':'お',
    'ka':'か','ki':'き','ku':'く','ke':'け','ko':'こ',
    'ga':'が','gi':'ぎ','gu':'ぐ','ge':'げ','go':'ご',
    'sa':'さ','shi':'し','si':'し','su':'す','se':'せ','so':'そ',
    'za':'ざ','ji':'じ','zi':'じ','zu':'ず','ze':'ぜ','zo':'ぞ',
    'ta':'た','chi':'ち','ti':'ち','tsu':'つ','tu':'つ','te':'て','to':'と',
    'da':'だ','di':'ぢ','du':'づ','de':'で','do':'ど',
    'na':'な','ni':'に','nu':'ぬ','ne':'ね','no':'の',
    'ha':'は','hi':'ひ','fu':'ふ','hu':'ふ','he':'へ','ho':'ほ',
    'ba':'ば','bi':'び','bu':'ぶ','be':'べ','bo':'ぼ',
    'pa':'ぱ','pi':'ぴ','pu':'ぷ','pe':'ぺ','po':'ぽ',
    'ma':'ま','mi':'み','mu':'む','me':'め','mo':'も',
    'ya':'や','yu':'ゆ','yo':'よ',
    'ra':'ら','ri':'り','ru':'る','re':'れ','ro':'ろ',
    'wa':'わ','wo':'を','wi':'ゐ','we':'ゑ',
    'n':'ん','nn':'ん',
    // youon (combos)
    'kya':'きゃ','kyu':'きゅ','kyo':'きょ',
    'sha':'しゃ','shu':'しゅ','sho':'しょ','sya':'しゃ','syu':'しゅ','syo':'しょ',
    'cha':'ちゃ','chu':'ちゅ','cho':'ちょ','tya':'ちゃ','tyu':'ちゅ','tyo':'ちょ',
    'nya':'にゃ','nyu':'にゅ','nyo':'にょ',
    'hya':'ひゃ','hyu':'ひゅ','hyo':'ひょ',
    'mya':'みゃ','myu':'みゅ','myo':'みょ',
    'rya':'りゃ','ryu':'りゅ','ryo':'りょ',
    'gya':'ぎゃ','gyu':'ぎゅ','gyo':'ぎょ',
    'ja':'じゃ','ju':'じゅ','jo':'じょ','jya':'じゃ','jyu':'じゅ','jyo':'じょ',
    'bya':'びゃ','byu':'びゅ','byo':'びょ',
    'pya':'ぴゃ','pyu':'ぴゅ','pyo':'ぴょ',
    // long vowels
    'aa':'ああ','ii':'いい','uu':'うう','ee':'ええ','oo':'おお','ou':'おう','ei':'えい',
  };

  // Convert romaji string to hiragana. Greedy longest-match.
  function romajiToHiragana(str) {
    if (!str) return '';
    let s = str.toLowerCase().trim();
    let out = '';
    let i = 0;
    while (i < s.length) {
      // sokuon: double consonant (not 'n') → っ + rest
      const c = s[i], n = s[i+1];
      if (c === n && c !== 'a' && c !== 'i' && c !== 'u' && c !== 'e' && c !== 'o' && c !== 'n') {
        out += 'っ';
        i += 1;
        continue;
      }
      // 'n' before consonant (not n/y/vowel) → ん
      if (c === 'n' && n && !'aiueoyn'.includes(n)) {
        out += 'ん'; i += 1; continue;
      }
      // try longest match first (4, 3, 2, 1 chars)
      let matched = false;
      for (let len = Math.min(4, s.length - i); len >= 1; len--) {
        const chunk = s.slice(i, i + len);
        if (ROMAJI_TABLE[chunk]) {
          out += ROMAJI_TABLE[chunk];
          i += len;
          matched = true;
          break;
        }
      }
      if (!matched) {
        // unknown char — pass through
        out += s[i];
        i += 1;
      }
    }
    return out;
  }

  // Hiragana ↔ Katakana converters (codepoint shift)
  function hiraToKata(s) {
    return s.replace(/[\u3041-\u3096]/g, ch => String.fromCodePoint(ch.codePointAt(0) + 0x60));
  }
  function kataToHira(s) {
    return s.replace(/[\u30A1-\u30F6]/g, ch => String.fromCodePoint(ch.codePointAt(0) - 0x60));
  }

  // Vietnamese: strip diacritics for fuzzy match.
  // E.g. "học sinh" → "hoc sinh"
  function stripVi(s) {
    if (!s) return '';
    return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D');
  }

  // Build a normalized search haystack for an item. Includes:
  //   - raw text
  //   - hiragana + katakana variants
  //   - vi without diacritics
  function buildHaystack(parts) {
    const tokens = new Set();
    for (const p of parts) {
      if (!p) continue;
      const lower = String(p).toLowerCase();
      tokens.add(lower);
      tokens.add(stripVi(lower));
      // also store kana converted to other form (for matching katakana onyomi against hiragana queries)
      if (/[\u3040-\u309F]/.test(lower)) tokens.add(hiraToKata(lower));
      if (/[\u30A0-\u30FF]/.test(lower)) tokens.add(kataToHira(lower));
    }
    return [...tokens].join(' ');
  }

  // Convert a query into multiple search keys:
  //   "gakusei" → ['gakusei', 'がくせい', 'ガクセイ']
  //   "sinh"    → ['sinh', 'sinh' (already deburred)]
  //   "学生"     → ['学生']
  function expandQuery(q) {
    if (!q) return [];
    const lower = q.toLowerCase().trim();
    const out = new Set([lower]);
    out.add(stripVi(lower));
    // if ASCII letters, try romaji → kana
    if (/^[a-z\s-]+$/.test(lower)) {
      const hira = romajiToHiragana(lower);
      if (hira !== lower) { out.add(hira); out.add(hiraToKata(hira)); }
    }
    // if hiragana, also try katakana
    if (/[\u3040-\u309F]/.test(lower)) out.add(hiraToKata(lower));
    if (/[\u30A0-\u30FF]/.test(lower)) out.add(kataToHira(lower));
    return [...out].filter(Boolean);
  }

  // Score how well an item matches the query keys.
  // Higher = better. Returns 0 if no match.
  function scoreMatch(haystack, keys, primary) {
    if (!keys.length) return 0;
    const hay = haystack.toLowerCase();
    const prim = (primary || '').toLowerCase();
    let best = 0;
    for (const key of keys) {
      const k = key.toLowerCase();
      if (!k) continue;
      // exact primary match → highest
      if (prim === k) return 1000;
      // primary starts with key
      if (prim.startsWith(k)) best = Math.max(best, 500 + (10 - Math.min(10, prim.length - k.length)));
      // haystack contains key
      else if (hay.includes(k)) best = Math.max(best, 100 + Math.max(0, 20 - k.length));
    }
    return best;
  }

  window.KMRomaji = {
    toHiragana: romajiToHiragana,
    hiraToKata, kataToHira,
    stripVi,
    buildHaystack,
    expandQuery,
    scoreMatch,
  };
})();
