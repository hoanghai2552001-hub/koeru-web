// kanji-map-panel.jsx — Glass detail panel for selected kanji/vocab.

// Split a kana string into mora (small kana attach to preceding mora).
function splitMora(kana) {
  if (!kana) return [];
  const small = new Set('ゃゅょャュョぁぃぅぇぉァィゥェォ');
  const out = [];
  for (const ch of kana) {
    if (small.has(ch) && out.length) out[out.length - 1] += ch;
    else out.push(ch);
  }
  return out;
}

// Compute H/L pattern for a given pitch type.
// Returns array of 'H'|'L', length = mora.length (we don't render the particle).
function pitchPattern(moraCount, pitch) {
  if (moraCount === 0) return [];
  const arr = new Array(moraCount);
  if (pitch === 0) {
    // heiban: first L, rest H (stays H on particle)
    arr[0] = 'L';
    for (let i = 1; i < moraCount; i++) arr[i] = 'H';
  } else if (pitch === 1) {
    // atamadaka: first H, rest L
    arr[0] = 'H';
    for (let i = 1; i < moraCount; i++) arr[i] = 'L';
  } else {
    // nakadaka or odaka: first L, then H until pitch, then L
    arr[0] = 'L';
    for (let i = 1; i < moraCount; i++) arr[i] = i < pitch ? 'H' : 'L';
  }
  return arr;
}

