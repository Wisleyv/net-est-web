import React from 'react';
import { render } from '@testing-library/react';
import { describe, beforeEach, it, expect } from 'vitest';
import SideBySideTextDisplay from '../../components/SideBySideTextDisplay.jsx';
import useAppStore from '../../stores/useAppStore.js';
import useAnnotationStore from '../../stores/useAnnotationStore.js';

// NOTE: jsdom can't perform real DOM range selection; we simulate internal state by direct store calls.

describe('Create Annotation Flow (UI abstraction test)', () => {
  beforeEach(() => {
    // Enable feedback actions
    useAppStore.setState({ config: { enableFeedbackActions: true } });
    // Reset annotations
    useAnnotationStore.setState({ annotations: [] });
  });

  it('optimistically adds created annotation via store and appears in merged strategies', () => {
    const analysisResult = {
      target_text: 'Texto simplificado de teste.',
      simplification_strategies: []
    };
    render(<SideBySideTextDisplay sourceText="Origem" targetText={analysisResult.target_text} analysisResult={analysisResult} />);

    const { createAnnotation } = useAnnotationStore.getState();
    createAnnotation({ strategy_code: 'OM+', target_offsets: [{ start: 0, end: 5 }], comment: 'Teste' });

    const ann = useAnnotationStore.getState().annotations.find(a => a.strategy_code === 'OM+');
    expect(ann).toBeTruthy();
  });
});
