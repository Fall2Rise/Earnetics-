import React, { useCallback, useEffect, useState } from 'react';
import { listExperiments, Experiment } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { FlaskConical, Search, Filter, CheckCircle, XCircle, Clock } from 'lucide-react';

export const ExperimentsLab: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const loadExperiments = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listExperiments(statusFilter || undefined, 20, abortSignal);
      if (abortSignal?.aborted) return;
      setExperiments(data.experiments);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load experiments');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [statusFilter]);

  useEffect(() => {
    const abortController = new AbortController();
    void loadExperiments(abortController.signal);
    return () => {
      abortController.abort();
    };
  }, [loadExperiments]);

  const getStatusIcon = (status: string) => {
    if (status === 'validated' || status === 'completed') return <CheckCircle size={16} className="text-emerald-400" />;
    if (status === 'running') return <Clock size={16} className="text-yellow-400" />;
    return <XCircle size={16} className="text-red-400" />;
  };

  return (
    <section className="experiments-lab">
      <header className="panel-header">
        <div>
          <h3>🧪 Experiments Lab</h3>
          <span className="experiments-lab__subtitle">Micro-tests and experiment results</span>
        </div>
        <div className="panel-header__actions">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white text-sm"
          >
            <option value="">All Status</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="validated">Validated</option>
          </select>
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadExperiments()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="experiments-lab__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Experiments are micro-tests run by Intelligence Department to validate hypotheses.
          Results are recorded and used to update Truth Library playbooks.
        </p>
      </div>

      <div className="experiments-list">
        {loading && <p className="panel-loading">Loading experiments...</p>}
        {!loading && experiments.length === 0 && (
          <p className="panel-empty">No experiments found for the current filters.</p>
        )}

        {experiments.map((experiment) => (
          <motion.div
            key={experiment.asset_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="experiment-card"
          >
            <div className="experiment-card__header">
              <div className="flex items-center gap-2">
                <FlaskConical size={20} className="text-indigo-400" />
                <h4>{experiment.title}</h4>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(experiment.status)}
                <span className={`status-pill status-pill--${experiment.status === 'validated' ? 'success' : experiment.status === 'running' ? 'warning' : 'error'}`}>
                  {experiment.status}
                </span>
              </div>
            </div>
            {experiment.content && (
              <div className="experiment-card__content">
                <p><strong>Hypothesis:</strong> {experiment.content.hypothesis}</p>
                {experiment.content.results && (
                  <div className="experiment-card__results">
                    <strong>Results:</strong>
                    <pre className="text-xs">{JSON.stringify(experiment.content.results, null, 2)}</pre>
                  </div>
                )}
                {experiment.content.conclusion && (
                  <p><strong>Conclusion:</strong> {experiment.content.conclusion}</p>
                )}
                {experiment.content.next_steps && experiment.content.next_steps.length > 0 && (
                  <div className="experiment-card__next-steps">
                    <strong>Next Steps:</strong>
                    <ul>
                      {experiment.content.next_steps.map((step: string, idx: number) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            <footer className="experiment-card__footer">
              <span className="text-xs text-slate-500">
                {new Date(experiment.created_at).toLocaleString()}
              </span>
            </footer>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
