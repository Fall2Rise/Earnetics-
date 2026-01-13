import React, { useCallback, useEffect, useState } from 'react';
import { getSignals, Signal } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { TrendingUp, Filter, AlertCircle, CheckCircle } from 'lucide-react';

export const SignalDashboard: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState(1);

  const loadSignals = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await getSignals(20, priorityFilter, abortSignal);
      if (abortSignal?.aborted) return;
      setSignals(data.signals);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load signals');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [priorityFilter]);

  useEffect(() => {
    const abortController = new AbortController();
    void loadSignals(abortController.signal);
    return () => {
      abortController.abort();
    };
  }, [loadSignals]);

  const getPriorityColor = (priority: number) => {
    if (priority >= 5) return 'text-red-400 border-red-500/30 bg-red-900/20';
    if (priority >= 4) return 'text-orange-400 border-orange-500/30 bg-orange-900/20';
    if (priority >= 3) return 'text-yellow-400 border-yellow-500/30 bg-yellow-900/20';
    return 'text-blue-400 border-blue-500/30 bg-blue-900/20';
  };

  return (
    <section className="signal-dashboard">
      <header className="panel-header">
        <div>
          <h3>📡 Signal Dashboard</h3>
          <span className="signal-dashboard__subtitle">Ranked signals from Knowledge Radio and external sources</span>
        </div>
        <div className="panel-header__actions">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-slate-400" />
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(Number(e.target.value))}
              className="px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white text-sm"
            >
              <option value={1}>All Priorities</option>
              <option value={3}>Priority 3+</option>
              <option value={4}>Priority 4+</option>
              <option value={5}>Priority 5</option>
            </select>
          </div>
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadSignals()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="signal-dashboard__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Signals are automatically collected from Knowledge Radio feeds (GDELT, RSS, GitHub releases)
          and ranked by priority. High-priority signals indicate immediate revenue opportunities or critical market changes.
        </p>
      </div>

      <div className="signal-list">
        {loading && <p className="panel-loading">Loading signals...</p>}
        {!loading && signals.length === 0 && (
          <p className="panel-empty">No signals found for the current filters.</p>
        )}

        {signals.map((signal) => (
          <motion.div
            key={signal.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`signal-card ${getPriorityColor(signal.priority)}`}
          >
            <div className="signal-card__header">
              <div className="flex items-center gap-2">
                <TrendingUp size={20} className="text-indigo-400" />
                <h4>{signal.headline}</h4>
              </div>
              <div className="flex items-center gap-2">
                <span className={`status-pill status-pill--${signal.priority >= 5 ? 'critical' : signal.priority >= 4 ? 'high' : 'medium'}`}>
                  P{signal.priority}
                </span>
                <span className="text-xs text-slate-400">{signal.topic}</span>
              </div>
            </div>
            <p className="signal-card__why">{signal.why_it_matters}</p>
            {signal.actionable_angle && (
              <div className="signal-card__actionable">
                <strong>Actionable:</strong> {signal.actionable_angle}
              </div>
            )}
            {signal.citations && signal.citations.length > 0 && (
              <div className="signal-card__citations">
                <strong>Sources:</strong>
                {signal.citations.map((cite, idx) => (
                  <a
                    key={idx}
                    href={cite.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-indigo-400 hover:text-indigo-300"
                  >
                    {cite.source_id}
                  </a>
                ))}
              </div>
            )}
            <footer className="signal-card__footer">
              <span className="text-xs text-slate-500">
                {new Date(signal.created_at).toLocaleString()}
              </span>
            </footer>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
