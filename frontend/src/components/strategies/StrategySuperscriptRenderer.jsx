import React, { useMemo } from 'react';
import { normalizeStrategies, buildInsertionPoints, buildSentenceFallback, assignDisplayIndices } from '../../utils/strategyOffsets.js';
import { getStrategyColor, STRATEGY_METADATA } from '../../services/strategyColorMapping.js';

function getContrastText(hex) {
  if (!hex) return '#000';
  const c = hex.replace('#','');
  if (c.length !== 6) return '#000';
  const r = parseInt(c.slice(0,2),16);
  const g = parseInt(c.slice(2,4),16);
  const b = parseInt(c.slice(4,6),16);
  const luminance = (0.299*r + 0.587*g + 0.114*b)/255;
  return luminance > 0.6 ? '#000' : '#fff';
}

// Phase 2a additive component: renders superscript markers over target text.
// Displays strategy codes (e.g., ADD+, GEN+) at detected positions (Phase 2b correction)
// unifiedMap (optional): { [code]: { markerColor, textColor, borderColor } }
export default function StrategySuperscriptRenderer({ targetText, strategies, onMarkerActivate, activeStrategyId, rovingIndex = 0, onRovingIndexChange = () => {}, colorblindMode = false, unifiedMap = {} }) {
  const containerRef = React.useRef(null);
  const { nodes } = useMemo(() => {
    if (!targetText) return { nodes: [targetText] };
    const normalized = normalizeStrategies(strategies);
    const points = buildInsertionPoints(normalized, targetText.length);
    if (points.length === 0) {
      // Sentence fallback
      const { sentences, mapping } = buildSentenceFallback(normalized, targetText);
      const { indexMap } = assignDisplayIndices(mapping.map(m => ({ pos: m.sentenceIdx, id: m.id })));
      const out = [];
      sentences.forEach((sent, i) => {
        out.push(<span key={`sent-${i}`}>{sent}</span>);
        const related = mapping.filter(m => m.sentenceIdx === i);
        related.forEach(r => {
          const num = indexMap.get(r.id);
          // Attempt to find strategy code from normalized array
      const strat = normalized.find(s => s.strategy_id === r.id);
      const label = strat?.code || String(num);
      const mapEntry = unifiedMap[label];
      const bg = mapEntry ? mapEntry.markerColor : getStrategyColor(label, colorblindMode);
      const textColor = mapEntry ? mapEntry.textColor : getContrastText(bg);
      const fullName = STRATEGY_METADATA[label]?.name || label;
  const accepted = strat?.status === 'accepted';
  const modified = strat?.status === 'modified';
  const created = strat?.status === 'created' || strat?.origin === 'human';
  const borderStyle = accepted ? { boxShadow: '0 0 0 2px #16a34a' } : (modified ? { boxShadow: '0 0 0 2px #d97706' } : (created ? { boxShadow: '0 0 0 2px #2563eb' } : {}));
          out.push(
            <sup
              key={`m-fallback-${r.id}`}
              className="strategy-marker"
              tabIndex={0}
              data-strategy-id={r.id}
              data-code={label}
        style={{ background: bg, color: textColor, borderColor: bg, ...borderStyle }}
              onClick={() => onMarkerActivate && onMarkerActivate(r.id)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onMarkerActivate && onMarkerActivate(r.id); } }}
  aria-label={`Estratégia ${label} - ${fullName}${accepted ? ' (aceita)' : ''}${modified ? ` (modificada${strat?.original_code ? ' de ' + strat.original_code : ''})` : ''}${created ? ' (criada manualmente)' : ''}`}
            >{label}</sup>
          );
        });
        out.push(' ');
      });
      return { nodes: out };
    }
    const { indexMap } = assignDisplayIndices(points);
    const out = [];
    let cursor = 0;
    points.forEach((p, idx) => {
      if (p.pos > cursor) {
        out.push(<span key={`seg-${cursor}`}>{targetText.slice(cursor, p.pos)}</span>);
      }
      // Find strategy code for display
  const strat = normalized.find(s => s.strategy_id === p.id);
      const label = strat?.code || 'STR';
      const isActive = activeStrategyId === p.id;
  const mapEntry = unifiedMap[label];
  const color = mapEntry ? mapEntry.markerColor : getStrategyColor(label, colorblindMode);
  const textColor = mapEntry ? mapEntry.textColor : getContrastText(color);
  const fullName = STRATEGY_METADATA[label]?.name || label;
  const accepted = strat?.status === 'accepted';
  const modified = strat?.status === 'modified';
  const created = strat?.status === 'created' || strat?.origin === 'human';
  const outline = isActive ? { boxShadow: '0 0 0 2px rgba(0,0,0,0.25)' } : (accepted ? { boxShadow: '0 0 0 2px #16a34a' } : (modified ? { boxShadow: '0 0 0 2px #d97706' } : (created ? { boxShadow: '0 0 0 2px #2563eb' } : {})));
      out.push(
        <sup
          key={`m-${p.pos}-${p.id}`}
          className="strategy-marker"
          tabIndex={rovingIndex === idx ? 0 : -1}
          data-strategy-id={p.id}
          data-code={label}
          data-active={isActive ? 'true' : 'false'}
          data-roving-index={idx}
          aria-current={isActive ? 'true' : undefined}
          onClick={(e) => onMarkerActivate && onMarkerActivate(p.id, e.currentTarget, idx)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onMarkerActivate && onMarkerActivate(p.id, e.currentTarget, idx); }
            else if (e.key === 'ArrowRight') { e.preventDefault(); onRovingIndexChange(Math.min(points.length - 1, idx + 1)); }
            else if (e.key === 'ArrowLeft') { e.preventDefault(); onRovingIndexChange(Math.max(0, idx - 1)); }
            else if (e.key === 'Home') { e.preventDefault(); onRovingIndexChange(0); }
            else if (e.key === 'End') { e.preventDefault(); onRovingIndexChange(points.length - 1); }
          }}
          aria-label={`Estratégia ${label} - ${fullName}${isActive ? ' (ativa)' : ''}${accepted ? ' (aceita)' : ''}${modified ? ` (modificada${strat?.original_code ? ' de ' + strat.original_code : ''})` : ''}${created ? ' (criada manualmente)' : ''}`}
          style={{ background: color, color: textColor, borderColor: color, ...outline }}
        >{label}</sup>
      );
      cursor = p.pos;
    });
    if (cursor < targetText.length) {
      out.push(<span key={`tail-${cursor}`}>{targetText.slice(cursor)}</span>);
    }
    return { nodes: out };
  }, [targetText, strategies, onMarkerActivate]);

  // Focus management for roving index
  React.useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current.querySelector(`sup.strategy-marker[data-roving-index='${rovingIndex}']`);
    if (el) {
      // Only shift focus if element is not already focused
      if (document.activeElement !== el) {
        el.focus();
      }
    }
  }, [rovingIndex, nodes]);

  return <div ref={containerRef} className="strategy-superscript-layer" role="group" aria-label="Marcadores de estratégias" >{nodes}</div>;
}
