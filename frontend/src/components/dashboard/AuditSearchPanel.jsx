import React, { useEffect, useMemo, useState } from 'react';
import useAppStore from '../../stores/useAppStore';
import useAnnotationStore from '../../stores/useAnnotationStore';

const statusesOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'modified', label: 'Modified' },
  { value: 'created', label: 'Created' },
];

const actionOptions = [
  { value: 'accept', label: 'Accept' },
  { value: 'reject', label: 'Reject' },
  { value: 'modify', label: 'Modify' },
  { value: 'create', label: 'Create' },
];

export default function AuditSearchPanel() {
  const { config } = useAppStore();
  const enable = config?.enableAuditSearch;
  const {
    sessionId,
    searchFilters, setSearchFilters, resetSearch,
    runSearch, searchResults, searchLoading,
    audit, fetchAudit,
  } = useAnnotationStore();

  const [strategyCode, setStrategyCode] = useState('');
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    // keep store filters in sync with local code input
    const codes = strategyCode ? [strategyCode] : [];
    setSearchFilters({ codes });
  }, [strategyCode, setSearchFilters]);

  if (!enable) return null;

  const toggleRow = (id) => setExpanded((e) => ({ ...e, [id]: !e[id] }));

  return (
    <section aria-labelledby="audit-search-title" className="audit-search" style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: 8 }}>
      <h2 id="audit-search-title">Audit Search</h2>
      <div role="form" aria-label="Audit search form" className="filters" style={{ display: 'grid', gap: '0.5rem', gridTemplateColumns: 'repeat(auto-fit, minmax(200px,1fr))' }}>
        <div>
          <label htmlFor="status-filter">Status</label>
          <select id="status-filter" aria-label="Filter by status" multiple value={searchFilters.statuses} onChange={(e) => {
            const opts = Array.from(e.target.selectedOptions).map(o => o.value);
            setSearchFilters({ statuses: opts });
          }}>
            {statusesOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="code-filter">Strategy code</label>
          <input id="code-filter" type="text" aria-label="Filter by strategy code" value={strategyCode} onChange={(e) => setStrategyCode(e.target.value.trim())} />
        </div>
        <div>
          <label htmlFor="actions-filter">Actions</label>
          <select id="actions-filter" aria-label="Filter audit actions" multiple value={searchFilters.actions} onChange={(e) => {
            const opts = Array.from(e.target.selectedOptions).map(o => o.value);
            setSearchFilters({ actions: opts });
          }}>
            {actionOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end' }}>
          <button onClick={runSearch} aria-label="Run search" disabled={searchLoading}>Search</button>
          <button onClick={resetSearch} aria-label="Reset filters">Reset</button>
        </div>
      </div>

      <div role="status" aria-live="polite" style={{ marginTop: '0.5rem' }}>
        {searchLoading ? 'Loading…' : ''}
      </div>

      <div className="results" aria-label="Search results" style={{ marginTop: '1rem' }}>
        {(!searchResults || searchResults.length === 0) && !searchLoading ? (
          <p>No results</p>
        ) : (
          <table className="audit-results" role="table" aria-label="Annotations list" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Code</th>
                <th scope="col">Status</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map((a, idx) => (
                <React.Fragment key={a.id}>
                  <tr tabIndex={0} onKeyDown={(e) => { if (e.key === 'Enter') toggleRow(a.id); }} style={{ outline: 'none' }}>
                    <td><button onClick={() => toggleRow(a.id)} aria-expanded={!!expanded[a.id]} aria-controls={`aud-${a.id}`}>{expanded[a.id] ? '▾' : '▸'}</button> {a.id.slice(0,8)}</td>
                    <td>{a.strategy_code}</td>
                    <td>{a.status}</td>
                    <td>
                      <button onClick={() => fetchAudit(a.id)} aria-label={`Load audit for ${a.id}`}>Load audit</button>
                    </td>
                  </tr>
                  {expanded[a.id] && (
                    <tr id={`aud-${a.id}`}>
                      <td colSpan={4}>
                        {(audit[a.id] || []).length === 0 ? (
                          <em>No audit entries</em>
                        ) : (
                          <ul>
                            {(audit[a.id] || []).map((ev, i) => (
                              <li key={i}>{ev.timestamp} — {ev.action} ({ev.from_status} → {ev.to_status})</li>
                            ))}
                          </ul>
                        )}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
