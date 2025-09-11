import React from 'react';
import useAnnotationStore from '../../stores/useAnnotationStore.js';
import useAppStore from '../../stores/useAppStore.js';

// Minimal HITL feedback control bar (Accept / Modify / Reject) for a strategy annotation
export default function FeedbackCollection({ strategy, onModifyStart }) {
  const enable = useAppStore(s => s.config.enableFeedbackActions);
  const { acceptAnnotation, rejectAnnotation } = useAnnotationStore();
  if (!strategy) return null;
  const enabled = !!enable;
  return (
  <div className="flex gap-2 mt-2" aria-label="Coleta de feedback" data-testid="feedback-collection" data-enabled={enabled ? 'true' : 'false'}>
  {enabled && <button
        type="button"
        onClick={() => acceptAnnotation(strategy.strategy_id)}
        className="px-2 py-1 text-xs rounded bg-green-100 text-green-800 border border-green-300 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-green-500"
        aria-label="Aceitar sugestão"
  >Aceitar</button>}
  {enabled && <button
        type="button"
        onClick={() => onModifyStart && onModifyStart(strategy)}
        className="px-2 py-1 text-xs rounded bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200 focus:outline-none focus:ring-2 focus:ring-amber-600"
        aria-label="Modificar código da estratégia"
  >Modificar</button>}
  {enabled && <button
        type="button"
        onClick={() => rejectAnnotation(strategy.strategy_id)}
        className="px-2 py-1 text-xs rounded bg-red-100 text-red-800 border border-red-300 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-600"
        aria-label="Rejeitar sugestão"
  >Rejeitar</button>}
    </div>
  );
}
