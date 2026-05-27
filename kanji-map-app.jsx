// kanji-map-app.jsx — main shell: top bar + controls + graph + panel + recent.

const RECENT_MAX = 12;
// N1 chưa có data → chỉ hiện N5–N2
const ALL_LEVELS = ['N5', 'N4', 'N3', 'N2'];

const KanjiMapApp = () => {
  const data = window.KANJI_DATA;

  // Guard: nếu data chưa load (script lỗi/chậm) → hiển thị lỗi thay vì crash
  if (!data || !data.kanji) {
    return (
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center',
                    height:'100vh', flexDirection:'column', gap:16, fontFamily:'sans-serif' }}>
        <div style={{ fontSize:48 }}>⚠️</div>
        <div style={{ fontSize:18, fontWeight:700 }}>Không tải được dữ liệu Kanji Map</div>
        <div style={{ color:'#888', fontSize:14 }}>Thử tải lại trang (F5)</div>
        <button onClick={() => location.reload()}
          style={{ marginTop:8, padding:'8px 20px', borderRadius:8, border:'1px solid #ccc', cursor:'pointer' }}>
          🔄 Tải lại
        </button>
      </div>
    );
  }

  // initial selection from URL ?k=生
  const initialFromURL = (() => {
    try {
      const p = new URLSearchParams(window.location.search);
      return p.get('k') || null;
    } catch { return null; }
  })();

  const [selectedId, setSelectedId] = useState(initialFromURL);
  const [jlptFilter, setJlptFilter] = useState(['N5', 'N4', 'N3', 'N2']);
  const [viewMode, setViewMode] = useState('2D');
  const [expanded, setExpanded] = useState(false);
  const [recent, setRecent] = useState(() => JSON.parse(localStorage.getItem('km_recent') || '[]'));
  const [search, setSearch] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [mobilePanelOpen, setMobilePanelOpen] = useState(false);
  const [size, setSize] = useState({ w: 800, h: 600 });
  const graphWrapRef = useRef(null);

  // measure graph wrap
  useEffect(() => {
    const measure = () => {
      const el = graphWrapRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      setSize({ w: r.width, h: r.height });
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  // record to recent on selection (kanji only — vocab gets selected too but we keep both)
  const select = useCallback((id) => {
    if (!id) {
      setSelectedId(null);
      // clear URL
      const url = new URL(window.location.href);
      url.searchParams.delete('k');
      window.history.pushState({}, '', url);
      return;
    }
    setSelectedId(id);
    setExpanded(false);
    setShowSearchResults(false);
    setMobilePanelOpen(true);
    // push to URL (skip duplicate)
    const url = new URL(window.location.href);
    if (url.searchParams.get('k') !== id) {
      url.searchParams.set('k', id);
      window.history.pushState({ k: id }, '', url);
    }
    setRecent(prev => {
      const next = [id, ...prev.filter(x => x !== id)].slice(0, RECENT_MAX);
      localStorage.setItem('km_recent', JSON.stringify(next));
      return next;
    });
  }, []);

  // browser back/forward → restore selection
  useEffect(() => {
    const onPop = () => {
      const p = new URLSearchParams(window.location.search);
      const k = p.get('k');
      setSelectedId(k || null);
      setExpanded(false);
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  // search index — builds haystack with romaji/katakana/diacritic-less variants
  const searchIndex = useMemo(() => {
    const idx = [];
    const KM = window.KMRomaji || { buildHaystack: parts => parts.filter(Boolean).join(' ').toLowerCase() };
    data.kanji.forEach(k => {
      idx.push({
        id: k.id, type: 'kanji', jlpt: k.jlpt,
        primary: k.id, secondary: `${k.han_viet} · ${k.meaning}`,
        haystack: KM.buildHaystack([
          k.id, k.han_viet, k.meaning,
          ...(k.onyomi||[]), ...(k.kunyomi||[])
        ])
      });
    });
    data.vocab.forEach(v => {
      idx.push({
        id: v.id, type: 'vocab', jlpt: v.jlpt,
        primary: v.id, secondary: `${v.reading} · ${v.meaning}`,
        haystack: KM.buildHaystack([v.id, v.reading, v.meaning])
      });
    });
    return idx;
  }, [data]);

  const searchResults = useMemo(() => {
    const q = search.trim();
    if (!q) return [];
    const KM = window.KMRomaji;
    // only include items in current JLPT filter
    const inFilter = (x) => jlptFilter.includes(x.jlpt);
    if (!KM) {
      const lower = q.toLowerCase();
      return searchIndex.filter(x => inFilter(x) && x.haystack.includes(lower)).slice(0, 20);
    }
    const keys = KM.expandQuery(q);
    return searchIndex
      .filter(inFilter)
      .map(x => ({ x, score: KM.scoreMatch(x.haystack, keys, x.id) }))
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 20)
      .map(({ x }) => x);
  }, [search, searchIndex, jlptFilter]);

  // keyboard: Cmd/Ctrl+K focuses search, Esc clears, ←/→ cycle recent
  useEffect(() => {
    const onKey = (e) => {
      // ignore when typing in inputs
      const inInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        document.querySelector('.km-search input')?.focus();
        return;
      }
      if (e.key === 'Escape') {
        setShowSearchResults(false);
        if (document.activeElement?.tagName === 'INPUT') document.activeElement.blur();
        return;
      }
      if (inInput) return;
      // arrow navigation through recent
      if ((e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        const r = JSON.parse(localStorage.getItem('km_recent') || '[]');
        if (r.length < 2) return;
        e.preventDefault();
        const cur = r.indexOf(selectedId);
        const dir = e.key === 'ArrowRight' ? -1 : 1;  // → forward in history = idx-1
        const next = (cur < 0 ? 0 : (cur + dir + r.length) % r.length);
        select(r[next]);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selectedId, select]);

  // re-render when learned updates (so progress bar refreshes)
  const [, forceTick] = useState(0);
  useEffect(() => {
    const h = () => forceTick(t => t + 1);
    window.addEventListener('km-learned-updated', h);
    return () => window.removeEventListener('km-learned-updated', h);
  }, []);

  // streak (mocked)
  const streak = 7;
  const xpToday = 120;

  const toggleLevel = (lvl) => {
    setJlptFilter(prev => prev.includes(lvl) ? prev.filter(x => x !== lvl) : [...prev, lvl]);
  };

  const visibleCounts = useMemo(() => {
    const k = data.kanji.filter(x => jlptFilter.includes(x.jlpt)).length;
    const v = data.vocab.filter(x => jlptFilter.includes(x.jlpt)).length;
    return { k, v, totalK: data.kanji.length, totalV: data.vocab.length };
  }, [data, jlptFilter]);

  return (
    <div className="km-app">

      {/* === TOP BAR === */}
      <div className="km-top">
        <div className="km-brand">
          <a href="./index.html" style={{ textDecoration:'none', color:'inherit', display:'flex', alignItems:'center', gap:8 }}>
            <img src="./koeru-logo.png" alt="KOERU" style={{ height:32, width:'auto' }} />
          </a>
          <span className="km-brand-sub">Bản đồ Kanji</span>
        </div>
        <div className="km-top-right">
          <span className="km-stat">Đang xem <b>{visibleCounts.k}</b>/{visibleCounts.totalK} chữ</span>
          <span style={{ color:'var(--hairline)' }}>·</span>
          <span className="km-stat"><b>{visibleCounts.v}</b>/{visibleCounts.totalV} từ ghép</span>
          {selectedId && (
            <button className="km-btn is-ghost" title="Sao chép link" style={{ marginLeft:8 }}
              onClick={(e) => {
                navigator.clipboard.writeText(window.location.href).catch(() => {});
                const btn = e.currentTarget;
                const oldText = btn.textContent;
                btn.textContent = '✓ đã copy';
                setTimeout(() => { btn.textContent = oldText; }, 1500);
              }}>
              🔗 share
            </button>
          )}
          <span className="km-btn is-ghost" style={{ marginLeft:4 }}>
            <a href="./index.html" style={{ color:'inherit', textDecoration:'none' }}>← Trang chủ</a>
          </span>
        </div>
      </div>

      {/* === CONTROLS PANEL (LEFT) === */}
      <aside className="km-controls">
        {/* search */}
        <div className="km-section km-section-search">
          <div className="km-label">Tìm kiếm</div>
          <div className="km-search">
            <span className="km-search-icon">🔍</span>
            <input
              type="text"
              value={search}
              onChange={e => { setSearch(e.target.value); setShowSearchResults(true); }}
              onFocus={() => setShowSearchResults(true)}
              onBlur={() => setTimeout(() => setShowSearchResults(false), 150)}
              placeholder="kanji · từ · hán việt · nghĩa…"
            />
            {search && (
              <button className="km-search-clear" onClick={() => { setSearch(''); setShowSearchResults(false); }}>×</button>
            )}
            {showSearchResults && searchResults.length > 0 && (
              <div className="km-search-results">
                {searchResults.map(r => (
                  <div key={r.type + r.id} className={`km-search-result km-search-result-${r.type}`}
                    onMouseDown={() => { select(r.id); setSearch(''); }}>
                    <div className="km-search-result-glyph">{r.primary}</div>
                    <div className="km-search-result-text">
                      <div className="km-search-result-primary">{r.secondary}</div>
                      <div className="km-search-result-meta">{r.type === 'kanji' ? 'Kanji' : 'Từ ghép'} · {r.jlpt}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {showSearchResults && search.trim() && searchResults.length === 0 && (
              <div className="km-search-results">
                <div className="km-search-result" style={{ cursor:'default', color:'var(--ink-faint)' }}>
                  Không tìm thấy "{search}"
                </div>
              </div>
            )}
          </div>
          <div className="km-help">
            <span className="km-kbd">⌘ K</span> tìm · <span className="km-kbd">←</span> <span className="km-kbd">→</span> đổi chữ · gõ <i>"gakusei"</i> hoặc <i>"hoc sinh"</i> cũng tìm được
          </div>
        </div>

        {/* JLPT filter */}
        <div className="km-section km-section-jlpt">
          <div className="km-label">Cấp độ JLPT</div>
          <div className="km-chips">
            {ALL_LEVELS.map(lvl => (
              <button key={lvl}
                className={`km-chip lvl-${lvl} ${jlptFilter.includes(lvl) ? 'is-on' : ''}`}
                onClick={() => toggleLevel(lvl)}>
                {lvl}
              </button>
            ))}
          </div>
          <div className="km-help">
            Viền node = cấp JLPT của chữ đó.
          </div>
        </div>

        {/* view mode */}
        <div className="km-section">
          <div className="km-label">Chế độ xem</div>
          <div className="km-segmented">
            <button className={viewMode === '2D' ? 'is-on' : ''} onClick={() => setViewMode('2D')}>2D Mindmap</button>
            <button className={viewMode === '3D' ? 'is-on' : ''} onClick={() => alert('3D view sắp ra mắt!\n\nTrong MVP này, 2D là chế độ chính.')}>3D 🌐</button>
          </div>
          <div className="km-help">
            Bản đồ 2D dùng để học. 3D explore mode sắp ra mắt.
          </div>
        </div>

        {/* mode shortcuts */}
        <div className="km-section">
          <div className="km-label">Bắt đầu nhanh</div>
          <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
            {[
              { id:'生', label:'Tâm: 生 (sinh)' },
              { id:'学', label:'Tâm: 学 (học)' },
              { id:'日', label:'Tâm: 日 (nhật)' },
            ].map(s => (
              <button key={s.id} className="km-btn" style={{ justifyContent:'flex-start' }}
                onClick={() => select(s.id)}>
                <span style={{ fontFamily:'var(--font-kanji)', fontSize:18, fontWeight:700, marginRight:6 }}>{s.id}</span>
                {s.label.replace(/^.*: /, '')}
              </button>
            ))}
            {selectedId && (
              <button className="km-btn" onClick={() => select(null)}>
                ← Quay về tổng quan
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* === GRAPH (CENTER) === */}
      <div className="km-graph-wrap" ref={graphWrapRef}
        style={{ gridArea:'graph', position:'relative' }}>
        <KanjiGraph
          data={data}
          jlptFilter={jlptFilter}
          selectedId={selectedId}
          onSelect={select}
          expanded={expanded}
          onExpandMore={() => setExpanded(true)}
          width={size.w} height={size.h}
        />
      </div>

      {/* === DETAIL PANEL (RIGHT) === */}
      <div className={mobilePanelOpen ? 'is-open km-detail-wrap' : 'km-detail-wrap'}
        style={{ display:'contents' }}>
        <div className={`km-detail-host ${mobilePanelOpen ? 'is-open' : ''}`}
          style={{ display:'contents' }}>
          <KanjiPanel data={data} selectedId={selectedId} onSelect={select}
            onClose={() => setMobilePanelOpen(false)} />
        </div>
      </div>

      {/* === RECENT RAIL (BOTTOM) === */}
      <div className="km-recent">
        <div className="km-recent-title">
          <span className="km-label">Gần đây</span>
          <span className="km-recent-title-sub">{recent.length || 0} chữ tuần này</span>
        </div>
        <div className="km-recent-list">
          {recent.length === 0 && (
            <span className="km-recent-empty">Chưa có chữ nào — click 1 node để bắt đầu khám phá.</span>
          )}
          {recent.map(id => {
            const k = data.kanji.find(x => x.id === id) || data.vocab.find(x => x.id === id);
            if (!k) return null;
            const isKanji = !k.kanji;
            return (
              <button key={id}
                className={`km-recent-item lvl-${k.jlpt} ${selectedId === id ? 'is-current' : ''}`}
                style={{ fontFamily: isKanji ? 'var(--font-kanji)' : 'var(--font-jp)',
                         fontSize: isKanji ? 20 : 13, width: isKanji ? 44 : 'auto',
                         padding: isKanji ? 0 : '0 12px', borderRadius: isKanji ? '50%' : '99px' }}
                onClick={() => select(id)}
                title={isKanji ? `${k.han_viet} — ${k.meaning}` : `${k.reading} — ${k.meaning}`}>
                {id}
              </button>
            );
          })}
        </div>
        <div className="km-streak">
          <div className="km-streak-num">+{xpToday} XP</div>
          <div className="km-streak-meta">🔥 {streak} ngày</div>
        </div>
      </div>

    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<KanjiMapApp />);
