import React, { useState, useEffect } from 'react';
import { leadManagementApi, Subscriber } from '../../api/leadManagementApi';

export const SubscribersPanel: React.FC = () => {
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [categories, setCategories] = useState<Record<string, Subscriber[]>>({});
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  useEffect(() => {
    loadSubscribers();
    loadStats();
    const interval = setInterval(() => {
      loadSubscribers();
      loadStats();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadSubscribers = async () => {
    try {
      setLoading(true);
      const data = await leadManagementApi.getSubscribers({ limit: 1000 });
      setSubscribers(data.subscribers);
      setCategories(data.categories || {});
    } catch (error) {
      console.error('Failed to load subscribers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await leadManagementApi.getSubscribersStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const displaySubscribers = selectedCategory && categories[selectedCategory]
    ? categories[selectedCategory]
    : subscribers;

  return (
    <div className="command-panel">
      <div className="panel-header">
        <h2>📬 Subscribers by Category</h2>
        <div className="panel-controls">
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value || null)}
            style={{ marginRight: '1rem' }}
          >
            <option value="">All Categories</option>
            {Object.keys(categories).map((cat) => (
              <option key={cat} value={cat}>
                {cat} ({categories[cat].length})
              </option>
            ))}
          </select>
          <button className="btn btn-sm" onClick={loadSubscribers}>Refresh</button>
        </div>
      </div>

      {stats && (
        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
          <div className="stat-card">
            <div className="stat-value">{stats.total_subscribers}</div>
            <div className="stat-label">Total Subscribers</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.active_count}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{Object.keys(categories).length}</div>
            <div className="stat-label">Categories</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{Object.keys(stats.by_source || {}).length}</div>
            <div className="stat-label">Sources</div>
          </div>
        </div>
      )}

      {Object.keys(categories).length > 0 && (
        <div className="category-tabs" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          {Object.entries(categories).map(([category, subs]) => (
            <button
              key={category}
              className={`badge ${selectedCategory === category ? 'badge-primary' : ''}`}
              onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
              style={{ cursor: 'pointer', padding: '0.5rem 1rem' }}
            >
              {category} ({subs.length})
            </button>
          ))}
        </div>
      )}

      <div className="table-container" style={{ maxHeight: '600px', overflowY: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Name</th>
              <th>Category</th>
              <th>Source</th>
              <th>Status</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>Loading subscribers...</td>
              </tr>
            ) : displaySubscribers.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>No subscribers found</td>
              </tr>
            ) : (
              displaySubscribers.map((sub) => {
                const category = Object.keys(categories).find(cat => categories[cat].some(s => s.id === sub.id)) || 'General';
                return (
                  <tr key={sub.id}>
                    <td>{sub.email}</td>
                    <td>{sub.first_name || '-'}</td>
                    <td>
                      <span className="badge">{category}</span>
                    </td>
                    <td>{sub.source || '-'}</td>
                    <td>
                      <span className={`badge ${sub.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                        {sub.status}
                      </span>
                    </td>
                    <td>
                      {sub.tags && sub.tags.length > 0 ? (
                        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                          {sub.tags.map((tag, idx) => (
                            <span key={idx} className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                              {tag}
                            </span>
                          ))}
                        </div>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
