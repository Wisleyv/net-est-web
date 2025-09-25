import React, { useMemo } from 'react';
import { STRATEGY_METADATA } from '../../services/strategyColorMapping.js';

/**
 * Phase 2c: StrategyFilterBar
 * - Checkbox per strategy code present in current analysis
 * - Select all / none controls
 * - Confidence threshold slider (0-100%)
 * - Colorblind mode toggle
 * Accessible, additive, non-regressive.
 */
export default function StrategyFilterBar({
  strategies = [],
  activeCodes = [],
  onCodesChange = () => {},
  confidenceMin = 0,
  onConfidenceChange = () => {},
  colorblindMode = false,
  onColorblindToggle = () => {},
}) {
  const uniqueCodes = useMemo(() => {
    const set = new Set(strategies.map(s => s.code).filter(Boolean));
    return Array.from(set).sort();
  }, [strategies]);

  const handleToggle = (code) => {
    if (activeCodes.includes(code)) {
      onCodesChange(activeCodes.filter(c => c !== code));
    } else {
      onCodesChange([...activeCodes, code]);
    }
  };

  const allSelected = activeCodes.length === uniqueCodes.length && uniqueCodes.length > 0;

  return (
    <div className="strategy-filter-bar" role="region" aria-label="Filtros de estratégias" style={{
      background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.75rem'
    }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
        <strong style={{ fontSize: '0.75rem', letterSpacing: '0.05em', color: '#334155' }}>ESTRATÉGIAS</strong>
        {uniqueCodes.map(code => {
          const meta = STRATEGY_METADATA[code];
          return (
            <label key={code} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.65rem', background: '#fff', border: '1px solid #cbd5e1', padding: '2px 6px', borderRadius: '4px' }}>
              <input
                type="checkbox"
                checked={activeCodes.includes(code)}
                onChange={() => handleToggle(code)}
                aria-label={`Filtrar estratégia ${code}`}
              />
              <span>{code}</span>
              {meta && <span style={{ fontSize: '0.55rem', color: '#64748b' }}>{meta.name}</span>}
            </label>
          );
        })}
        {uniqueCodes.length === 0 && (
          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Nenhuma estratégia detectada</span>
        )}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="button" onClick={() => onCodesChange(uniqueCodes)} disabled={allSelected} style={smallBtn}>Todos</button>
          <button type="button" onClick={() => onCodesChange([])} disabled={activeCodes.length === 0} style={smallBtn}>Nenhum</button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.65rem', color: '#334155', fontWeight: 600 }}>
            Confiança ≥ {confidenceMin}%
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={confidenceMin}
              onChange={(e) => onConfidenceChange(Number(e.target.value))}
              aria-label="Filtro de confiança mínima"
              style={{ marginLeft: '0.5rem' }}
            />
          </label>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.65rem', color: '#334155', fontWeight: 600 }}>Modo daltônico
            <input
              type="checkbox"
              checked={colorblindMode}
              onChange={() => onColorblindToggle(!colorblindMode)}
              aria-label="Ativar modo daltônico"
              style={{ marginLeft: '0.4rem' }}
            />
          </label>
        </div>
      </div>
    </div>
  );
}

const smallBtn = {
  fontSize: '0.6rem',
  padding: '4px 8px',
  border: '1px solid #cbd5e1',
  borderRadius: '4px',
  background: '#fff',
  cursor: 'pointer'
};
