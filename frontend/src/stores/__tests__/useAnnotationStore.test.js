import { describe, beforeEach, test, expect, vi } from 'vitest';
import useAnnotationStore from '../useAnnotationStore.js';
import api from '../../services/api.js';

// Basic unit tests for accept / reject transitions (Phase 3.1)

describe('useAnnotationStore (Phase 3.1)', () => {
  beforeEach(() => {
    const { setAnnotations, setSession } = useAnnotationStore.getState();
    setSession('test');
    setAnnotations([
      { id: 'a1', strategy_id: 'a1', code: 'ADD+', status: 'pending' },
      { id: 'a2', strategy_id: 'a2', code: 'GEN+', status: 'pending' }
    ]);
  });

  test('acceptAnnotation marks status accepted optimistically', async () => {
    vi.spyOn(api, 'patch').mockResolvedValue({ data: { ok: true } });
    await useAnnotationStore.getState().acceptAnnotation('a1');
    const ann = useAnnotationStore.getState().annotations.find(a => a.id === 'a1');
    expect(ann.status).toBe('accepted');
  });

  test('rejectAnnotation removes item optimistically', async () => {
    vi.spyOn(api, 'patch').mockResolvedValue({ data: { ok: true } });
    const { rejectAnnotation } = useAnnotationStore.getState();
    await rejectAnnotation('a2');
    const exists = useAnnotationStore.getState().annotations.find(a => a.id === 'a2');
    expect(exists).toBeUndefined();
  });

  test.skip('modifyAnnotation updates code and status, preserves original_code (implemented in later patch)', async () => {});

  test('createAnnotation adds new annotation with created status', async () => {
    const apiResponse = { annotation: { id: 'real123', strategy_code: 'OM+', target_offsets: [{ start: 0, end: 5 }], status: 'created', origin: 'human' } };
    vi.spyOn(api, 'post').mockResolvedValue({ data: apiResponse });
    const { createAnnotation } = useAnnotationStore.getState();
    await createAnnotation({ strategy_code: 'OM+', target_offsets: [{ start: 0, end: 5 }] });
    const created = useAnnotationStore.getState().annotations.find(a => a.id === 'real123');
    expect(created).toBeDefined();
    expect(created.status).toBe('created');
    expect(created.origin).toBe('human');
  });
});
