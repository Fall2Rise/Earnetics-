import React, { useCallback, useEffect, useState } from 'react';
import { getExecutiveInbox, decideOnPacket, DecisionPacket } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { Inbox, CheckCircle, XCircle, FlaskConical, AlertCircle, Send } from 'lucide-react';

export const ExecutiveInbox: React.FC = () => {
  const [packets, setPackets] = useState<DecisionPacket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, total: 0 });

  const loadInbox = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await getExecutiveInbox(statusFilter || undefined, 20, abortSignal);
      if (abortSignal?.aborted) return;
      setPackets(data.packets);
      setStats({
        pending: data.pending,
        approved: data.approved,
        rejected: data.rejected,
        total: data.total
      });
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load inbox');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [statusFilter]);

  useEffect(() => {
    const abortController = new AbortController();
    void loadInbox(abortController.signal);
    return () => {
      abortController.abort();
    };
  }, [loadInbox]);

  const handleDecide = async (packetId: string, decision: 'deploy' | 'experiment' | 'reject' | 'needs_evidence') => {
    try {
      await decideOnPacket(packetId, decision);
      await loadInbox();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process decision');
    }
  };

  return (
    <section className="executive-inbox">
      <header className="panel-header">
        <div>
          <h3>📬 Executive Inbox</h3>
          <span className="executive-inbox__subtitle">Decision Packets awaiting executive review</span>
        </div>
        <div className="panel-header__actions">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white text-sm"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadInbox()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="executive-inbox__stats">
        <div className="stat-card">
          <Inbox size={20} className="text-indigo-400" />
          <div>
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Packets</div>
          </div>
        </div>
        <div className="stat-card">
          <AlertCircle size={20} className="text-yellow-400" />
          <div>
            <div className="stat-value">{stats.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
        </div>
        <div className="stat-card">
          <CheckCircle size={20} className="text-emerald-400" />
          <div>
            <div className="stat-value">{stats.approved}</div>
            <div className="stat-label">Approved</div>
          </div>
        </div>
        <div className="stat-card">
          <XCircle size={20} className="text-red-400" />
          <div>
            <div className="stat-value">{stats.rejected}</div>
            <div className="stat-label">Rejected</div>
          </div>
        </div>
      </div>

      <div className="executive-inbox__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Decision Packets are 1-page structured briefs from Intelligence Department
          requesting executive approval for revenue opportunities. Review and decide: Deploy, Experiment, Reject, or Request More Evidence.
        </p>
      </div>

      <div className="packet-list">
        {loading && <p className="panel-loading">Loading packets...</p>}
        {!loading && packets.length === 0 && (
          <p className="panel-empty">No decision packets in inbox.</p>
        )}

        {packets.map((packet) => (
          <motion.div
            key={packet.packet_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="packet-card"
          >
            <div className="packet-card__header">
              <div>
                <h4>{packet.opportunity.niche} - {packet.opportunity.offer_type}</h4>
                <span className="text-xs text-slate-400">Packet ID: {packet.packet_id}</span>
              </div>
              <span className={`status-pill status-pill--${packet.status === 'pending' ? 'warning' : packet.status === 'approved' ? 'success' : 'error'}`}>
                {packet.status}
              </span>
            </div>
            <div className="packet-card__content">
              <p><strong>Hypothesis:</strong> {packet.opportunity.hypothesis}</p>
              <div className="packet-card__metrics">
                <span>Expected ROI: ${packet.opportunity.expected_roi.toLocaleString()}</span>
                <span>Time to First Dollar: {packet.opportunity.time_to_first_dollar} days</span>
              </div>
              {packet.why_now && packet.why_now.signals && packet.why_now.signals.length > 0 && (
                <div className="packet-card__signals">
                  <strong>Signals:</strong> {packet.why_now.signals.length} signals identified
                </div>
              )}
            </div>
            {packet.status === 'pending' && (
              <div className="packet-card__actions">
                <button
                  className="small-button primary-button"
                  onClick={() => void handleDecide(packet.packet_id, 'deploy')}
                >
                  <Send size={14} /> Deploy
                </button>
                <button
                  className="small-button refresh-button"
                  onClick={() => void handleDecide(packet.packet_id, 'experiment')}
                >
                  <FlaskConical size={14} /> Experiment
                </button>
                <button
                  className="small-button refresh-button"
                  onClick={() => void handleDecide(packet.packet_id, 'needs_evidence')}
                >
                  <AlertCircle size={14} /> Needs Evidence
                </button>
                <button
                  className="small-button refresh-button"
                  onClick={() => void handleDecide(packet.packet_id, 'reject')}
                >
                  <XCircle size={14} /> Reject
                </button>
              </div>
            )}
            <footer className="packet-card__footer">
              <span className="text-xs text-slate-500">
                {new Date(packet.generated_at).toLocaleString()}
              </span>
            </footer>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
