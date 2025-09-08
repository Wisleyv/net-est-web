import { describe, it, expect } from 'vitest';
import { normalizeStrategies, buildInsertionPoints, superscriptNumber } from '../../../utils/strategyOffsets.js';

describe('strategyOffsets utilities', () => {
  it('normalizes offsets list', () => {
    const raw = [{ strategy_id: 'a', target_offsets: [{ start: 2, end: 5 }] }];
    const norm = normalizeStrategies(raw);
    expect(norm[0].target_offsets[0]).toEqual({ start: 2, end: 5 });
  });
  it('builds insertion points sorted & deduped', () => {
    const norm = normalizeStrategies([
      { strategy_id: 'a', target_offsets: [{ start: 5, end: 9 }, { start: 5, end: 9 }] },
      { strategy_id: 'b', target_offsets: [[3, 4]] }
    ]);
    const pts = buildInsertionPoints(norm, 100);
    expect(pts.map(p => p.id)).toEqual(['b','a']);
  });
  it('superscriptNumber renders unicode digits', () => {
    expect(superscriptNumber(12)).toBe('¹²');
  });
});
