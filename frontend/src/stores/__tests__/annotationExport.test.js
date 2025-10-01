import { describe, it, expect, vi, beforeEach } from 'vitest';
import useAnnotationStore from '../useAnnotationStore.js';
import * as apiModule from '../../services/api.js';

// Mock api
vi.mock('../../services/api.js', () => {
  return {
    default: {
      post: vi.fn(() => Promise.resolve({ data: 'id,strategy_code,status'})),
      get: vi.fn()
    }
  };
});

describe('annotation export', () => {
  beforeEach(() => {
    useAnnotationStore.setState({ sessionId: 'test_session' });
  });

  it('calls backend with correct query for jsonl', async () => {
    const { exportAnnotations } = useAnnotationStore.getState();
    await exportAnnotations('jsonl');
    expect(apiModule.default.post).toHaveBeenCalledWith(expect.stringContaining('/api/v1/annotations/export?session_id=test_session&format=jsonl'));
  });

  it('calls backend with correct query for csv', async () => {
    const { exportAnnotations } = useAnnotationStore.getState();
    await exportAnnotations('csv');
    expect(apiModule.default.post).toHaveBeenCalledWith(expect.stringContaining('/api/v1/annotations/export?session_id=test_session&format=csv'));
  });
});
