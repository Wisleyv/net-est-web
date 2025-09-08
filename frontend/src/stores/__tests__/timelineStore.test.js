import { describe, it, expect, beforeEach } from 'vitest';
import useAnnotationStore from '../useAnnotationStore.js';
import useTimelineStore from '../useTimelineStore.js';

describe('timeline store', () => {
  beforeEach(() => {
    useAnnotationStore.setState({ annotations: [
      { id:'a1', strategy_code:'OM+', code:'OM+', status:'created', origin:'human' },
      { id:'a2', strategy_code:'SL+', code:'SL+', status:'modified', origin:'human', original_code:'OM+' }
    ], annotationsLoaded:true });
    useAnnotationStore.setState({ audit: {
      a1: [{ action:'create', timestamp:'2025-09-08T10:00:00Z' }],
      a2: [{ action:'create', timestamp:'2025-09-08T10:01:00Z' }, { action:'modify', timestamp:'2025-09-08T10:02:00Z' }]
    }});
    useTimelineStore.setState({ filters: { status:'all', code:'all', origin:'all', search:'' } });
  });

  it('builds timeline entries sorted by last timestamp desc', () => {
    const { buildTimeline } = useTimelineStore.getState();
    const list = buildTimeline();
    expect(list[0].id).toBe('a2');
    expect(list[1].id).toBe('a1');
  });
});
