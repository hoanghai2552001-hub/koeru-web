// kanji-stroke-order.jsx — animated stroke order via KanjiVG
// Fetches SVG from jsdelivr CDN mirror of KanjiVG repo (CORS-friendly).

const StrokeOrder = ({ kanji, size = 180 }) => {
  const [paths, setPaths] = useState(null);
  const [error, setError] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [strokeIdx, setStrokeIdx] = useState(0);   // how many strokes drawn so far
  const [lengths, setLengths] = useState([]);       // path length per stroke
  const svgRef = useRef(null);
  const rafRef = useRef(null);

  // codepoint → KanjiVG filename (5-digit lowercase hex)
  const codepoint = kanji.codePointAt(0).toString(16).padStart(5, '0');
  const url = `https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/${codepoint}.svg`;

  // fetch SVG → extract path d attributes (one per stroke, in order)
  useEffect(() => {
    let cancelled = false;
    setPaths(null); setError(null); setStrokeIdx(0); setPlaying(false);
    fetch(url)
      .then(r => {
        if (!r.ok) throw new Error('not found');
        return r.text();
      })
      .then(text => {
        if (cancelled) return;
        const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
        const ps = Array.from(doc.querySelectorAll('path'))
          .map(p => p.getAttribute('d'))
          .filter(Boolean);
        if (!ps.length) throw new Error('no paths');
        setPaths(ps);
      })
      .catch(e => { if (!cancelled) setError(e.message || 'load failed'); });
    return () => { cancelled = true; };
  }, [url]);

  // measure path lengths once rendered (using a hidden SVG)
  useEffect(() => {
    if (!paths || !svgRef.current) return;
    const els = svgRef.current.querySelectorAll('path[data-stroke]');
    const lens = Array.from(els).map(el => {
      try { return el.getTotalLength(); } catch { return 100; }
    });
    setLengths(lens);
    setStrokeIdx(paths.length); // start fully drawn
  }, [paths]);

  // animation loop: progressively reveal strokes
  const play = () => {
    if (!paths) return;
    setPlaying(true);
    setStrokeIdx(0);
    const STROKE_MS = 380; // per stroke
    const PAUSE_MS = 120;  // between strokes
    let i = 0;
    let start = performance.now();
    const step = (now) => {
      const t = (now - start) / STROKE_MS;
      if (t >= 1) {
        i += 1;
        if (i >= paths.length) {
          setStrokeIdx(paths.length);
          setPlaying(false);
          return;
        }
        start = now + PAUSE_MS;
        setStrokeIdx(i);
      } else {
        setStrokeIdx(i + Math.min(1, t));
      }
      rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
  };

  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  if (error) {
    // fallback: show static glyph with a hint
    return (
      <div className="km-stroke">
        <div className="km-stroke-header">
          <span className="km-label">Cách viết</span>
          <span style={{ fontSize:11, color:'var(--ink-faint)' }}>Không có dữ liệu</span>
        </div>
        <div className="km-stroke-fallback">
          <span style={{ fontFamily:'var(--font-kanji)', fontSize:84, fontWeight:900, color:'var(--ink-faint)' }}>{kanji}</span>
        </div>
      </div>
    );
  }

  if (!paths) {
    return (
      <div className="km-stroke">
        <div className="km-stroke-header">
          <span className="km-label">Cách viết</span>
        </div>
        <div className="km-stroke-fallback">
          <span style={{ fontSize:13, color:'var(--ink-faint)' }}>Đang tải…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="km-stroke">
      <div className="km-stroke-header">
        <span className="km-label">Cách viết · {paths.length} nét</span>
        <button className="km-btn is-ghost" style={{ padding:'2px 8px', fontSize:12 }}
          onClick={play} disabled={playing}>
          {playing ? '▶ đang vẽ…' : '▶ phát lại'}
        </button>
      </div>
      <div className="km-stroke-canvas">
        <svg ref={svgRef} viewBox="0 0 109 109" width={size} height={size}>
          {/* tic-tac-toe grid (KanjiVG canvas is 109×109) */}
          <line x1="54.5" y1="0" x2="54.5" y2="109" className="km-stroke-grid" />
          <line x1="0" y1="54.5" x2="109" y2="54.5" className="km-stroke-grid" />
          {paths.map((d, i) => {
            const len = lengths[i] || 100;
            const isDone = i + 1 <= Math.floor(strokeIdx);
            const isCurrent = !isDone && i === Math.floor(strokeIdx);
            const frac = isCurrent ? (strokeIdx - i) : (isDone ? 1 : 0);
            const offset = len * (1 - frac);
            return (
              <path key={i} data-stroke={i} d={d}
                className={`km-stroke-path ${isDone ? 'is-done' : isCurrent ? 'is-current' : 'is-pending'}`}
                style={{
                  strokeDasharray: len,
                  strokeDashoffset: offset,
                }} />
            );
          })}
          {/* stroke number labels at start of each stroke */}
          {paths.map((d, i) => {
            // parse first M coordinate from path
            const m = /M\s*([-\d.]+)[ ,]([-\d.]+)/.exec(d);
            if (!m) return null;
            const x = parseFloat(m[1]), y = parseFloat(m[2]);
            const isDone = i + 1 <= Math.floor(strokeIdx);
            return (
              <text key={'n'+i} x={x} y={y} className="km-stroke-num"
                opacity={isDone ? 1 : 0.3}>
                {i + 1}
              </text>
            );
          })}
        </svg>
      </div>
    </div>
  );
};

window.StrokeOrder = StrokeOrder;
