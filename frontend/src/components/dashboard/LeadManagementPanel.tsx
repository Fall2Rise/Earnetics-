import React, { useState, useEffect } from 'react';
import { leadManagementApi, ScrapedLead } from '../../api/leadManagementApi';

export const LeadManagementPanel: React.FC = () => {
  const [leads, setLeads] = useState<ScrapedLead[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'qualified' | 'unqualified' | 'added'>('all');

  useEffect(() => {
    loadLeads();
    loadStats();
    const interval = setInterval(() => {
      loadLeads();
      loadStats();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 500 };
      if (filter === 'qualified') params.qualified_only = true;
      if (filter === 'added') params.added_to_list = true;
      const data = await leadManagementApi.getScrapedLeads(params);
      setLeads(data.leads);
    } catch (error) {
      console.error('Failed to load leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await leadManagementApi.getScrapedLeadsStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleQualify = async (leadId: number, qualified: boolean) => {
    try {
      await leadManagementApi.qualifyLead(leadId, qualified);
      loadLeads();
      loadStats();
    } catch (error) {
      console.error('Failed to qualify lead:', error);
    }
  };

  const handleAddToList = async (leadId: number) => {
    try {
      await leadManagementApi.addLeadToList(leadId);
      loadLeads();
      loadStats();
    } catch (error) {
      console.error('Failed to add lead to list:', error);
    }
  };

  return (
    <div className="command-panel">
      <div className="panel-header">
        <h2>🔍 Scraped Leads</h2>
        <div className="panel-controls">
          <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
            <option value="all">All Leads</option>
            <option value="qualified">Qualified Only</option>
            <option value="unqualified">Unqualified Only</option>
            <option value="added">Added to List</option>
          </select>
        </div>
      </div>

      {stats && (
        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
          <div className="stat-card">
            <div className="stat-value">{stats.total_leads}</div>
            <div className="stat-label">Total Leads</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.qualified_leads}</div>
            <div className="stat-label">Qualified</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.added_to_list}</div>
            <div className="stat-label">Added to List</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{Object.keys(stats.by_domain || {}).length}</div>
            <div className="stat-label">Source Domains</div>
          </div>
        </div>
      )}

      <div className="table-container" style={{ maxHeight: '600px', overflowY: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Name</th>
              <th>Source</th>
              <th>Qualified</th>
              <th>Added</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>Loading leads...</td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>No leads found</td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id}>
                  <td>{lead.email}</td>
                  <td>{lead.name || '-'}</td>
                  <td>
                    <span className="badge">{lead.source_domain}</span>
                  </td>
                  <td>
                    {lead.qualified ? (
                      <span className="badge badge-success">✓ Qualified</span>
                    ) : (
                      <span className="badge badge-warning">Unqualified</span>
                    )}
                  </td>
                  <td>
                    {lead.added_to_list ? (
                      <span className="badge badge-success">✓ Added</span>
                    ) : (
                      <span className="badge">Not Added</span>
                    )}
                  </td>
                  <td>
                    {!lead.qualified && (
                      <button
                        className="btn btn-sm"
                        onClick={() => handleQualify(lead.id, true)}
                        style={{ marginRight: '0.5rem' }}
                      >
                        Qualify
                      </button>
                    )}
                    {lead.qualified && !lead.added_to_list && (
                      <button 
                        className="btn btn-sm btn-primary"
                        onClick={() => handleAddToList(lead.id)}
                      >
                        Add to List
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
