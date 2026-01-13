import React, { useCallback, useEffect, useState } from 'react';
import { listLeads, LeadRecord } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { Users, Search, Filter, Shield, Mail, Phone, Building } from 'lucide-react';

export const LeadVaultBrowser: React.FC = () => {
  const [leads, setLeads] = useState<LeadRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [entityType, setEntityType] = useState<string>('');
  const [tags, setTags] = useState('');

  const loadLeads = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listLeads(
        entityType || undefined,
        tags || undefined,
        100,
        abortSignal
      );
      if (abortSignal?.aborted) return;
      setLeads(data.leads);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load leads');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [entityType, tags]);

  useEffect(() => {
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => {
      void loadLeads(abortController.signal);
    }, 300);
    return () => {
      clearTimeout(timeoutId);
      abortController.abort();
    };
  }, [loadLeads]);

  return (
    <section className="lead-vault-browser">
      <header className="panel-header">
        <div>
          <h3>🔒 Lead Vault</h3>
          <span className="lead-vault-browser__subtitle">PII storage with governance, audit logs, and suppression</span>
        </div>
        <div className="panel-header__actions">
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadLeads()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="lead-vault-browser__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>🔒 Access Gated:</strong> Lead Vault contains PII and is subject to strict access control.
          All access is audited. Suppressed leads are automatically excluded.
        </p>
      </div>

      <div className="lead-vault-filters">
        <div className="category-filter">
          <Filter size={16} className="text-slate-400" />
          <select value={entityType} onChange={(e) => setEntityType(e.target.value)}>
            <option value="">All Entity Types</option>
            <option value="person">Person</option>
            <option value="business">Business</option>
          </select>
        </div>
        <div className="search-input">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            placeholder="Filter by tags..."
            value={tags}
            onChange={(e) => setTags(e.target.value)}
          />
        </div>
      </div>

      <div className="lead-vault-list">
        {loading && <p className="panel-loading">Loading leads...</p>}
        {!loading && leads.length === 0 && (
          <p className="panel-empty">No leads found for the current filters.</p>
        )}

        {leads.map((lead) => (
          <motion.div
            key={lead.lead_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lead-card"
          >
            <div className="lead-card__header">
              <div className="flex items-center gap-2">
                {lead.entity_type === 'business' ? (
                  <Building size={20} className="text-indigo-400" />
                ) : (
                  <Users size={20} className="text-indigo-400" />
                )}
                <div>
                  <h4>{lead.name}</h4>
                  {lead.business_name && (
                    <span className="text-xs text-slate-400">{lead.business_name}</span>
                  )}
                  {lead.role && (
                    <span className="text-xs text-slate-400"> • {lead.role}</span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {lead.compliance.do_not_contact ? (
                  <span className="status-pill status-pill--warning">Suppressed</span>
                ) : (
                  <span className="status-pill status-pill--success">Active</span>
                )}
              </div>
            </div>
            <div className="lead-card__contacts">
              {lead.emails && lead.emails.length > 0 && (
                <div className="flex items-center gap-2">
                  <Mail size={14} className="text-slate-400" />
                  {lead.emails.map((email, idx) => (
                    <span key={idx} className="text-sm text-slate-300">
                      {email.value}
                      {email.verified && <CheckCircle size={12} className="inline ml-1 text-emerald-400" />}
                    </span>
                  ))}
                </div>
              )}
              {lead.phones && lead.phones.length > 0 && (
                <div className="flex items-center gap-2">
                  <Phone size={14} className="text-slate-400" />
                  {lead.phones.map((phone, idx) => (
                    <span key={idx} className="text-sm text-slate-300">
                      {phone.value}
                      {phone.verified && <CheckCircle size={12} className="inline ml-1 text-emerald-400" />}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="lead-card__compliance">
              <div className="flex items-center gap-2">
                <Shield size={14} className="text-slate-400" />
                <span className="text-xs text-slate-400">
                  Legal Basis: {lead.compliance.legal_basis} • Channels: {lead.compliance.allowed_channels.join(', ')}
                </span>
              </div>
            </div>
            {lead.tags && lead.tags.length > 0 && (
              <div className="lead-card__tags">
                {lead.tags.map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            )}
            {lead.scores && Object.keys(lead.scores).length > 0 && (
              <div className="lead-card__scores">
                {Object.entries(lead.scores).map(([key, value]) => (
                  <span key={key} className="text-xs text-slate-400">
                    {key}: {Math.round(value * 100)}%
                  </span>
                ))}
              </div>
            )}
            <footer className="lead-card__footer">
              <span className="text-xs text-slate-500">
                {new Date(lead.created_at).toLocaleString()}
              </span>
            </footer>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
