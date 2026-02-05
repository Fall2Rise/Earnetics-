import React, { useCallback, useEffect, useState } from 'react';
import { getOpportunityBacklog, moveOpportunity, Opportunity } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { Kanban, ArrowRight, DollarSign, Clock } from 'lucide-react';

const COLUMNS = [
  { id: 'intake', label: 'Intake', color: 'slate' },
  { id: 'triage', label: 'Triage', color: 'yellow' },
  { id: 'synthesis', label: 'Synthesis', color: 'blue' },
  { id: 'experiment', label: 'Experiment', color: 'purple' },
  { id: 'validated', label: 'Validated', color: 'emerald' },
  { id: 'sent_to_exec', label: 'Sent to Exec', color: 'indigo' },
  { id: 'deployed', label: 'Deployed', color: 'green' },
];

export const OpportunityBacklogKanban: React.FC = () => {
  const [columns, setColumns] = useState<Record<string, Opportunity[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draggedItem, setDraggedItem] = useState<{ opportunity: Opportunity; sourceColumn: string } | null>(null);

  const loadBacklog = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await getOpportunityBacklog(abortSignal);
      if (abortSignal?.aborted) return;
      setColumns(data.columns);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load backlog');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    void loadBacklog(abortController.signal);
    return () => {
      abortController.abort();
    };
  }, [loadBacklog]);

  const handleMove = async (opportunityId: string, newStatus: string) => {
    try {
      await moveOpportunity(opportunityId, newStatus);
      await loadBacklog();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to move opportunity');
    }
  };

  const handleDragStart = (opportunity: Opportunity, sourceColumn: string) => {
    setDraggedItem({ opportunity, sourceColumn });
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  const handleDrop = (targetColumn: string) => {
    if (draggedItem && draggedItem.sourceColumn !== targetColumn) {
      void handleMove(draggedItem.opportunity.opportunity_id, targetColumn);
    }
    setDraggedItem(null);
  };

  return (
    <section className="opportunity-backlog-kanban">
      <header className="panel-header">
        <div>
          <h3>📋 Opportunity Backlog</h3>
          <span className="opportunity-backlog-kanban__subtitle">Kanban board for opportunity workflow</span>
        </div>
        <div className="panel-header__actions">
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadBacklog()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="opportunity-backlog-kanban__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Opportunities flow through stages: Intake → Triage → Synthesis → Experiment → Validated → Sent to Exec → Deployed.
          Drag and drop opportunities between columns to update their status.
        </p>
      </div>

      <div className="kanban-board">
        {COLUMNS.map((column) => {
          const opportunities = columns[column.id] || [];
          return (
            <div
              key={column.id}
              className="kanban-column"
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(column.id)}
            >
              <div className={`kanban-column__header kanban-column__header--${column.color}`}>
                <h4>{column.label}</h4>
                <span className="kanban-column__count">{opportunities.length}</span>
              </div>
              <div className="kanban-column__content">
                {opportunities.map((opp) => (
                  <motion.div
                    key={opp.opportunity_id}
                    className="opportunity-card"
                    draggable
                    onDragStart={() => handleDragStart(opp, column.id)}
                    onDragEnd={handleDragEnd}
                    whileHover={{ scale: 1.02 }}
                    whileDrag={{ opacity: 0.5 }}
                  >
                    <div className="opportunity-card__header">
                      <h5>{opp.niche}</h5>
                      <span className="text-xs text-slate-400">{opp.offer_type}</span>
                    </div>
                    <p className="opportunity-card__hypothesis">{opp.hypothesis.substring(0, 100)}...</p>
                    <div className="opportunity-card__metrics">
                      <div className="flex items-center gap-1">
                        <DollarSign size={14} className="text-emerald-400" />
                        <span className="text-sm">${opp.expected_roi.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock size={14} className="text-blue-400" />
                        <span className="text-sm">{opp.time_to_first_dollar}d</span>
                      </div>
                    </div>
                    <footer className="opportunity-card__footer">
                      <span className="text-xs text-slate-500">
                        {new Date(opp.created_at).toLocaleDateString()}
                      </span>
                    </footer>
                  </motion.div>
                ))}
                {opportunities.length === 0 && (
                  <div className="kanban-column__empty">No opportunities</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
