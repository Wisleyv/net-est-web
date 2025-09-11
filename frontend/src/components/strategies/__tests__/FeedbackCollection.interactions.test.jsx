import React from 'react';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { vi, describe, it, afterEach, expect } from 'vitest';

// Use hoisted mocks to avoid ESM race/hoisting issues
const { mockUseAppStore, mockUseAnnotationStore } = vi.hoisted(() => ({
  mockUseAppStore: vi.fn(),
  mockUseAnnotationStore: vi.fn(),
}));

vi.mock('../../../stores/useAppStore.js', () => ({ default: mockUseAppStore }));
vi.mock('../../../stores/useAnnotationStore.js', () => ({ default: mockUseAnnotationStore }));

import FeedbackCollection from '../FeedbackCollection.jsx';

function setup({ enabled = true } = {}) {
  const acceptAnnotation = vi.fn();
  const rejectAnnotation = vi.fn();
  mockUseAppStore.mockImplementation(sel => sel({ config: { enableFeedbackActions: enabled } }));
  mockUseAnnotationStore.mockReturnValue({ acceptAnnotation, rejectAnnotation });
  render(<FeedbackCollection strategy={{ strategy_id: 's42', code: 'ADD+' }} />);
  return { acceptAnnotation, rejectAnnotation };
}

afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe('FeedbackCollection interactions', () => {
  it('calls acceptAnnotation with strategy id', () => {
    const { acceptAnnotation } = setup({ enabled: true });
    const btn = screen.getByRole('button', { name: /Aceitar/i });
    fireEvent.click(btn);
    expect(acceptAnnotation).toHaveBeenCalledTimes(1);
    expect(acceptAnnotation).toHaveBeenCalledWith('s42');
  });
  it('calls rejectAnnotation with strategy id', () => {
    const { rejectAnnotation } = setup({ enabled: true });
    const btn = screen.getByRole('button', { name: /Rejeitar/i });
    fireEvent.click(btn);
    expect(rejectAnnotation).toHaveBeenCalledTimes(1);
    expect(rejectAnnotation).toHaveBeenCalledWith('s42');
  });
  it('does nothing when feature flag disabled', () => {
    const { acceptAnnotation, rejectAnnotation } = setup({ enabled: false });
    expect(screen.queryByRole('button', { name: /Aceitar/i })).toBeNull();
    expect(screen.queryByRole('button', { name: /Rejeitar/i })).toBeNull();
    expect(acceptAnnotation).not.toHaveBeenCalled();
    expect(rejectAnnotation).not.toHaveBeenCalled();
  });
});
