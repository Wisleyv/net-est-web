import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import api from '../services/api.js';
import { annotationsAPI } from '../services/api.js';
import useAppStore from './useAppStore.js';

/**
 * Annotation store (Phase 3.1 - Accept / Reject)
 * Holds current annotations (mirrors backend list endpoint semantics: hidden = rejected).
 */
const useAnnotationStore = create(devtools((set, get) => ({
  annotations: [],
  audit: {}, // map annotation_id -> events array
  searchResults: [],
  searchFilters: { statuses: [], codes: [], actions: [] },
  searchLoading: false,
  loading: false,
  error: null,
  sessionId: 'local',

  setSession: (sessionId) => set({ sessionId }, false, 'annotation/setSession'),
  setAnnotations: (annotations) => set({ annotations }, false, 'annotation/setAnnotations'),

  fetchAnnotations: async () => {
    const { sessionId } = get();
    set({ loading: true, error: null }, false, 'annotation/fetch/start');
    try {
      const res = await api.get(`/api/v1/annotations?session_id=${encodeURIComponent(sessionId)}`);
      set({ annotations: res.data.annotations || [], loading: false }, false, 'annotation/fetch/success');
    } catch (error) {
      set({ error: error.message || 'Erro ao carregar anotações', loading: false }, false, 'annotation/fetch/error');
    }
  },

  acceptAnnotation: async (id) => {
    const { sessionId, annotations } = get();
    // Optimistic update: mark as accepted
    const idx = annotations.findIndex(a => a.id === id || a.strategy_id === id);
    const prev = idx !== -1 ? annotations[idx] : null;
    if (prev) {
      const updated = { ...prev, status: 'accepted' };
      set({ annotations: [...annotations.slice(0, idx), updated, ...annotations.slice(idx + 1)] }, false, 'annotation/accept/optimistic');
    }
    try {
      const targetId = prev?.id || prev?.strategy_id || id;
      await api.patch(`/api/v1/annotations/${targetId}?session_id=${encodeURIComponent(sessionId)}`, { action: 'accept', session_id: sessionId });
    } catch (error) {
      // rollback
      if (prev) {
        set({ annotations: [...annotations.slice(0, idx), prev, ...annotations.slice(idx + 1)] }, false, 'annotation/accept/rollback');
      }
      useAppStore.getState().addNotification({ type: 'error', message: 'Falha ao aceitar anotação' });
    }
  },

  // Modify strategy code of an existing annotation (HITL)
  modifyAnnotation: async (id, newCode) => {
    const { sessionId, annotations } = get();
    const idx = annotations.findIndex(a => a.id === id || a.strategy_id === id);
    const prev = idx !== -1 ? annotations[idx] : null;
    if (!prev) return; // nothing to do
    // Optimistic update
    const updated = { ...prev, status: 'modified', original_code: prev.code || prev.strategy_code, code: newCode, strategy_code: newCode };
    set({ annotations: [...annotations.slice(0, idx), updated, ...annotations.slice(idx + 1)] }, false, 'annotation/modify/optimistic');
    try {
      const targetId = prev.id || prev.strategy_id || id;
      await api.patch(`/api/v1/annotations/${targetId}?session_id=${encodeURIComponent(sessionId)}`, { action: 'modify', session_id: sessionId, new_code: newCode });
    } catch (error) {
      // rollback
      set({ annotations: [...annotations.slice(0, idx), prev, ...annotations.slice(idx + 1)] }, false, 'annotation/modify/rollback');
      useAppStore.getState().addNotification({ type: 'error', message: 'Falha ao modificar código da anotação' });
    }
  },

  // Span editing flow (beta): select new offsets for an existing annotation
  editingAnnotationId: null,
  setEditingAnnotation: (annotationId) => set({ editingAnnotationId: annotationId }, false, 'annotation/editing/set'),
  clearEditingAnnotation: () => set({ editingAnnotationId: null }, false, 'annotation/editing/clear'),

  modifyAnnotationSpan: async (id, newTargetOffsets) => {
    const { sessionId, annotations } = get();
    const idx = annotations.findIndex(a => a.id === id || a.strategy_id === id);
    const prev = idx !== -1 ? annotations[idx] : null;
    if (!prev) return;
    // Optimistic update
    const updated = { ...prev, status: 'modified', target_offsets: newTargetOffsets };
    set({ annotations: [...annotations.slice(0, idx), updated, ...annotations.slice(idx + 1)] }, false, 'annotation/modifySpan/optimistic');
    try {
      const targetId = prev.id || prev.strategy_id || id;
      // Try a couple of common payload shapes
      try {
        await api.patch(`/api/v1/annotations/${targetId}?session_id=${encodeURIComponent(sessionId)}`, { action: 'modify_span', session_id: sessionId, target_offsets: newTargetOffsets });
      } catch (_) {
        await api.patch(`/api/v1/annotations/${targetId}?session_id=${encodeURIComponent(sessionId)}`, { action: 'modify', session_id: sessionId, target_offsets: newTargetOffsets });
      }
    } catch (error) {
      // rollback
      set({ annotations: [...annotations.slice(0, idx), prev, ...annotations.slice(idx + 1)] }, false, 'annotation/modifySpan/rollback');
      useAppStore.getState().addNotification({ type: 'error', message: 'Falha ao ajustar intervalo da anotação' });
    } finally {
      set({ editingAnnotationId: null }, false, 'annotation/editing/clear');
    }
  },

  rejectAnnotation: async (id) => {
    const { sessionId, annotations } = get();
    const idx = annotations.findIndex(a => a.id === id || a.strategy_id === id);
    const prev = idx !== -1 ? annotations[idx] : null;
    // Optimistic: remove from list (hidden) only if present
    if (prev) {
      set({ annotations: annotations.filter((_, i) => i !== idx) }, false, 'annotation/reject/optimistic');
    }
    try {
      const targetId = prev?.id || prev?.strategy_id || id;
      await api.patch(`/api/v1/annotations/${targetId}?session_id=${encodeURIComponent(sessionId)}`, { action: 'reject', session_id: sessionId });
    } catch (error) {
      // rollback
      if (prev) {
        set({ annotations: [...annotations.slice(0, idx), prev, ...annotations.slice(idx + 1)] }, false, 'annotation/reject/rollback');
      }
      useAppStore.getState().addNotification({ type: 'error', message: 'Falha ao rejeitar anotação' });
    }
  }
  ,

  createAnnotation: async ({ strategy_code, target_offsets, comment }, options = {}) => {
    const { sessionId, annotations } = get();
    const originalId = options.originalId; // preserve mapping to predicted strategy_id if provided
    
    // Test connectivity first
    try {
      await api.get('/health');
    } catch (connectivityError) {
      throw new Error('Backend não está acessível. Verifique se o servidor está executando.');
    }
    
    // optimistic id: if originalId provided, use it; else use temp
    const tempId = originalId || `temp_${Date.now()}`;
    const newAnn = {
      id: tempId,
      strategy_id: originalId || tempId,
      strategy_code,
      code: strategy_code,
      target_offsets,
      origin: 'human',
      status: 'created',
      comment: comment || null
    };
    set({ annotations: [...annotations, newAnn] }, false, 'annotation/create/optimistic');
    try {
      const res = await api.post(`/api/v1/annotations?session_id=${encodeURIComponent(sessionId)}`, {
        strategy_code,
        target_offsets,
        origin: 'human',
        status: 'created',
        comment
      });
      const real = res.data.annotation;
      // Replace temp but preserve originalId mapping in strategy_id so UI actions using predicted id continue to work
      set({ annotations: get().annotations.map(a => (a.id === tempId)
        ? { ...real, code: real.strategy_code, strategy_code: real.strategy_code, strategy_id: originalId || real.id }
        : a) }, false, 'annotation/create/commit');
    } catch (error) {
      
      // rollback
      set({ annotations: get().annotations.filter(a => a.id !== tempId) }, false, 'annotation/create/rollback');
      
      // Provide specific error feedback
      let errorMessage = 'Falha ao criar anotação';
      if (error.code === 'ERR_NETWORK' || error.message.includes('ERR_INTERNET_DISCONNECTED')) {
        errorMessage = 'Erro de rede: verifique a conexão com o servidor';
      } else if (error.response?.status === 404) {
        errorMessage = 'Endpoint de anotações não encontrado';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Erro interno do servidor';
      }
      
      console.error('Create annotation error:', error);
      useAppStore.getState().addNotification({ type: 'error', message: errorMessage });
      throw error; // Re-throw to allow caller to handle if needed
    }
  }
  ,

  fetchAudit: async (annotationId) => {
    const { sessionId, audit } = get();
    try {
      const res = await api.get(`/api/v1/annotations/audit?session_id=${encodeURIComponent(sessionId)}${annotationId ? `&annotation_id=${annotationId}`:''}`);
      if (annotationId) {
        set({ audit: { ...audit, [annotationId]: res.data } }, false, 'annotation/audit/one');
      } else {
        // group by annotation_id
        const grouped = res.data.reduce((acc, ev) => { (acc[ev.annotation_id] = acc[ev.annotation_id] || []).push(ev); return acc; }, {});
        set({ audit: grouped }, false, 'annotation/audit/all');
      }
    } catch (e) {
      // silent for now
    }
  },

  exportAnnotations: async (format='jsonl') => {
    const { sessionId } = get();
    const res = await api.post(`/api/v1/annotations/export?session_id=${encodeURIComponent(sessionId)}&format=${format}`);
    // The backend returns raw text (axios will parse if JSON but here it's text)
    const blob = new Blob([res.data], { type: format==='csv' ? 'text/csv' : 'application/x-ndjson' });
    if (typeof URL !== 'undefined' && typeof URL.createObjectURL === 'function') {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = format==='csv' ? 'annotations.csv' : 'annotations.jsonl';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 0);
    }
  }
  ,

  // Phase 4b: Audit Search
  setSearchFilters: (filters) => set({ searchFilters: { ...get().searchFilters, ...filters } }, false, 'annotation/search/setFilters'),
  resetSearch: () => set({ searchResults: [], searchFilters: { statuses: [], codes: [], actions: [] } }, false, 'annotation/search/reset'),
  runSearch: async () => {
    const { sessionId, searchFilters } = get();
    set({ searchLoading: true }, false, 'annotation/search/start');
    try {
      const { data } = await annotationsAPI.search({ sessionId, statuses: searchFilters.statuses, codes: searchFilters.codes });
      const anns = data?.annotations || [];
      // Fetch audits for returned annotations with action filter (optional)
      const ids = anns.map(a => a.id);
      let audits = {};
      if (ids.length) {
        const { data: auditArr } = await annotationsAPI.audit({ sessionId, actions: searchFilters.actions });
        audits = auditArr.reduce((acc, ev) => {
          if (!ids.includes(ev.annotation_id)) return acc;
          (acc[ev.annotation_id] = acc[ev.annotation_id] || []).push(ev);
          return acc;
        }, {});
      }
      set({ searchResults: anns, audit: { ...get().audit, ...audits }, searchLoading: false }, false, 'annotation/search/success');
    } catch (e) {
      set({ searchLoading: false }, false, 'annotation/search/error');
      useAppStore.getState().addNotification({ type: 'error', message: 'Falha na busca de auditoria' });
    }
  }
})));

export default useAnnotationStore;
