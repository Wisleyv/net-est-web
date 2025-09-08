import { describe, it, expect } from 'vitest';
import { buildUnifiedStrategyMap, generateUnifiedCSS } from '../../../services/unifiedStrategyMapping.js';

describe('pattern injection (colorblind mode)', () => {
  it('assigns patterns only when colorblindMode + enablePatterns true', () => {
    const strategies = [
      { code: 'SL+', confidence: 0.9 },
      { code: 'ADD+', confidence: 0.8 },
      { code: 'MOD+', confidence: 0.7 }
    ];
    const mapNo = buildUnifiedStrategyMap(strategies, { colorblindMode: false, enablePatterns: false });
    const mapYes = buildUnifiedStrategyMap(strategies, { colorblindMode: true, enablePatterns: true });
    expect(Object.values(mapNo).every(e => e.pattern === null)).toBe(true);
    expect(Object.values(mapYes).some(e => e.pattern)).toBe(true);
    const css = generateUnifiedCSS(mapYes);
    expect(css).toMatch(/repeating|radial|linear/);
  });
});