const PitchAccent = ({ reading, pitch }) => {
  const mora = splitMora(reading);
  if (!mora.length) return null;
  const pattern = pitchPattern(mora.length, pitch);
  const label = pitch === 0 ? 'heiban (平板)'
              : pitch === 1 ? 'atamadaka (頭高)'
              : pitch === mora.length ? 'odaka (尾高)'
              : 'nakadaka (中高)';
  // build SVG contour line
  const w = mora.length * 32 + 16;
  const h = 36;
  const pts = pattern.map((p, i) => ({
    x: 16 + i * 32,
    y: p === 'H' ? 8 : 24,
  }));
  return (
    <div className="km-pitch">
      <div className="km-section-title">
        Trọng âm
        <span className="km-section-count">[{pitch}] {label}</span>
      </div>
      <div className="km-pitch-canvas">
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
          {/* contour line */}
          <polyline
            points={pts.map(p => `${p.x},${p.y}`).join(' ')}
            fill="none" stroke="var(--hanko)" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round"
          />
          {pts.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r="4"
              fill={pattern[i] === 'H' ? 'var(--hanko)' : '#fff'}
              stroke="var(--hanko)" strokeWidth="2" />
          ))}
        </svg>
        <div className="km-pitch-mora">
          {mora.map((m, i) => (
            <span key={i} className={pattern[i] === 'H' ? 'is-h' : 'is-l'}>{m}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

const KanjiPanel = ({ data, selectedId, onSelect, onClose }) => {
  const item = useMemo(() => {
    if (!selectedId) return null;
    return data.kanji.find(k => k.id === selectedId) || data.vocab.find(v => v.id === selectedId);
  }, [selectedId, data]);

  const isVocab = item && item.kanji && Array.isArray(item.kanji);

  // compounds for kanji (vocab that contain it); for vocab: sibling vocab + component kanji
  const related = useMemo(() => {
    if (!item) return { compounds: [], examples: [] };
    if (isVocab) {
      const sibling = data.vocab.filter(v => v.id !== item.id && v.kanji.some(k => item.kanji.includes(k)));
      return { compounds: sibling.slice(0, 10), components: item.kanji.map(k => data.kanji.find(x => x.id === k)).filter(Boolean) };
    }
    const compounds = data.vocab.filter(v => v.kanji.includes(item.id));
    return { compounds };
  }, [item, data, isVocab]);

  // ONYOMI FAMILY — other kanji that share at least one onyomi with this one
  const onyomiFamily = useMemo(() => {
    if (!item || isVocab || !item.onyomi?.length) return [];
    const myOn = new Set(item.onyomi);
    return data.kanji
      .filter(k => k.id !== item.id && k.onyomi?.some(o => myOn.has(o)))
      .map(k => ({
        ...k,
        shared: k.onyomi.filter(o => myOn.has(o))
      }))
      .slice(0, 12);
  }, [item, data, isVocab]);

  // a representative example: first vocab example that involves this kanji
  const exampleVocab = useMemo(() => {
    if (!item) return null;
    if (isVocab) return item;
    return related.compounds.find(c => c.example_jp);
  }, [item, related, isVocab]);

  // pronounce via browser speechSynthesis (ja-JP)
  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window)) {
      alert('Trình duyệt không hỗ trợ phát âm tự động.');
      return;
    }
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'ja-JP';
    utter.rate = 0.85;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }, []);

  // bookmark (localStorage)
  const [bookmarked, setBookmarked] = useState(false);
  useEffect(() => {
    if (!item) return;
    const set = new Set(JSON.parse(localStorage.getItem('km_bookmarks') || '[]'));
    setBookmarked(set.has(item.id));
  }, [item]);
  const toggleBookmark = () => {
    if (!item) return;
    const set = new Set(JSON.parse(localStorage.getItem('km_bookmarks') || '[]'));
    if (set.has(item.id)) set.delete(item.id); else set.add(item.id);
    localStorage.setItem('km_bookmarks', JSON.stringify([...set]));
    setBookmarked(set.has(item.id));
  };

  // mocked progress: how many compounds of this kanji are "learned"
  const progress = useMemo(() => {
    if (!item) return null;
    const learned = JSON.parse(localStorage.getItem('km_learned') || '[]');
    const all = isVocab ? related.compounds.length + 1 : related.compounds.length;
    if (all === 0) return null;
    const done = (isVocab ? [item, ...related.compounds] : related.compounds)
      .filter(v => learned.includes(v.id)).length;
    return { done, total: all };
  }, [item, related, isVocab]);

  if (!item) {
    return (
      <aside className="km-detail" data-screen-label="detail-panel">
        <div className="km-detail-grip" />
        <div className="km-detail-empty">
          <div className="km-detail-empty-icon">字</div>
          <div>Chọn 1 chữ trong bản đồ<br/>để xem chi tiết.</div>
          <div style={{ marginTop: 4, fontSize: 12 }}>Hoặc dùng search ở panel trái.</div>
        </div>
      </aside>
    );
  }

  return (
    <aside className="km-detail" data-screen-label="detail-panel">
      <div className="km-detail-grip" onClick={onClose} />

      {/* HEADER */}
      <div className="km-detail-header">
        <div className={`km-detail-glyph ${isVocab ? 'is-vocab' : ''}`}>{item.id}</div>
        <div className="km-detail-meta">
          <div className="km-detail-hanviet">
            {isVocab ? item.reading : item.han_viet}
          </div>
          <div className="km-detail-meaning">{item.meaning}</div>
          <span className={`km-detail-jlpt lvl-${item.jlpt}`}>JLPT {item.jlpt}</span>
        </div>
        <button className="km-btn is-icon is-ghost" onClick={() => speak(item.id)} title="Phát âm">
          🔊
        </button>
      </div>

      {/* MNEMONIC (kanji only) */}
      {!isVocab && item.mnemonic ? (
        <div className="km-mnemonic">
          <div className="km-section-title" style={{ marginBottom:6, color:'var(--hanko)' }}>
            ✦ Cách nhớ
          </div>
          <div className="km-mnemonic-text">{item.mnemonic}</div>
        </div>
      ) : null}

      {/* PITCH ACCENT (vocab only) */}
      {isVocab && typeof item.pitch === 'number' ? (
        <PitchAccent reading={item.reading} pitch={item.pitch} />
      ) : null}

      {/* READINGS (kanji only) */}
      {!isVocab && (item.onyomi?.length || item.kunyomi?.length) ? (
        <div className="km-readings">
          {item.onyomi?.length ? (<>
            <div className="km-reading-label">音</div>
            <div className="km-reading-value">{item.onyomi.join('・')}</div>
          </>) : null}
          {item.kunyomi?.length ? (<>
            <div className="km-reading-label">訓</div>
            <div className="km-reading-value">{item.kunyomi.join('・')}</div>
          </>) : null}
          <div className="km-reading-label">画</div>
          <div className="km-reading-value" style={{ fontFamily: 'var(--font-sans)', color: 'var(--ink-soft)' }}>
            {item.stroke} nét
            {item.freq_rank ? <span style={{ marginLeft:10, color:'var(--ink-faint)' }}>· top {item.freq_rank} thường gặp</span> : null}
          </div>
        </div>
      ) : null}

      {/* STROKE ORDER (kanji only) */}
      {!isVocab && window.StrokeOrder ? (
        <StrokeOrder kanji={item.id} size={140} />
      ) : null}

      {/* RADICAL + COMPONENTS (kanji only) */}
      {!isVocab && item.radical && data.radicals?.[item.radical] ? (
        <div>
          <div className="km-section-title">Bộ thủ</div>
          <div className="km-radical" onClick={() => {
            // surface other kanji with same radical
            const same = data.kanji.filter(k => k.radical === item.radical && k.id !== item.id);
            if (same.length) onSelect(same[0].id);
          }}>
            <div className="km-radical-glyph">{item.radical}</div>
            <div className="km-radical-meta">
              <div className="km-radical-name">bộ {data.radicals[item.radical].han_viet}</div>
              <div className="km-radical-desc">
                {data.radicals[item.radical].meaning} · {data.radicals[item.radical].strokes} nét
              </div>
            </div>
          </div>
          {item.components?.length > 1 ? (
            <div style={{ marginTop:10 }}>
              <div className="km-section-title" style={{ marginBottom:6 }}>Cấu tạo</div>
              <div className="km-components">
                {item.components.map((c, i) => {
                  const inData = data.kanji.find(k => k.id === c);
                  return (
                    <div key={i} className="km-component"
                      onClick={() => inData && onSelect(c)}
                      title={inData ? `${inData.han_viet} — ${inData.meaning}` : 'thành phần'}
                      style={{ cursor: inData ? 'pointer' : 'default' }}>
                      {c}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}

      {/* ONYOMI FAMILY (kanji only) — kanji sharing the same onyomi */}
      {!isVocab && onyomiFamily.length ? (
        <div>
          <div className="km-section-title">
            Cùng âm 音 (onyomi)
            <span className="km-section-count">{onyomiFamily.length}</span>
          </div>
          <div className="km-onyomi-family">
            {onyomiFamily.map(k => (
              <div key={k.id} className="km-onyomi-pill" onClick={() => onSelect(k.id)}
                title={`${k.han_viet} — ${k.meaning}`}>
                <div className={`km-onyomi-pill-glyph lvl-${k.jlpt}`}>{k.id}</div>
                <div className="km-onyomi-pill-text">
                  <span className="km-onyomi-pill-reading">{k.shared.join('・')}</span>
                  <span className="km-onyomi-pill-hanviet">{k.han_viet} · {k.jlpt}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* COMPONENT KANJI (vocab only) */}
      {isVocab && related.components?.length ? (
        <div>
          <div className="km-section-title">
            Kanji thành phần <span className="km-section-count">{related.components.length}</span>
          </div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
            {related.components.map(k => (
              <button key={k.id} className="km-btn"
                style={{ padding:'6px 10px', display:'flex', gap:8, alignItems:'center' }}
                onClick={() => onSelect(k.id)}>
                <span style={{ fontFamily:'var(--font-kanji)', fontSize:20, fontWeight:700 }}>{k.id}</span>
                <span style={{ display:'flex', flexDirection:'column', alignItems:'flex-start', lineHeight:1.1 }}>
                  <span style={{ fontSize:12 }}>{k.han_viet}</span>
                  <span style={{ fontSize:10, color:'var(--ink-faint)' }}>{k.jlpt}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {/* EXAMPLE */}
      {exampleVocab && exampleVocab.example_jp && (
        <div>
          <div className="km-section-title">Ví dụ</div>
          <div className="km-example">
            <div className="km-example-jp"
              dangerouslySetInnerHTML={{ __html: highlightInExample(exampleVocab.example_jp, item.id) }} />
            <div className="km-example-vi">{exampleVocab.example_vi}</div>
            <button className="km-btn is-ghost"
              style={{ padding:'4px 8px', fontSize:12, marginTop:6 }}
              onClick={() => speak(exampleVocab.example_jp)}>
              🔊 phát âm câu
            </button>
          </div>
        </div>
      )}

      {/* COMPOUNDS */}
      {related.compounds?.length ? (
        <div>
          <div className="km-section-title">
            {isVocab ? 'Từ liên quan' : 'Từ ghép'}
            <span className="km-section-count">{related.compounds.length}</span>
          </div>
          <div className="km-compounds">
            {related.compounds.map(c => (
              <div key={c.id} className="km-compound" onClick={() => onSelect(c.id)}>
                <div className="km-compound-text">
                  <div className="km-compound-word">{c.id}</div>
                  <div className="km-compound-reading">{c.reading}</div>
                  <div className="km-compound-meaning">{c.meaning}</div>
                </div>
                <span className={`km-compound-jlpt lvl-${c.jlpt}`}>{c.jlpt}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* PROGRESS */}
      {progress && progress.total > 0 ? (
        <div className="km-progress">
          <div className="km-section-title" style={{ marginBottom: 0 }}>Tiến độ chữ này</div>
          <div className="km-progress-bar">
            <div className="km-progress-fill"
              style={{ width: `${Math.round((progress.done / progress.total) * 100)}%` }} />
          </div>
          <div className="km-progress-meta">
            <span>Đã học {progress.done}/{progress.total} từ</span>
            <span>{Math.round((progress.done / progress.total) * 100)}%</span>
          </div>
        </div>
      ) : null}

      {/* ACTIONS */}
      <div className="km-actions">
        <button className="km-btn is-primary" style={{ flex: 1 }} onClick={() => markLearned(item.id)}>
          ＋ Học từ này
        </button>
        <button className="km-btn is-icon" onClick={toggleBookmark}
          style={{ color: bookmarked ? 'var(--hanko)' : 'inherit' }}>
          {bookmarked ? '♥' : '♡'}
        </button>
      </div>
    </aside>
  );
};

function highlightInExample(text, kanjiId) {
  if (!text || !kanjiId) return text;
  // wrap occurrences of kanjiId in <b>
  return text.split(kanjiId).map(s =>
    s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))
  ).join(`<b>${kanjiId}</b>`);
}

function markLearned(id) {
  const set = new Set(JSON.parse(localStorage.getItem('km_learned') || '[]'));
  set.add(id);
  localStorage.setItem('km_learned', JSON.stringify([...set]));
  // force a re-render via a custom event
  window.dispatchEvent(new CustomEvent('km-learned-updated'));
}

window.KanjiPanel = KanjiPanel;
