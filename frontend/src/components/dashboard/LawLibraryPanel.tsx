import React, { useCallback, useEffect, useState } from 'react';
import { fetchLawEntries, getLawEntry, LawLibraryEntry } from '../../api/headOfficeApi';

export const LawLibraryPanel: React.FC = () => {
  const [entries, setEntries] = useState<LawLibraryEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<LawLibraryEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const loadEntries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchLawEntries(categoryFilter === 'all' ? undefined : categoryFilter);
      setEntries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load law library');
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  useEffect(() => {
    void loadEntries();
  }, [loadEntries]);

  const handleSelectEntry = async (id: string) => {
    try {
      const entry = await getLawEntry(id);
      setSelectedEntry(entry);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load law entry');
    }
  };

  if (loading && entries.length === 0) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Law Library</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  const categories = Array.from(new Set(entries.map(e => e.category)));

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Law Library</h2>
        <div className="panel-controls">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="select-input"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <button onClick={loadEntries} className="btn-secondary" disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content panel-content--split">
        <div className="entry-list">
          <h3>Entries ({entries.length})</h3>
          {entries.length === 0 ? (
            <p className="empty-state">No law entries found</p>
          ) : (
            <ul className="entry-items">
              {entries.map((entry) => (
                <li
                  key={entry.id}
                  className={`entry-item ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
                  onClick={() => handleSelectEntry(entry.id)}
                >
                  <div className="entry-header">
                    <strong>{entry.title}</strong>
                    <span className={`risk-badge risk-${entry.risk_level}`}>
                      {entry.risk_level}
                    </span>
                  </div>
                  <div className="entry-meta">
                    <span>Category: {entry.category}</span>
                    <span>Jurisdiction: {entry.jurisdiction}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {selectedEntry && (
          <div className="entry-details">
            <h3>{selectedEntry.title}</h3>
            <div className="detail-section">
              <h4>Summary</h4>
              <p>{selectedEntry.plain_english_summary}</p>
            </div>
            <div className="detail-section">
              <h4>Compliance Checklist</h4>
              <ul>
                {selectedEntry.compliance_checklist.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
            {selectedEntry.applicability_tags.length > 0 && (
              <div className="detail-section">
                <h4>Tags</h4>
                <div className="tags">
                  {selectedEntry.applicability_tags.map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}
            {selectedEntry.primary_sources_links.length > 0 && (
              <div className="detail-section">
                <h4>Primary Sources</h4>
                <ul>
                  {selectedEntry.primary_sources_links.map((link, idx) => (
                    <li key={idx}>
                      <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="detail-meta">
              <p>Risk Level: <strong>{selectedEntry.risk_level}</strong></p>
              <p>Jurisdiction: {selectedEntry.jurisdiction}</p>
              <p>Category: {selectedEntry.category}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
