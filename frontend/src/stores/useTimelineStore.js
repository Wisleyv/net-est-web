/**
 * Timeline Store
 * Manages timeline view state and filters for annotations
 */

import { create } from 'zustand';
import useAnnotationStore from './useAnnotationStore.js';

const useTimelineStore = create((set, get) => ({
  // Timeline filters
  filters: {
    status: 'all',
    code: 'all',
    search: ''
  },

  // Set filters
  setFilters: (newFilters) => set((state) => ({
    filters: { ...state.filters, ...newFilters }
  })),

  // Build timeline from annotations
  buildTimeline: () => {
    const annotations = useAnnotationStore.getState().annotations || [];
    
    // Transform annotations into timeline entries
    const timeline = annotations.map(annotation => ({
      id: annotation.id || `ann_${Date.now()}_${Math.random()}`,
      strategy_code: annotation.strategy_code || 'UNKNOWN',
      status: annotation.status || 'created',
      comment: annotation.comment || '',
      lastAction: annotation.status || 'created',
      lastTimestamp: annotation.created_at || annotation.updated_at || new Date().toISOString(),
      original_code: annotation.original_strategy_code || null,
      events: [
        {
          action: 'created',
          timestamp: annotation.created_at || new Date().toISOString(),
          details: `Annotation created with strategy ${annotation.strategy_code}`
        }
      ]
    }));

    // Sort by timestamp (newest first)
    timeline.sort((a, b) => new Date(b.lastTimestamp) - new Date(a.lastTimestamp));

    return timeline;
  },

  // Reset filters
  resetFilters: () => set({
    filters: {
      status: 'all',
      code: 'all',
      search: ''
    }
  })
}));

export default useTimelineStore;