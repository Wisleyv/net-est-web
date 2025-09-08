/** @vitest-environment jsdom */
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StrategySuperscriptRenderer from '../StrategySuperscriptRenderer.jsx';

describe('StrategySuperscriptRenderer', () => {
  it('renders abbreviation markers using offsets with aria-label full name', () => {
    const strategies = [{ strategy_id: 's1', code: 'ADD+', target_offsets: [{ start: 2, end: 5 }], confidence: 0.9 }];
    render(<StrategySuperscriptRenderer targetText="ABCDEFG" strategies={strategies} />);
    const sup = screen.getByText('ADD+');
    expect(sup).toBeTruthy();
    expect(sup.getAttribute('aria-label')).toMatch(/ADD\+ -/);
  });
  it('falls back to sentence segmentation showing abbreviation', () => {
    const strategies = [{ strategy_id: 's1', code: 'MOD+', target_offsets: [] }];
    render(<StrategySuperscriptRenderer targetText="Uma frase. Outra frase." strategies={strategies} />);
    const sup = screen.getByText('MOD+');
    expect(sup).toBeTruthy();
  });
});
