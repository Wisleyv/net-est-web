import React, { useMemo } from 'react';
import { normalizeStrategies, __diag_normalizeStrategies, buildInsertionPoints, buildSentenceFallback, assignDisplayIndices } from '../../utils/strategyOffsets.js';
import { buildRangeHighlighting, buildHighlightedNodes } from '../../utils/rangeHighlighting.jsx';
import { getStrategyColor, STRATEGY_METADATA } from '../../services/strategyColorMapping.js';

function getContrastText(hex) {
  // Simple luminance calculation to determine if text should be white or black
  if (!hex || !hex.startsWith('#')) return '#000000';
  
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

// Phase 2a additive component: renders superscript markers over target text.
// Displays strategy codes (e.g., ADD+, GEN+) at detected positions (Phase 2b correction)
// unifiedMap (optional): { [code]: { markerColor, textColor, borderColor } }
export default function StrategySuperscriptRenderer({ 
  targetText, 
  strategies, 
  onMarkerActivate, 
  activeStrategyId, 
  rovingIndex = 0, 
  onRovingIndexChange = () => {}, 
  colorblindMode = false, 
  unifiedMap = {},
  // Phase 2B: Hover event handlers
  onMarkerHover,
  onMarkerLeave,
  // Add prop to disable focus management when rationale dialog is open
  disableFocusManagement = false
}) {
  const containerRef = React.useRef(null);
  const { nodes } = useMemo(() => {
    if (!targetText) return { nodes: [targetText] };
    // DEV diagnostics (concise)
    if (typeof window !== 'undefined' && import.meta.env.DEV) {
      try {
        console.log('🔍 StrategySuperscriptRenderer input data:');
        console.log('  targetText length:', targetText.length);
        console.log('  strategies count:', strategies.length);
        console.log('  strategies sample:', strategies.slice(0, 3).map(s => ({
          id: s.strategy_id,
          code: s.code,
          target_offsets: s.target_offsets
        })));
      } catch (diagErr) {
        console.warn('DEV: failed to log input data', diagErr);
      }
      
      try {
        const incomingCount = Array.isArray(strategies) ? strategies.length : 'not-array';
        console.debug('DEV: incoming strategies count=', incomingCount);
      } catch (diagErr) {
        console.warn('DEV: failed to log incoming strategies', diagErr);
      }
    }

    const normalized = (typeof window !== 'undefined' && import.meta.env && import.meta.env.DEV && __diag_normalizeStrategies) ? __diag_normalizeStrategies(strategies) : normalizeStrategies(strategies);
    
    // Use new range highlighting approach instead of just insertion points
    const { ranges, insertionPoints } = buildRangeHighlighting(normalized, targetText.length);
    
    if (typeof window !== 'undefined' && import.meta.env.DEV) {
      try { 
        console.debug('DEV: normalized strategies summary=', JSON.stringify(normalized.slice(0,3).map(s => ({ id: s.strategy_id, code: s.code, status: s.status, target_offsets: s.target_offsets })), null, 2)); 
        console.debug('DEV: ranges for highlighting=', ranges.slice(0, 3));
        console.debug('DEV: insertion points for markers=', insertionPoints.slice(0, 3));
      } catch(e) { 
        console.debug('DEV: range highlighting debug failed', e); 
      }
    }

    if (ranges.length === 0 && insertionPoints.length === 0) {
      // Sentence fallback for backward compatibility
      const { sentences, mapping } = buildSentenceFallback(normalized, targetText);
      const { indexMap } = assignDisplayIndices(mapping.map(m => ({ pos: m.sentenceIdx, id: m.id })));
      const out = [];
      sentences.forEach((sent, i) => {
        out.push(<span key={`sent-${i}`}>{sent}</span>);
        const related = mapping.filter(m => m.sentenceIdx === i);
        related.forEach(r => {
          const num = indexMap.get(r.id);
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
              data-status={accepted ? 'accepted' : (modified ? 'modified' : (created ? 'created' : undefined))}
              data-origin={created ? 'human' : undefined}
              data-testid="strategy-marker"
              style={{ background: bg, color: textColor, borderColor: bg, ...borderStyle }}
              onClick={(e) => onMarkerActivate && onMarkerActivate(r.id, e.currentTarget)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onMarkerActivate && onMarkerActivate(r.id, e.currentTarget); } }}
              aria-label={`Estratégia ${label} - ${fullName}${accepted ? ' (aceita)' : ''}${modified ? ` (modificada${strat?.original_code ? ' de ' + strat.original_code : ''})` : ''}${created ? ' (criada manualmente)' : ''}`}
            >{label}</sup>
          );
        });
        out.push(' ');
      });
      return { nodes: out };
    }
    
    // NEW: Use range highlighting with both background spans and markers
    const colorMapping = {};
    normalized.forEach(s => {
      if (s.code) {
        const mapEntry = unifiedMap[s.code];
        colorMapping[s.code] = mapEntry ? mapEntry.markerColor : getStrategyColor(s.code, colorblindMode);
      }
    });
    
    const markerRenderer = (marker) => {
      const strat = normalized.find(s => s.strategy_id === marker.id);
      const label = strat?.code || 'STR';
      const mapEntry = unifiedMap[label];
      const color = mapEntry ? mapEntry.markerColor : getStrategyColor(label, colorblindMode);
      const textColor = mapEntry ? mapEntry.textColor : getContrastText(color);
      const fullName = STRATEGY_METADATA[label]?.name || label;
      const accepted = strat?.status === 'accepted';
      const modified = strat?.status === 'modified';
      const created = strat?.status === 'created' || strat?.origin === 'human';
      const outline = accepted ? { boxShadow: '0 0 0 2px #16a34a' } : (modified ? { boxShadow: '0 0 0 2px #d97706' } : (created ? { boxShadow: '0 0 0 2px #2563eb' } : {}));
      
      return (
        <sup
          key={`marker-${marker.pos}-${marker.id}`}
          className="strategy-marker"
          tabIndex={0}
          data-strategy-id={marker.id}
          data-code={label}
          data-status={accepted ? 'accepted' : (modified ? 'modified' : (created ? 'created' : undefined))}
          data-origin={created ? 'human' : undefined}
          data-testid="strategy-marker"
          onClick={(e) => onMarkerActivate && onMarkerActivate(marker.id, e.currentTarget)}
          onMouseEnter={(e) => onMarkerHover && onMarkerHover(marker.id, e.currentTarget)}
          onMouseLeave={onMarkerLeave}
          onKeyDown={(e) => { 
            if (e.key === 'Enter' || e.key === ' ') { 
              e.preventDefault(); 
              onMarkerActivate && onMarkerActivate(marker.id, e.currentTarget); 
            } 
          }}
          aria-label={`Estratégia ${label} - ${fullName}${accepted ? ' (aceita)' : ''}${modified ? ` (modificada${strat?.original_code ? ' de ' + strat.original_code : ''})` : ''}${created ? ' (criada manualmente)' : ''}`}
          style={{ background: color, color: textColor, borderColor: color, ...outline }}
        >{label}</sup>
      );
    };
    
    const highlightedNodes = buildHighlightedNodes(targetText, ranges, insertionPoints, {
      colorMapping,
      markerRenderer
    });
    
    return { nodes: highlightedNodes };
  }, [targetText, strategies, onMarkerActivate]);

  // Focus management for roving index
  React.useEffect(() => {
    // Don't manage focus if rationale dialog is open or focus management is disabled
    if (disableFocusManagement || !containerRef.current) return;
    
    const el = containerRef.current.querySelector(`sup.strategy-marker[data-roving-index='${rovingIndex}']`);
    if (el) {
      // Only shift focus if element is not already focused
      if (document.activeElement !== el) {
        el.focus();
      }
    }
  }, [rovingIndex, nodes, disableFocusManagement]);

  return <div ref={containerRef} className="strategy-superscript-layer" role="group" aria-label="Marcadores de estratégias" data-testid="strategy-superscript-layer">{nodes}</div>;
}
