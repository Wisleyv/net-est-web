import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from '@testing-library/react';
import create from 'zustand';

vi.mock('../../src/services/api.js', async () => {
  const actual = await vi.importActual('../../src/services/api.js');
  return {
    ...actual,
    annotationsAPI: {
      search: vi.fn().mockResolvedValue({ data: { annotations: [{ id:'1', strategy_code:'SL+', status:'accepted' }] } }),
      audit: vi.fn().mockResolvedValue({ data: [{ annotation_id:'1', action:'accept', from_status:'pending', to_status:'accepted', timestamp:'2020-01-01T00:00:00Z' }] }),
    },
  };
});

import useAnnotationStore from '../../src/stores/useAnnotationStore.js';

describe('useAnnotationStore - search', () => {
  beforeEach(() => {
    useAnnotationStore.setState({ sessionId: 'test', searchFilters: { statuses: [], codes: [], actions: [] }, searchResults: [], audit: {} });
  });

  it('runs search and populates results and audit', async () => {
    await act(async () => {
      await useAnnotationStore.getState().runSearch();
    });
    const st = useAnnotationStore.getState();
    expect(st.searchResults.length).toBe(1);
    expect(st.audit['1']).toBeDefined();
    expect(st.audit['1'][0].action).toBe('accept');
  });
});
