import { describe, it, expect } from 'vitest';
import { buildUnifiedStrategyMap, segmentTextForHighlights, defaultSentenceSplit } from '../../../services/unifiedStrategyMapping.js';

describe('buildUnifiedStrategyMap', () => {
  it('creates stable deterministic map', () => {
    const input = [
      { code: 'MOD+', confidence: 0.8 },
      { code: 'ADD+', confidence: 0.9 },
      { code: 'ADD+', confidence: 0.5 } // duplicate ignored
    ];
    const map1 = buildUnifiedStrategyMap(input, { colorblindMode: false });
    const map2 = buildUnifiedStrategyMap(input, { colorblindMode: false });
    expect(Object.keys(map1)).toEqual(['ADD+','MOD+']);
    expect(JSON.stringify(map1)).toBe(JSON.stringify(map2));
  });
});

describe('segmentTextForHighlights', () => {
  const sampleText = 'Primeira frase. Segunda frase. Terceira frase.';
  const strategies = [
    { code: 'ADD+', confidence: 0.7, targetPosition: { type: 'sentence', sentence: 0 } },
    { code: 'MOD+', confidence: 0.9, targetPosition: { type: 'sentence', sentence: 1 } },
    { code: 'MOD+', confidence: 0.4, targetPosition: { type: 'sentence', sentence: 1 } },
    { code: 'SUB+', confidence: 0.8, targetPosition: { type: 'sentence', sentence: 2 } }
  ];
  it('creates one segment per covered sentence selecting highest confidence', () => {
    const segs = segmentTextForHighlights(sampleText, strategies, { scope: 'target' });
    expect(segs.length).toBe(3);
    expect(segs[1].code).toBe('MOD+'); // highest confidence chosen
  });
  it('skips uncovered sentences', () => {
    const segs = segmentTextForHighlights(sampleText, strategies.slice(0,2), { scope: 'target' });
    expect(segs.length).toBe(2);
  });
  it('uses default sentence splitter', () => {
    const parts = defaultSentenceSplit(sampleText);
    expect(parts.length).toBe(3);
  });
});
