import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import useAnnotationStore from './useAnnotationStore.js';

// Derives a timeline from annotations + audit events (client-only Phase 4a)
const useTimelineStore = create(devtools((set, get) => ({
  filters: { status: 'all', code: 'all', origin: 'all', search: '' },
  setFilters: (partial) => set(state => ({ filters: { ...state.filters, ...partial } }), false, 'timeline/setFilters'),

  // Build derived timeline entries
  buildTimeline: () => {
    const { annotations, audit } = useAnnotationStore.getState();
    const entries = [];
    // Map annotation id -> events sorted
    Object.values(annotations).forEach(a => {
      const events = audit[a.id] || audit[a.strategy_id] || [];
      const lastEvent = events[events.length - 1];
      entries.push({
        id: a.id || a.strategy_id,
        strategy_code: a.strategy_code || a.code,
        status: a.status,
        origin: a.origin,
        comment: a.comment,
        original_code: a.original_code,
        lastAction: lastEvent ? lastEvent.action : 'create',
        lastTimestamp: lastEvent ? lastEvent.timestamp : null,
        events: events
      });
    });
    return entries.sort((a,b) => (b.lastTimestamp || '').localeCompare(a.lastTimestamp || ''));
  }
})));

export default useTimelineStore;
