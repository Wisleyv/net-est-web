import React, { useState } from 'react';

/**
 * SentenceAlignmentPlaceholder.jsx
 * Minimal UI placeholder to visualize sentence-level alignment output during early M1 integration.
 * - Shows a sample alignment list
 * - Provides a "Simulate alignment" button to toggle demo data
 *
 * This is intentionally simple so it can be extended later to consume real API data.
 */

export default function SentenceAlignmentPlaceholder() {
  const [loaded, setLoaded] = useState(false);

  const demoData = [
    {
      id: 's-0-0',
      text: 'Primeira frase de exemplo (fonte).',
      alignment: [{ target_index: 0, similarity: 0.92 }],
      micro_spans: [],
    },
    {
      id: 's-0-1',
      text: 'Segunda frase de exemplo (fonte).',
      alignment: [{ target_index: 1, similarity: 0.78 }],
      micro_spans: [],
    },
  ];

  return (
    <div style={{ marginTop: '1.5rem', padding: '1rem', borderRadius: 8, background: '#f7fafc', border: '1px solid #e2e8f0' }}>
      <h3 style={{ margin: 0, fontSize: '1rem', color: '#2d3748' }}>🔗 Sentence Alignment (Placeholder)</h3>
      <p style={{ margin: '0.5rem 0 1rem 0', color: '#4a5568', fontSize: '0.875rem' }}>
        This is a placeholder component for visualizing sentence-level alignments. Click "Simulate alignment" to show demo data.
      </p>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          onClick={() => setLoaded(!loaded)}
          style={{
            padding: '0.5rem 0.75rem',
            backgroundColor: '#3182ce',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}
        >
          {loaded ? 'Hide demo alignment' : 'Simulate alignment'}
        </button>
      </div>

      {loaded && (
        <div style={{ marginTop: '1rem' }}>
          {demoData.map((s) => (
            <div key={s.id} style={{ padding: '0.5rem', borderRadius: 6, background: 'white', marginBottom: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong style={{ color: '#2d3748' }}>{s.id}</strong>
                  <div style={{ color: '#4a5568', fontSize: '0.9rem' }}>{s.text}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.85rem', color: '#2f855a' }}>
                    Aligned to: {s.alignment.map(a => a.target_index).join(', ')}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#718096' }}>
                    Similarity: {s.alignment.map(a => a.similarity).join(', ')}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}