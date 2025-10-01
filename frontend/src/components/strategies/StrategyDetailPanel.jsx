import React, { useEffect, useMemo, useCallback, useRef, useState } from 'react';
import useAppStore from '../../stores/useAppStore.js';
import useAnnotationStore from '../../stores/useAnnotationStore.js';
import { X } from 'lucide-react';
import { normalizeStrategies, buildInsertionPoints, buildSentenceFallback, assignDisplayIndices } from '../../utils/strategyOffsets.js';
import { STRATEGY_METADATA, getStrategyColor, getStrategyInfo } from '../../services/strategyColorMapping.js';
import FeedbackCollection from './FeedbackCollection.jsx';

/**
 * Phase 2b: StrategyDetailPanel
 * Accessible side panel showing detailed info about a selected simplification strategy.
 * Non-breaking additive feature.
 */
export default function StrategyDetailPanel({
  targetText,
  sourceText = '',
  rawStrategies = [],
  activeStrategyId = null,
  onClose = () => {},
  useColorblindFriendly = false,
  returnFocusTo = null, // DOM element to restore focus to on close
}) {
  // Normalize and build numbering consistent with superscript renderer
  const { strategies, numberMap } = useMemo(() => {
    const norm = normalizeStrategies(rawStrategies);
    let points = buildInsertionPoints(norm, (targetText || '').length);
    let numberMap;
    if (points.length === 0) {
      const { mapping } = buildSentenceFallback(norm, targetText || '');
      const assigned = assignDisplayIndices(mapping.map(m => ({ pos: m.sentenceIdx, id: m.id })));
      numberMap = assigned.indexMap;
    } else {
      const assigned = assignDisplayIndices(points);
      numberMap = assigned.indexMap;
    }
    return { strategies: norm, numberMap };
  }, [rawStrategies, targetText]);

  const active = useMemo(() => strategies.find(s => s.strategy_id === activeStrategyId), [strategies, activeStrategyId]);
  const enableFeedbackActions = useAppStore(s => s.config.enableFeedbackActions);
  const { acceptAnnotation, rejectAnnotation, modifyAnnotation, setEditingAnnotation, modifyAnnotationSpan, clearEditingAnnotation } = useAnnotationStore();
  const { fetchAudit, exportAnnotations, audit } = useAnnotationStore();
  const [showAudit, setShowAudit] = useState(false);
  const [modifying, setModifying] = useState(false);
  const [newCode, setNewCode] = useState('');
  const [spanEditing, setSpanEditing] = useState(false);

  const headerRef = useRef(null);
  // Close on ESC
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Focus management when panel opens
  useEffect(() => {
    if (activeStrategyId && headerRef.current) {
      // Delay to ensure rendering complete
  setTimeout(() => headerRef.current && headerRef.current.focus(), 0);
    }
  }, [activeStrategyId]);

  // Restore focus to previously active marker when closing
  useEffect(() => {
    if (!activeStrategyId && returnFocusTo) {
      setTimeout(() => {
        try { returnFocusTo.focus(); } catch (_) { /* focus restore noop */ }
      }, 0);
    }
  }, [activeStrategyId, returnFocusTo]);

  // Clear span editing mode on close/unmount
  useEffect(() => () => { try { clearEditingAnnotation(); } catch (e) { /* ignore */ } }, [clearEditingAnnotation]);

  const stop = useCallback(e => e.stopPropagation(), []);

  if (!activeStrategyId || !active) return null;

  if (import.meta?.env?.DEV) {
    try {
      // eslint-disable-next-line no-console
      console.log('[NET-EST] StrategyDetailPanel render', {
        activeStrategyId,
        enableFeedbackActions,
        hasAudit: !!audit[activeStrategyId],
      });
    } catch {}
  }

  const meta = STRATEGY_METADATA[active.code] || getStrategyInfo(active.code) || {};
  const color = getStrategyColor(active.code, useColorblindFriendly);
  const displayIndex = numberMap.get(active.strategy_id);
  const modifiedFrom = active.original_code && active.status === 'modified' ? active.original_code : null;
  const canonicalCodes = Object.keys(STRATEGY_METADATA || {});

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Detalhes da estratégia de simplificação"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md h-full bg-white shadow-xl border-l border-gray-200 flex flex-col animate-slide-in"
        onClick={stop}
      >
  <div className="flex items-start justify-between p-4 border-b border-gray-200" ref={headerRef} tabIndex={-1}>
          <div>
            <div className="flex items-center gap-2">
              <span
                className="inline-flex items-center justify-center w-8 h-8 rounded text-xs font-bold"
                style={{ backgroundColor: color, color: '#fff' }}
              >
                {active.code}
              </span>
              <h2 className="text-sm font-semibold text-gray-900 leading-tight">
                Estratégia {displayIndex ? `#${displayIndex}` : ''} – {meta.name || active.name || active.code} {modifiedFrom ? <span className="text-[10px] ml-1 px-1 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300" aria-label={`Modificada de ${modifiedFrom}`}>mod</span> : null}
              </h2>
            </div>
            {meta.description && (
              <p className="mt-2 text-xs text-gray-600 pr-6">{meta.description}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-800 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Fechar painel de detalhes"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
          {enableFeedbackActions && (
            <div className="flex justify-between items-center mb-2">
              <button
                type="button"
                onClick={() => exportAnnotations('jsonl')}
                className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 border border-blue-300 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Exportar anotações em JSONL"
              >Exportar JSONL</button>
              <button
                type="button"
                onClick={() => exportAnnotations('csv')}
                className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 border border-blue-300 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Exportar anotações em CSV"
              >Exportar CSV</button>
            </div>
          )}
          <section>
            <h3 className="font-medium text-gray-800 mb-1">Confiança</h3>
            <div className="text-xs text-gray-700">
              {typeof active.confidence_score === 'number' ? `${(active.confidence_score * 100).toFixed(1)}%` :
               typeof active.confidence === 'number' ? `${(active.confidence * 100).toFixed(1)}%` : 'N/A'}
            </div>
          </section>
          {active.explanation && (
            <section>
              <h3 className="font-medium text-gray-800 mb-1">Explicação</h3>
              <p className="text-xs text-gray-700" data-testid="strategy-explanation">{active.explanation}</p>
            </section>
          )}
          {/* Evidence: prefer evidence array; fallback to examples */}
          {(Array.isArray(active.evidence) && active.evidence.length > 0) || (Array.isArray(active.examples) && active.examples.length > 0) ? (
            <section>
              <h3 className="font-medium text-gray-800 mb-1">Evidências / Exemplos</h3>
              <ul className="list-disc list-inside text-xs text-gray-700 space-y-2">
                {Array.isArray(active.evidence) && active.evidence.length > 0 && active.evidence.map((ev, i) => (
                  <li key={`ev-${i}`}>{ev}</li>
                ))}
                {(!active.evidence || active.evidence.length === 0) && Array.isArray(active.examples) && active.examples.map((ex, i) => (
                  <li key={`ex-${i}`}><span className="font-semibold">Orig:</span> {ex.original || '—'} <span className="font-semibold ml-1">Simpl.:</span> {ex.simplified || '—'}</li>
                ))}
              </ul>
            </section>
          ) : null}

          {/* Target offsets (array or single dict) */}
          {(() => {
            const to = active.target_offsets;
            if (Array.isArray(to) && to.length > 0) {
              return (
                <section>
                  <h3 className="font-medium text-gray-800 mb-1">Offsets no texto simplificado</h3>
                  <div className="text-xs text-gray-700 space-y-1">
                    {to.map((r, i) => (
                      <div key={i}>[{r.start}, {r.end}] → "{(targetText || '').slice(r.start, r.end)}"</div>
                    ))}
                  </div>
                </section>
              );
            } else if (to && typeof to === 'object' && typeof to.char_start === 'number') {
              const r = { start: to.char_start, end: to.char_end };
              return (
                <section>
                  <h3 className="font-medium text-gray-800 mb-1">Offsets no texto simplificado</h3>
                  <div className="text-xs text-gray-700">[{r.start}, {r.end}] → "{(targetText || '').slice(r.start, r.end)}"</div>
                </section>
              );
            }
            return null;
          })()}

          {(() => {
            const so = active.source_offsets;
            if (Array.isArray(so) && so.length > 0) {
              return (
                <section>
                  <h3 className="font-medium text-gray-800 mb-1">Offsets no texto fonte</h3>
                  <div className="text-xs text-gray-700 space-y-1">
                    {so.map((r, i) => (
                      <div key={i}>[{r.start}, {r.end}] → "{(sourceText || '').slice(r.start, r.end)}"</div>
                    ))}
                  </div>
                </section>
              );
            } else if (so && typeof so === 'object' && typeof so.char_start === 'number') {
              const r = { start: so.char_start, end: so.char_end };
              return (
                <section>
                  <h3 className="font-medium text-gray-800 mb-1">Offsets no texto fonte</h3>
                  <div className="text-xs text-gray-700">[{r.start}, {r.end}] → "{(sourceText || '').slice(r.start, r.end)}"</div>
                </section>
              );
            }
            return null;
          })()}

          <section>
            <h3 className="font-medium text-gray-800 mb-1">Metadados</h3>
            <dl className="text-xs text-gray-700 space-y-1">
              <div><dt className="inline font-semibold">ID:</dt> <dd className="inline break-all">{active.strategy_id}</dd></div>
              {active.model_version && <div><dt className="inline font-semibold">Modelo:</dt> <dd className="inline">{active.model_version}</dd></div>}
              {active.type && <div><dt className="inline font-semibold">Tipo:</dt> <dd className="inline">{active.type}</dd></div>}
            </dl>
          </section>

          {enableFeedbackActions && (
            <section>
              <button
                type="button"
                className="text-xs underline text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-expanded={showAudit}
                onClick={() => { if (!showAudit) fetchAudit(active.strategy_id); setShowAudit(s => !s); }}
              >{showAudit ? 'Ocultar histórico' : 'Mostrar histórico de auditoria'}</button>
              {showAudit && (
                <div className="mt-2 border rounded p-2 bg-gray-50 text-[11px] max-h-40 overflow-auto" aria-label="Histórico de auditoria">
                  {(audit[active.strategy_id] || []).map((ev,i) => {
                    const changedCode = ev.from_code && ev.to_code && ev.from_code !== ev.to_code;
                    return (
                      <div key={i} className="flex flex-col py-1 border-b last:border-b-0">
                        <div className="flex justify-between text-[10px]">
                          <span className="font-mono">{ev.action}</span>
                          <span>{ev.from_status || '—'} → {ev.to_status}</span>
                          <span className="text-gray-500">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                        </div>
                        {changedCode && (
                          <div className="mt-0.5 text-[10px] font-mono"><span className="text-red-600 line-through mr-1">{ev.from_code}</span><span className="text-gray-500">→</span><span className="text-green-700 ml-1">{ev.to_code}</span></div>
                        )}
                      </div>
                    );
                  })}
                  {(!audit[active.strategy_id] || audit[active.strategy_id].length===0) && <div className="text-gray-500">Sem eventos.</div>}
                </div>
              )}
            </section>
          )}
        </div>

        <div className="p-3 border-t border-gray-200 flex justify-end">
          {enableFeedbackActions && (
            <div className="flex gap-2 items-center mr-auto" aria-label="Ações de validação">
              <FeedbackCollection strategy={active} onModifyStart={() => { setModifying(true); setNewCode(active.code); }} />
              <button
                type="button"
                onClick={() => acceptAnnotation(active.strategy_id)}
                className="px-3 py-1.5 text-xs rounded font-medium focus:outline-none focus:ring-2 focus:ring-green-500 bg-green-100 hover:bg-green-200 text-green-800 border border-green-300"
                aria-label="Aceitar anotação"
              >Aceitar</button>
              <button
                type="button"
                onClick={() => { rejectAnnotation(active.strategy_id); onClose(); }}
                className="px-3 py-1.5 text-xs rounded font-medium focus:outline-none focus:ring-2 focus:ring-red-500 bg-red-100 hover:bg-red-200 text-red-800 border border-red-300"
                aria-label="Rejeitar anotação"
              >Rejeitar</button>
              <button
                type="button"
                onClick={() => { setEditingAnnotation(active.strategy_id); setSpanEditing(true); }}
                className="px-3 py-1.5 text-xs rounded font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-indigo-100 hover:bg-indigo-200 text-indigo-800 border border-indigo-300"
                aria-label="Ajustar intervalo no texto"
              >Ajustar intervalo</button>
              <div className="relative" aria-label="Modificar estratégia">
                {!modifying && (
                  <button
                    type="button"
                    onClick={() => { setModifying(true); setNewCode(active.code); }}
                    className="px-3 py-1.5 text-xs rounded font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 bg-amber-100 hover:bg-amber-200 text-amber-800 border border-amber-300"
                    aria-label="Modificar código da estratégia"
                  >Modificar</button>
                )}
                {modifying && (
                  <div className="flex items-center gap-2" role="group" aria-label="Editor de modificação de estratégia">
                    <label className="sr-only" htmlFor="modify-code-select">Novo código</label>
                    <select
                      id="modify-code-select"
                      className="text-xs border rounded px-1 py-1 focus:outline-none focus:ring-2 focus:ring-amber-500"
                      value={newCode}
                      onChange={e => setNewCode(e.target.value)}
                    >
                      {canonicalCodes.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                    <button
                      type="button"
                      onClick={() => { try { modifyAnnotation(active.strategy_id, newCode); } finally { setModifying(false); } }}
                      className="px-2 py-1 text-xs rounded bg-amber-600 text-white hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
                      aria-label="Confirmar modificação"
                    >OK</button>
                    <button
                      type="button"
                      onClick={() => { setModifying(false); setNewCode(''); }}
                      className="px-2 py-1 text-xs rounded bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400"
                      aria-label="Cancelar modificação"
                    >Cancelar</button>
                  </div>
                )}
              </div>
            </div>
          )}
          {spanEditing && (
            <div className="text-[11px] text-gray-600 mr-auto" role="status">
              Selecione um novo trecho no "Texto Simplificado" para atualizar os offsets desta anotação.
            </div>
          )}
          {!enableFeedbackActions && import.meta?.env?.DEV && (
            <button
              type="button"
              onClick={() => {
                const st = useAppStore.getState();
                useAppStore.setState({ config: { ...st.config, enableFeedbackActions: true } });
              }}
              className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 border border-blue-300 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >Ativar feedback (dev)</button>
          )}
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >Fechar</button>
        </div>
      </div>
    </div>
  );
}
