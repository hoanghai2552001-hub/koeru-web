// kanji-map-graph.jsx — 2D force-directed graph using d3-force.
// Renders SVG with pan/zoom + animated "fly-to" on selection.

const { useEffect, useRef, useState, useMemo, useCallback } = React;

// --- helper: build node/edge sets for a given selected kanji ---
// Strategy: when no selection → show all filtered kanji (sparse layout).
// When a kanji is selected → show selected + its direct compounds + bridge kanji
// (kanji that share a compound with selected). Cap at maxNodes.
function buildSubgraph({ data, jlptFilter, selectedId, expanded }) {
  // collect kanji that pass filter
  const allKanji = data.kanji.filter(k => jlptFilter.includes(k.jlpt));
  const allVocab = data.vocab.filter(v => jlptFilter.includes(v.jlpt));
  const kanjiById = Object.fromEntries(allKanji.map(k => [k.id, k]));
  const vocabById = Object.fromEntries(allVocab.map(v => [v.id, v]));

  const nodes = [];
  const links = [];
  const seenNodes = new Set();
  const addNode = (n) => { if (!seenNodes.has(n.id)) { seenNodes.add(n.id); nodes.push(n); } };
  const addLink = (s, t) => links.push({ source: s, target: t });

  if (!selectedId) {
    // overview: show all kanji + kanji-to-kanji relations
    allKanji.forEach(k => addNode({ ...k, type: 'kanji' }));
    (data.kanji_relations || []).forEach(r => {
      if (kanjiById[r.source] && kanjiById[r.target]) addLink(r.source, r.target);
    });
    // also show a few featured vocab (compounds that connect 2+ visible kanji)
    allVocab.slice(0, 0).forEach(() => {});
    return { nodes, links };
  }

  // selected mode
  const sel = kanjiById[selectedId] || vocabById[selectedId];
  if (!sel) return { nodes, links };

  if (sel.kanji) {
    // it's a vocab — anchor; show the vocab + its component kanji + sibling vocab
    addNode({ ...sel, type: 'vocab' });
    sel.kanji.forEach(kid => {
      if (kanjiById[kid]) {
        addNode({ ...kanjiById[kid], type: 'kanji' });
        addLink(sel.id, kid);
      }
    });
    // siblings: other vocab sharing any of the same kanji
    const siblingVocab = allVocab.filter(v => v.id !== sel.id && v.kanji.some(k => sel.kanji.includes(k)));
    const cap = expanded ? siblingVocab.length : Math.min(siblingVocab.length, 8);
    siblingVocab.slice(0, cap).forEach(v => {
      addNode({ ...v, type: 'vocab' });
      v.kanji.forEach(kid => {
        if (kanjiById[kid] && seenNodes.has(kid)) addLink(v.id, kid);
      });
    });
    return { nodes, links, total: siblingVocab.length, shown: cap };
  }

  // it's a kanji — anchor; show selected + compounds + bridge kanji
  addNode({ ...sel, type: 'kanji', role: 'center' });
  const compounds = allVocab.filter(v => v.kanji.includes(sel.id));
  const cap = expanded ? compounds.length : Math.min(compounds.length, 8);
  compounds.slice(0, cap).forEach(v => {
    addNode({ ...v, type: 'vocab', role: 'compound' });
    addLink(sel.id, v.id);
    // pull in bridge kanji (other kanji in this compound) — but cap separately
    v.kanji.forEach(kid => {
      if (kid !== sel.id && kanjiById[kid]) {
        addNode({ ...kanjiById[kid], type: 'kanji', role: 'bridge' });
        addLink(v.id, kid);
      }
    });
  });
  // kanji_relations involving selected
  (data.kanji_relations || []).forEach(r => {
    if (r.source === sel.id && kanjiById[r.target]) {
      addNode({ ...kanjiById[r.target], type: 'kanji', role: 'bridge' });
      addLink(r.source, r.target);
    } else if (r.target === sel.id && kanjiById[r.source]) {
      addNode({ ...kanjiById[r.source], type: 'kanji', role: 'bridge' });
      addLink(r.source, r.target);
    }
  });

  // ONYOMI cousins — kanji sharing at least one onyomi, max 3
  if (sel.onyomi?.length) {
    const myOn = new Set(sel.onyomi);
    const cousins = allKanji
      .filter(k => k.id !== sel.id && k.onyomi?.some(o => myOn.has(o)))
      .slice(0, 3);
    cousins.forEach(c => {
      // upgrade role to 'cousin' if not center
      const existing = nodes.find(n => n.id === c.id);
      if (existing) { existing.role = 'cousin'; }
      else { addNode({ ...c, type: 'kanji', role: 'cousin' }); }
      const shared = c.onyomi.filter(o => myOn.has(o))[0];
      links.push({ source: sel.id, target: c.id, kind: 'onyomi', label: shared });
    });
  }

  return { nodes, links, total: compounds.length, shown: cap };
}

