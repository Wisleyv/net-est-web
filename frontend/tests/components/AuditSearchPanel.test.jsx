import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import AuditSearchPanel from '../../src/components/dashboard/AuditSearchPanel.jsx';
import useAppStore from '../../src/stores/useAppStore.js';
import useAnnotationStore from '../../src/stores/useAnnotationStore.js';

vi.mock('../../src/stores/useAnnotationStore.js', () => {
  const mockState = {
    sessionId: 'test',
    searchFilters: { statuses: [], codes: [], actions: [] },
    setSearchFilters: vi.fn(),
    resetSearch: vi.fn(),
    runSearch: vi.fn(),
    searchResults: [],
    searchLoading: false,
    audit: {},
    fetchAudit: vi.fn(),
  };
  const useStore = (sel) => (typeof sel === 'function' ? sel(mockState) : mockState);
  useStore.getState = () => mockState;
  return { default: useStore };
});

describe('AuditSearchPanel', () => {
  beforeEach(() => {
    // enable flag
    useAppStore.setState((s) => ({ config: { ...s.config, enableAuditSearch: true } }));
  });

  it('renders filters and buttons', () => {
    render(<AuditSearchPanel />);
    expect(screen.getByLabelText(/Filter by status/i)).toBeTruthy();
    expect(screen.getByLabelText(/Filter by strategy code/i)).toBeTruthy();
    expect(screen.getByLabelText(/Filter audit actions/i)).toBeTruthy();
    expect(screen.getByRole('button', { name: /Search/i })).toBeTruthy();
    expect(screen.getByRole('button', { name: /Reset/i })).toBeTruthy();
  });

  it('shows no results message initially', () => {
    render(<AuditSearchPanel />);
    const els = screen.getAllByText(/No results/i);
    expect(els.length).toBeGreaterThan(0);
  });
});
