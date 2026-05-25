// ══════════════════════════════════════════
// KOERU — Unified Mastery + SRS Engine
// Dùng chung cho tất cả 4 games.
// Thuật toán: SM-2 (simplified)
// ══════════════════════════════════════════

const MASTERY_STORE_KEY  = 'koeru_mastery_v2';
const MASTERY_MAX_LEVEL  = 5;    // 0 (mới) → 5 (thành thạo)
const SM2_EASE_DEFAULT   = 2.5;
const SM2_EASE_MIN       = 1.3;
const SM2_EASE_MAX       = 2.5;

/**
 * Mỗi entry trong store:
 * {
 *   m       : 0-5,        // mastery level (hiển thị UI)
 *   reps    : 0,          // số lần trả lời đúng liên tiếp
 *   interval: 1,          // khoảng cách ôn tập (ngày)
 *   ease    : 2.5,        // hệ số dễ/khó (SM-2 EF)
 *   due     : timestamp,  // thời điểm cần ôn tiếp
 *   seen    : timestamp,  // lần cuối nhìn thấy
 *   source  : 'flash'|'match'|'dungeon'|'speed'  // game cuối cập nhật
 * }
 */

class KoeruMastery {
  constructor() {
    this._data = {};
    this._load();
  }

  // ── Persistence ─────────────────────────
  _load() {
    try {
      const raw = localStorage.getItem(MASTERY_STORE_KEY);
      const parsed = JSON.parse(raw || '{}');
      this._data = (parsed && typeof parsed === 'object' && !Array.isArray(parsed))
        ? parsed : {};
    } catch(e) { this._data = {}; }

    // Migration: nhập từ bubble_mastery (format cũ)
    this._migrateLegacy();
  }

  _save() {
    try { localStorage.setItem(MASTERY_STORE_KEY, JSON.stringify(this._data)); } catch(e) {}
  }

  _migrateLegacy() {
    try {
      const old = localStorage.getItem('bubble_mastery');
      if (!old) return;
      const parsed = JSON.parse(old);
      if (!parsed || typeof parsed !== 'object') return;
      let migrated = 0;
      for (const [kanji, val] of Object.entries(parsed)) {
        if (this._data[kanji]) continue; // already in new store
        this._data[kanji] = this._newEntry();
        this._data[kanji].m    = Math.min(MASTERY_MAX_LEVEL, val.m || 0);
        this._data[kanji].reps = val.m || 0;
        this._data[kanji].seen = val.seen || Date.now();
        migrated++;
      }
      if (migrated > 0) this._save();
    } catch(e) {}
  }

  _newEntry() {
    return {
      m        : 0,
      reps     : 0,
      interval : 1,
      ease     : SM2_EASE_DEFAULT,
      due      : 0,        // 0 = chưa từng học = ưu tiên cao nhất
      seen     : 0,
      source   : '',
    };
  }

  _get(kanji) {
    if (!this._data[kanji]) this._data[kanji] = this._newEntry();
    return this._data[kanji];
  }

  // ── Public API ───────────────────────────

  /** Mastery level 0–5 của một kanji */
  getMasteryLevel(kanji) {
    return this._data[kanji]?.m ?? 0;
  }

  /** Kanji đã được "học thuộc" chưa (m >= 4) */
  isLearned(kanji) {
    return this.getMasteryLevel(kanji) >= 4;
  }

  /** Thời điểm ôn tiếp theo (Date object) */
  getNextReview(kanji) {
    const entry = this._data[kanji];
    if (!entry || !entry.due) return null;
    return new Date(entry.due);
  }

  /** Kanji này có đến hạn ôn chưa (hôm nay hoặc quá hạn) */
  isDue(kanji) {
    const entry = this._data[kanji];
    if (!entry) return false;           // chưa học lần nào
    if (!entry.due) return true;        // due=0 = chưa học
    return entry.due <= Date.now();
  }

  /**
   * Ghi nhận kết quả trả lời — cập nhật SM-2 và mastery level.
   * @param {string} kanji
   * @param {boolean} correct
   * @param {string} source  'flash'|'match'|'dungeon'|'speed'
   */
  record(kanji, correct, source = '') {
    const e = this._get(kanji);
    e.seen   = Date.now();
    e.source = source;

