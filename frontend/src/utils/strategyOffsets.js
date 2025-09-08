// Phase 2a: Utilities for superscript marker generation (additive)
// Normalizes strategies returned by backend (Phase 1 fields) and prepares insertion map.

export function normalizeStrategies(rawStrategies = []) {
  return rawStrategies.map((s, idx) => {
    const id = s.strategy_id || s.id || `strat_${idx}`;
    // Accept multiple offset formats: list, tuple, or single dict with char_start/char_end
    let targetOffsets = [];
    const raw = s.target_offsets;
    if (Array.isArray(raw)) {
      targetOffsets = raw
        .map(o => {
          if (!o) return null;
            if (typeof o.start === 'number' && typeof o.end === 'number') {
              return { start: o.start, end: o.end };
            }
            if (Array.isArray(o) && o.length === 2) {
              return { start: o[0], end: o[1] };
            }
            if (typeof o.char_start === 'number' && typeof o.char_end === 'number') {
              return { start: o.char_start, end: o.char_end };
            }
          return null;
        })
        .filter(Boolean)
        .filter(r => r.end > r.start);
    } else if (raw && typeof raw === 'object' && typeof raw.char_start === 'number' && typeof raw.char_end === 'number') {
      if (raw.char_end > raw.char_start) {
        targetOffsets = [{ start: raw.char_start, end: raw.char_end }];
      }
    }
    return {
      ...s,
      strategy_id: id,
      target_offsets: targetOffsets,
    };
  });
}

// Build insertion map: positions in target text -> array of strategy ids to mark.
export function buildInsertionPoints(strategies, textLength) {
  const points = [];
  strategies.forEach(s => {
    if (!Array.isArray(s.target_offsets) || s.target_offsets.length === 0) return;
    s.target_offsets.forEach(range => {
      const start = Math.max(0, Math.min(textLength, range.start));
      // We index by start boundary only for marker placement.
      points.push({ pos: start, id: s.strategy_id });
    });
  });
  // Deduplicate by (pos,id) and sort
  const dedupKey = new Set();
  const deduped = [];
  points.forEach(p => {
    const key = `${p.pos}:${p.id}`;
    if (!dedupKey.has(key)) { dedupKey.add(key); deduped.push(p); }
  });
  deduped.sort((a,b) => a.pos - b.pos);
  return deduped;
}

// Fallback: split target text into sentences; place markers at sentence ends for each strategy in order.
export function buildSentenceFallback(strategies, targetText) {
  const sentences = splitIntoSentences(targetText);
  // Map strategy_id -> first sentence index heuristic
  const mapping = [];
  sentences.length && strategies.forEach((s, idx) => {
    const sentenceIdx = idx % sentences.length;
    mapping.push({ sentenceIdx, id: s.strategy_id });
  });
  return { sentences, mapping };
}

export function splitIntoSentences(text) {
  if (!text) return [];
  return text.split(/([.!?]+)/).filter(Boolean).reduce((acc, part, i, arr) => {
    if (i % 2 === 0) {
      const punct = arr[i+1] || '';
      acc.push(part + punct);
    }
    return acc;
  }, []);
}

// Generate Unicode superscript digits (1..n) -> ¹²³ etc.
const SUPER_DIGITS = ['⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹'];
export function superscriptNumber(n) {
  const s = String(n);
  return s.split('').map(ch => SUPER_DIGITS[parseInt(ch,10)] || ch).join('');
}

export function assignDisplayIndices(insertionPoints) {
  // Assign sequential numbers in order of first appearance of each strategy id.
  const order = [];
  const seen = new Set();
  insertionPoints.forEach(p => {
    if (!seen.has(p.id)) { seen.add(p.id); order.push(p.id); }
  });
  const indexMap = new Map(order.map((id, i) => [id, i+1]));
  return { indexMap, order };
}
