import React, { useMemo, useEffect } from 'react';
import useAppStore from '../../stores/useAppStore.js';
import useTimelineStore from '../../stores/useTimelineStore.js';
import useAnnotationStore from '../../stores/useAnnotationStore.js';

export default function AnnotationTimeline() {
  const enable = useAppStore(s => s.config.enableTimelineView);
  const { fetchAudit, fetchAnnotations } = useAnnotationStore.getState();
  const { filters, setFilters, buildTimeline } = useTimelineStore();

  useEffect(() => {
    if (!enable) return;
    // Ensure base data loaded
    fetchAnnotations();
    // Optionally fetch full audit
    fetchAudit();
  }, [enable]);

  const timeline = useMemo(() => enable ? buildTimeline() : [], [enable, filters, buildTimeline]);
  if (!enable) return null;

  return (
    <div className="annotation-timeline" aria-label="Linha do tempo de anotações">
      <h2 className="text-sm font-semibold mb-2">Linha do Tempo (Cliente)</h2>
      <div className="flex gap-2 mb-3 text-xs">
        <select aria-label="Filtrar por status" value={filters.status} onChange={e => setFilters({ status: e.target.value })}>
          <option value="all">Todos Status</option>
          <option value="created">Criados</option>
          <option value="modified">Modificados</option>
          <option value="accepted">Aceitos</option>
        </select>
        <input
          aria-label="Buscar por código"
          placeholder="Código"
          value={filters.code === 'all' ? '' : filters.code}
          onChange={e => setFilters({ code: e.target.value || 'all' })}
          className="border px-1"
        />
        <input
          aria-label="Busca livre"
            placeholder="Busca"
            value={filters.search}
            onChange={e => setFilters({ search: e.target.value })}
            className="border px-1"
        />
      </div>
      <ul className="space-y-1 text-xs">
        {timeline.filter(t => (filters.status==='all'|| t.status===filters.status) && (filters.code==='all'|| t.strategy_code===filters.code) && (!filters.search || t.strategy_code.includes(filters.search) || (t.comment||'').includes(filters.search))).map(t => (
          <li key={t.id} className="border rounded p-2 flex justify-between items-center">
            <div>
              <div className="font-mono text-[11px]">{t.strategy_code} · {t.status}</div>
              <div className="text-[10px] text-gray-600">Última ação: {t.lastAction}{t.lastTimestamp ? ` @ ${new Date(t.lastTimestamp).toLocaleTimeString()}`:''}</div>
              {t.original_code && t.original_code !== t.strategy_code && <div className="text-[10px] text-amber-700">orig: {t.original_code}</div>}
            </div>
            <div className="text-[10px] text-gray-500">{t.events.length} eventos</div>
          </li>
        ))}
        {timeline.length===0 && <li className="text-[11px] text-gray-500">Nenhuma anotação.</li>}
      </ul>
    </div>
  );
}