    if (correct) {
      // SM-2: tăng interval
      if (e.reps === 0)      e.interval = 1;
      else if (e.reps === 1) e.interval = 6;
      else                   e.interval = Math.round(e.interval * e.ease);
      e.ease = Math.min(SM2_EASE_MAX, e.ease + 0.1);
      e.reps++;
      // Mastery level: tăng 1 mỗi khi trả lời đúng
      e.m = Math.min(MASTERY_MAX_LEVEL, e.m + 1);
    } else {
      // SM-2: reset
      e.reps     = 0;
      e.interval = 1;
      e.ease     = Math.max(SM2_EASE_MIN, e.ease - 0.2);
      // Mastery level: giảm 1 khi sai (không về 0)
      e.m = Math.max(0, e.m - 1);
    }

    // Tính ngày ôn tiếp: now + interval ngày
    e.due = Date.now() + e.interval * 86_400_000;

    this._save();
  }

  /**
   * Lọc những kanji đến hạn ôn từ một deck.
   * Trả về mảng đã sort: quá hạn lâu nhất trước.
   */
  getDueCards(deck) {
    const now = Date.now();
    return deck
      .filter(k => {
        const e = this._data[k.kanji];
        if (!e) return false;
        return e.due > 0 && e.due <= now;
      })
      .sort((a, b) => {
        const da = this._data[a.kanji]?.due ?? 0;
        const db = this._data[b.kanji]?.due ?? 0;
        return da - db; // quá hạn lâu nhất trước
      });
  }

  /**
   * Số kanji đến hạn ôn hôm nay trong một deck (hoặc toàn bộ nếu không truyền).
   */
  countDue(deck) {
    if (deck) return this.getDueCards(deck).length;
    const now = Date.now();
    return Object.values(this._data).filter(e => e.due > 0 && e.due <= now).length;
  }

  /** Số kanji đã từng gặp (seen > 0) */
  countSeen() {
    return Object.keys(this._data).length;
  }

  /** Thống kê tổng hợp */
  getStats() {
    const entries = Object.values(this._data);
    const now     = Date.now();
    return {
      total    : entries.length,
      due      : entries.filter(e => e.due > 0 && e.due <= now).length,
      learned  : entries.filter(e => e.m >= 4).length,
      mastered : entries.filter(e => e.m >= MASTERY_MAX_LEVEL).length,
    };
  }

  /**
   * Sắp xếp deck ưu tiên:
   *  1. Đến hạn ôn (quá hạn lâu nhất đầu)
   *  2. Chưa học (due=0)
   *  3. Học rồi, chưa đến hạn (mastery thấp trước)
   */
  sortDeckByPriority(deck) {
    const now = Date.now();
    return [...deck].sort((a, b) => {
      const ea = this._data[a.kanji];
      const eb = this._data[b.kanji];
      const dueA = ea?.due ?? 0;
      const dueB = eb?.due ?? 0;

      // Cả 2 đến hạn: quá hạn lâu hơn trước
      if (dueA <= now && dueB <= now) return dueA - dueB;
      // Chỉ A đến hạn
      if (dueA <= now) return -1;
      // Chỉ B đến hạn
      if (dueB <= now) return 1;
      // Cả 2 chưa đến hạn: mastery thấp hơn trước
      return (ea?.m ?? 0) - (eb?.m ?? 0);
    });
  }
}

// ── Singleton ────────────────────────────
window.koeruMastery = new KoeruMastery();

// ── Backward compat cho kanji-bubble.js ──
// (bubble game dùng masteryData trực tiếp)
// Bridge: redirect getMastery/updateMastery sang unified store
function getMastery(kanji) {
  return window.koeruMastery.getMasteryLevel(kanji);
}
function updateMastery(kanji, correct) {
  window.koeruMastery.record(kanji, correct, 'dungeon');
  // Cập nhật masteryData local của bubble game để UI không bị lệch
  if (typeof masteryData !== 'undefined') {
    if (!masteryData[kanji]) masteryData[kanji] = {};
    masteryData[kanji].m    = window.koeruMastery.getMasteryLevel(kanji);
    masteryData[kanji].seen = Date.now();
  }
}
