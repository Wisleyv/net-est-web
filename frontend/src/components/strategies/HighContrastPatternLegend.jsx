import React from 'react';
import { STRATEGY_METADATA } from '../../services/strategyColorMapping.js';

export default function HighContrastPatternLegend({ unifiedMap = {}, show = true }) {
  if (!show) return null;
  const entries = Object.values(unifiedMap).filter(e => e.pattern);
  if (entries.length === 0) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 mt-4" aria-label="Legenda de padrões para modo daltônico">
      <h6 className="font-medium text-sm text-gray-800 mb-2">Padrões (Modo Daltônico)</h6>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
        {entries.map(entry => {
          const meta = STRATEGY_METADATA[entry.code];
          return (
            <div key={entry.code} className="flex items-center gap-2 text-xs bg-gray-50 p-2 rounded border" style={{ borderColor: entry.baseColor }}>
              <span
                className="inline-block w-8 h-6 rounded border"
                style={{
                  background: entry.pattern ? 'transparent' : entry.baseColor,
                  position: 'relative',
                  borderColor: entry.baseColor,
                  overflow: 'hidden'
                }}
                aria-hidden="true"
              >
                {/* pattern preview using same CSS layering idea */}
                <span style={{
                  position: 'absolute',
                  inset: 0,
                  background: entry.pattern ? '' : entry.baseColor
                }} />
              </span>
              <div className="flex-1">
                <div className="font-semibold">{entry.code}</div>
                <div className="text-gray-600 truncate" title={meta?.name}>{meta?.name}</div>
                <div className="text-gray-500">{entry.pattern}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
