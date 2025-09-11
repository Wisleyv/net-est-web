import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { vi, describe, it, expect, afterEach, beforeAll } from 'vitest';

// Use hoisted to define mock refs before the file is evaluated
const { mockUseAppStore, mockUseAnnotationStore } = vi.hoisted(() => ({
  mockUseAppStore: vi.fn(),
  mockUseAnnotationStore: vi.fn()
}));

vi.mock('../../../stores/useAppStore.js', () => ({ default: mockUseAppStore }));
vi.mock('../../../stores/useAnnotationStore.js', () => ({ default: mockUseAnnotationStore }));

// Import component after mocks (static import acceptable because mocks above are hoisted)
import FeedbackCollection from '../FeedbackCollection.jsx';

function setupStores({ enabled = true } = {}) {
  mockUseAppStore.mockImplementation((selector) => selector({ config: { enableFeedbackActions: enabled } }));
  mockUseAnnotationStore.mockReturnValue({ acceptAnnotation: vi.fn(), rejectAnnotation: vi.fn() });
}

describe('FeedbackCollection', () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });
  it('renders buttons when enabled', async () => {
    setupStores({ enabled: true });
    render(<FeedbackCollection strategy={{ strategy_id: 's1' }} />);
  const accept = screen.getByRole('button', { name: /Aceitar/i });
  const modify = screen.getByRole('button', { name: /Modificar/i });
  const reject = screen.getByRole('button', { name: /Rejeitar/i });
  expect(!!accept && !!modify && !!reject).toBe(true);
  });
  it('does not render buttons when disabled', async () => {
    setupStores({ enabled: false });
  render(<FeedbackCollection strategy={{ strategy_id: 's1' }} />);
  const wrapper = screen.getByTestId('feedback-collection');
  expect(wrapper.getAttribute('data-enabled')).toBe('false');
  const accepts = screen.queryAllByRole('button', { name: /Aceitar/i });
  expect(accepts.length).toBe(0);
  });
});
