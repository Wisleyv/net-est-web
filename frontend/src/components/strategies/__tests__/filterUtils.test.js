import { describe, it, expect } from 'vitest';

function filterStrategies(strats, activeCodes, minConf) {
  return strats.filter(s => activeCodes.includes(s.code) && ((s.confidence ?? s.confidence_score ?? 0) * 100) >= minConf);
}

describe('filterStrategies', () => {
  const sample = [
    { code: 'ADD+', confidence: 0.9 },
    { code: 'GEN+', confidence: 0.6 },
    { code: 'ADD+', confidence: 0.4 }
  ];
  it('keeps only active codes', () => {
    const res = filterStrategies(sample, ['ADD+'], 0);
    expect(res.length).toBe(2);
  });
  it('applies confidence threshold', () => {
    const res = filterStrategies(sample, ['ADD+','GEN+'], 70);
    expect(res.length).toBe(1);
    expect(res[0].confidence).toBe(0.9);
  });
});