// ---------------- Component ----------------
const KanjiGraph = ({
  data, jlptFilter, selectedId, onSelect,
  expanded, onExpandMore,
  width, height,
}) => {
  const svgRef = useRef(null);
  const simRef = useRef(null);
  const prevPosRef = useRef({});   // last-known positions, keyed by node id (for smooth transitions)
  const dragMovedRef = useRef({}); // per-id: did the user drag this node (> threshold) since pointerdown
  const [positions, setPositions] = useState({});       // id → {x,y}
  const [hoverId, setHoverId] = useState(null);
  const [dragId, setDragId] = useState(null);
  const dragOffsetRef = useRef({ x: 0, y: 0 });
  const dragStartPosRef = useRef({ x: 0, y: 0 });
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const targetTransformRef = useRef({ x: 0, y: 0, k: 1 });
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ mx: 0, my: 0, tx: 0, ty: 0 });
  // multi-touch pinch tracking
  const pointersRef = useRef(new Map()); // pointerId → {x, y}
  const pinchStartRef = useRef(null);    // { dist, k, midX, midY, tx, ty }

  // build subgraph based on current selection
  const { nodes, links, total, shown } = useMemo(
    () => buildSubgraph({ data, jlptFilter, selectedId, expanded }),
    [data, jlptFilter, selectedId, expanded]
  );

  // run d3-force simulation whenever the subgraph changes
  useEffect(() => {
    if (!nodes.length) { setPositions({}); return; }
    // pre-seed positions: inherit from previous frame if id existed, else ring slot
    const R = 120;
    const prev = prevPosRef.current;
    const nCopy = nodes.map((n, i) => {
      const seeded = prev[n.id];
      if (seeded) return { ...n, x: seeded.x, y: seeded.y };
      const a = (i / nodes.length) * Math.PI * 2;
      return { ...n, x: Math.cos(a) * R, y: Math.sin(a) * R };
    });
    const lCopy = links.map(l => ({ ...l }));

    // pin selected to center
    const selNode = nCopy.find(n => n.id === selectedId);
    if (selNode) { selNode.fx = 0; selNode.fy = 0; }

    const sim = d3.forceSimulation(nCopy)
      .force('link', d3.forceLink(lCopy).id(d => d.id).distance(d => {
        return (d.source.type === 'vocab' || d.target.type === 'vocab') ? 80 : 110;
      }).strength(0.6))
      .force('charge', d3.forceManyBody().strength(-180).distanceMax(380))
      .force('x', d3.forceX(0).strength(0.08))
      .force('y', d3.forceY(0).strength(0.08))
      .force('collide', d3.forceCollide(d => {
        if (d.role === 'center') return 48;
        if (d.type === 'vocab')  return 42;
        if (d.role === 'bridge') return 28;
        return 34;
      }))
      .stop();

    // run synchronously to convergence
    const ITER = 280;
    for (let i = 0; i < ITER; i++) sim.tick();

    const pos = {};
    nCopy.forEach(n => { pos[n.id] = { x: n.x, y: n.y }; });
    prevPosRef.current = pos;     // remember for next subgraph
    setPositions(pos);

    return () => sim.stop();
  }, [nodes.length, links.length, selectedId, expanded]);

  // fly-to when selection changes: animate transform so selected is centered & zoomed
  useEffect(() => {
    if (!selectedId) {
      targetTransformRef.current = { x: 0, y: 0, k: 1 };
    } else {
      // selected is pinned to (0,0), so we just need centering with mild zoom
      targetTransformRef.current = { x: 0, y: 0, k: 1.15 };
    }
    // simple rAF tween
    let raf;
    const ease = (a, b, t) => a + (b - a) * t;
    const step = () => {
      setTransform(prev => {
        const t = targetTransformRef.current;
        const nx = ease(prev.x, t.x, 0.12);
        const ny = ease(prev.y, t.y, 0.12);
        const nk = ease(prev.k, t.k, 0.12);
        if (Math.abs(nx - t.x) < 0.5 && Math.abs(ny - t.y) < 0.5 && Math.abs(nk - t.k) < 0.005) {
          return t;
        }
        raf = requestAnimationFrame(step);
        return { x: nx, y: ny, k: nk };
      });
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [selectedId]);

  // PAN: pointer down on empty space → start panning
  const onPointerDown = useCallback((e) => {
    pointersRef.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    // 2nd pointer arrived → switch to pinch mode (cancel any pan/node-drag)
    if (pointersRef.current.size === 2) {
      const pts = [...pointersRef.current.values()];
      const dx = pts[1].x - pts[0].x, dy = pts[1].y - pts[0].y;
      pinchStartRef.current = {
        dist: Math.hypot(dx, dy),
        k: transform.k,
        midX: (pts[0].x + pts[1].x) / 2,
        midY: (pts[0].y + pts[1].y) / 2,
        tx: transform.x, ty: transform.y,
      };
      isPanningRef.current = false;
      if (dragId) setDragId(null);
      return;
    }
    if (e.target.closest('.km-node')) return;
    isPanningRef.current = true;
    panStartRef.current = { mx: e.clientX, my: e.clientY, tx: transform.x, ty: transform.y };
  }, [transform, dragId]);

  // helper: client coords → graph-local coords
  const clientToGraph = useCallback((cx, cy) => {
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    return {
      x: (cx - rect.left - rect.width / 2 - transform.x) / transform.k,
      y: (cy - rect.top - rect.height / 2 - transform.y) / transform.k,
    };
  }, [transform]);

  // start dragging a node
  const onNodeDown = useCallback((e, id) => {
    e.stopPropagation();
    pointersRef.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    // if multi-touch, let the pinch path take over
    if (pointersRef.current.size >= 2) return;
    const p = positions[id];
    if (!p) return;
    const g = clientToGraph(e.clientX, e.clientY);
    dragOffsetRef.current = { x: g.x - p.x, y: g.y - p.y };
    dragStartPosRef.current = { x: e.clientX, y: e.clientY };
    dragMovedRef.current[id] = false;
    setDragId(id);
    e.currentTarget.setPointerCapture?.(e.pointerId);
  }, [positions, clientToGraph]);

  useEffect(() => {
    const onMove = (e) => {
      // update pointer record
      if (pointersRef.current.has(e.pointerId)) {
        pointersRef.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
      }
      // PINCH: 2+ active pointers
      if (pinchStartRef.current && pointersRef.current.size >= 2) {
        const pts = [...pointersRef.current.values()];
        const dx = pts[1].x - pts[0].x, dy = pts[1].y - pts[0].y;
        const newDist = Math.hypot(dx, dy);
        const start = pinchStartRef.current;
        const newK = Math.max(0.4, Math.min(2.5, start.k * (newDist / start.dist)));
        const newMid = { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2 };
        // pan so the pinch midpoint stays put under fingers
        const newTx = start.tx + (newMid.x - start.midX);
        const newTy = start.ty + (newMid.y - start.midY);
        setTransform({ x: newTx, y: newTy, k: newK });
        targetTransformRef.current = { x: newTx, y: newTy, k: newK };
        return;
      }
      // NODE DRAG
      if (dragId) {
        const dx0 = e.clientX - dragStartPosRef.current.x;
        const dy0 = e.clientY - dragStartPosRef.current.y;
        if (Math.hypot(dx0, dy0) > 4) dragMovedRef.current[dragId] = true;
        const g = clientToGraph(e.clientX, e.clientY);
        const nx = g.x - dragOffsetRef.current.x;
        const ny = g.y - dragOffsetRef.current.y;
        setPositions(p => ({ ...p, [dragId]: { x: nx, y: ny } }));
        prevPosRef.current[dragId] = { x: nx, y: ny };
        return;
      }
      // PAN
      if (!isPanningRef.current) return;
      const dx = e.clientX - panStartRef.current.mx;
      const dy = e.clientY - panStartRef.current.my;
      setTransform(t => ({ ...t, x: panStartRef.current.tx + dx, y: panStartRef.current.ty + dy }));
      targetTransformRef.current = { ...targetTransformRef.current,
        x: panStartRef.current.tx + dx, y: panStartRef.current.ty + dy };
    };
    const onUp = (e) => {
      pointersRef.current.delete(e.pointerId);
      if (pointersRef.current.size < 2) pinchStartRef.current = null;
      if (pointersRef.current.size === 0) {
        isPanningRef.current = false;
        if (dragId) {
          const id = dragId;
          setDragId(null);
          setTimeout(() => { dragMovedRef.current[id] = false; }, 50);
        }
      }
    };
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointercancel', onUp);
    return () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
    };
  }, [dragId, clientToGraph]);

  // wheel zoom
  const onWheel = useCallback((e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setTransform(t => {
      const newK = Math.max(0.4, Math.min(2.5, t.k * factor));
      return { ...t, k: newK };
    });
    targetTransformRef.current = { ...targetTransformRef.current,
      k: Math.max(0.4, Math.min(2.5, targetTransformRef.current.k * factor)) };
  }, []);

  // attach wheel handler — passive:false so preventDefault works
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, [onWheel]);

  const setZoom = (mul) => {
    targetTransformRef.current = { ...targetTransformRef.current,
      k: Math.max(0.4, Math.min(2.5, targetTransformRef.current.k * mul)) };
    setTransform(t => ({ ...t, k: Math.max(0.4, Math.min(2.5, t.k * mul)) }));
  };
  const resetZoom = () => {
    targetTransformRef.current = { x: 0, y: 0, k: 1 };
    setTransform({ x: 0, y: 0, k: 1 });
  };

  // viewport center
  const cx = width / 2 + transform.x;
  const cy = height / 2 + transform.y;
  const k = transform.k;

  // does the selected node have hidden compounds?
  const hasMore = !expanded && total && total > shown;

  // === render ===
  return (
    <div className="km-graph-wrap" style={{ position:'relative' }}>
      <svg
        ref={svgRef}
        width={width} height={height}
        onPointerDown={onPointerDown}
        style={{ cursor: isPanningRef.current ? 'grabbing' : 'grab', touchAction: 'none' }}
      >
        <g transform={`translate(${cx} ${cy}) scale(${k})`}>
          {/* edges */}
          {links.map((l, i) => {
            const sId = typeof l.source === 'object' ? l.source.id : l.source;
            const tId = typeof l.target === 'object' ? l.target.id : l.target;
            const s = positions[sId];
            const t = positions[tId];
            if (!s || !t) return null;
            const isHi = selectedId && (sId === selectedId || tId === selectedId);
            const isOnyomi = l.kind === 'onyomi';
            const mx = (s.x + t.x) / 2;
            const my = (s.y + t.y) / 2;
            return (
              <g key={i}>
                <line
                  x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                  className={'km-edge ' + (isHi ? 'is-highlighted' : '')}
                  strokeDasharray={isOnyomi ? '4 4' : undefined}
                  stroke={isOnyomi ? 'var(--hanko)' : undefined}
                  strokeOpacity={isOnyomi ? .65 : undefined}
                />
                {l.label ? (
                  <text x={mx} y={my} className="km-edge-label">{l.label}</text>
                ) : null}
              </g>
            );
          })}
          {/* nodes */}
          {nodes.map(n => {
            const p = positions[n.id];
            if (!p) return null;
            const isSelected = n.id === selectedId;
            const isHover = n.id === hoverId;
            const isKanji = n.type === 'kanji';
            const role = n.role || 'default';

            let size;
            if (isKanji) {
              if (role === 'center')  size = 40;
              else if (role === 'cousin') size = 26;
              else if (role === 'bridge') size = 22;
              else size = 28;
            } else {
              size = 28;
            }

            const opacity =
              role === 'bridge' ? 0.55 :
              role === 'cousin' ? 0.92 :
              1;

            return (
              <g key={n.id}
                className={`km-node ${isKanji ? 'is-kanji' : 'is-vocab'} role-${role} ${dragId === n.id ? 'is-dragging' : ''}`}
                transform={`translate(${p.x} ${p.y})`}
                opacity={opacity}
                style={{ transition: dragId ? 'none' : 'transform .55s cubic-bezier(.2,.7,.3,1), opacity .25s' }}
                onPointerDown={(e) => onNodeDown(e, n.id)}
                onMouseEnter={() => setHoverId(n.id)}
                onMouseLeave={() => setHoverId(h => h === n.id ? null : h)}
                onClick={(e) => {
                  e.stopPropagation();
                  // suppress if we just dragged this node noticeably
                  if (dragMovedRef.current[n.id]) return;
                  onSelect(n.id);
                }}
              >
                {isKanji ? (
                  <circle r={size} className={`km-node-circle lvl-${n.jlpt} ${isSelected ? 'is-selected' : ''}`} />
                ) : (
                  <rect
                    x={-(Math.max(n.id.length, 2) * 9 + 12)}
                    y={-18}
                    width={(Math.max(n.id.length, 2) * 9 + 12) * 2}
                    height={36}
                    rx={18}
                    className={`km-node-circle lvl-${n.jlpt} ${isSelected ? 'is-selected' : ''}`}
                  />
                )}
                <text className="km-node-glyph"
                  style={{ fontSize: isKanji ? size * 0.9 : 15 }}>
                  {n.id}
                </text>
                {isKanji && n.han_viet && (
                  <text className="km-node-label" y={size + 14}
                    style={{ fontSize: role === 'bridge' ? 9 : 10,
                             opacity: role === 'bridge' ? 0.75 : 1 }}>
                    {n.han_viet}
                  </text>
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {/* hover tooltip */}
      {(() => {
        if (!hoverId || hoverId === selectedId || dragId) return null;
        const n = nodes.find(x => x.id === hoverId);
        const p = positions[hoverId];
        if (!n || !p) return null;
        const screenX = width / 2 + transform.x + p.x * transform.k;
        const screenY = height / 2 + transform.y + p.y * transform.k;
        const isVocab = n.type === 'vocab';
        return (
          <div className="km-tooltip"
            style={{ left: screenX, top: screenY - 60 }}>
            <div className="km-tooltip-glyph"
              style={{ fontFamily: isVocab ? 'var(--font-jp)' : 'var(--font-kanji)' }}>
              {n.id}
            </div>
            <div className="km-tooltip-meta">
              <div className="km-tooltip-primary">
                {isVocab ? n.reading : n.han_viet}
              </div>
              <div className="km-tooltip-meaning">{n.meaning}</div>
              <div className="km-tooltip-tag">{n.jlpt}{isVocab ? '' : ` · ${n.stroke} nét`}</div>
            </div>
          </div>
        );
      })()}

      {/* status badge */}
      <div className="km-graph-status">
        <span>Đang xem <b>{nodes.length}</b> nodes</span>
        <span style={{ color:'var(--ink-faint)' }}>·</span>
        <span><b>{links.length}</b> liên kết</span>
        {selectedId && (
          <>
            <span style={{ color:'var(--ink-faint)' }}>·</span>
            <span>Tâm: <b>{selectedId}</b></span>
          </>
        )}
      </div>

      {/* zoom toolbar */}
      <div className="km-graph-toolbar">
        <button className="km-btn is-icon" onClick={() => setZoom(1.2)} title="Phóng to">＋</button>
        <button className="km-btn is-icon" onClick={() => setZoom(0.83)} title="Thu nhỏ">−</button>
        <button className="km-btn is-icon" onClick={resetZoom} title="Reset">⤢</button>
      </div>

      {/* expand more button */}
      {hasMore && (
        <button className="km-expand-more" onClick={onExpandMore}>
          Xem thêm {total - shown} liên kết
          <span style={{ fontSize: 14 }}>↓</span>
        </button>
      )}

      {/* empty state */}
      {!nodes.length && !selectedId && (
        <div className="km-empty">
          <div className="km-empty-glyph">無</div>
          <div className="km-empty-title">Không có chữ nào</div>
          <div className="km-empty-sub">Bật ít nhất 1 cấp JLPT để bắt đầu.</div>
        </div>
      )}
      {!nodes.length && selectedId && (
        <div className="km-empty">
          <div className="km-empty-glyph">?</div>
          <div className="km-empty-title">Không tìm thấy "{selectedId}"</div>
        </div>
      )}
    </div>
  );
};

window.KanjiGraph = KanjiGraph;
