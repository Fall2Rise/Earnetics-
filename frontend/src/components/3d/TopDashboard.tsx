import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { fetchOperationsMetrics, OperationsMetricsResponse } from '../../api/operationsApi';
import { fetchFinancialMetrics, FinancialMetrics } from '../../api/financialApi';
import { DetailModal } from '../dashboard/DetailModal';

export const TopDashboard: React.FC = () => {
  const [opsMetrics, setOpsMetrics] = useState<OperationsMetricsResponse | null>(null);
  const [financialMetrics, setFinancialMetrics] = useState<FinancialMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [detailKey, setDetailKey] = useState<'activeTrigs' | 'outputs' | 'errors' | null>(null);

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const loadMetrics = async () => {
      try {
        const [ops, financial] = await Promise.all([
          fetchOperationsMetrics(controller.signal),
          fetchFinancialMetrics(controller.signal),
        ]);
        if (!isMounted) return;
        setOpsMetrics(ops);
        setFinancialMetrics(financial);
        setError(null);
      } catch (err) {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load metrics');
      }
    };

    void loadMetrics();
    const intervalId = setInterval(loadMetrics, 15000);

    return () => {
      isMounted = false;
      controller.abort();
      clearInterval(intervalId);
    };
  }, []);

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

  const metrics = useMemo(() => {
    const revenue = financialMetrics?.total_revenue ?? 0;
    const activeTrades = opsMetrics?.queue?.pending ?? 0;
    const outputs = opsMetrics?.activity?.length ?? 0;
    const activityErrors = opsMetrics?.activity?.filter((entry) => entry.status === 'error').length ?? 0;
    const financialErrors = financialMetrics?.failed_payouts_count ?? 0;
    const errors = activityErrors + financialErrors;

    const payoutTotal = (financialMetrics?.total_paid_out ?? 0) + (financialMetrics?.total_reinvested ?? 0);
    const revenueProgress = revenue > 0 ? Math.min(1, payoutTotal / revenue) : 0;

    return {
      revenue: formatCurrency(revenue),
      activeTrades,
      apps: outputs,
      errors,
      reportReturning: financialMetrics?.pending_payouts_count ?? 0,
      revenueProgress,
    };
  }, [financialMetrics, opsMetrics]);

  return (
    <div className="absolute top-0 left-0 right-0 z-50 bg-gradient-to-b from-slate-950/95 to-slate-950/75 backdrop-blur border-b border-cyan-500/20">
      <div className="container mx-auto px-6 py-3">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-3 items-stretch">
          <div className="col-span-2 flex items-center gap-4 bg-slate-900/70 border border-cyan-500/25 rounded-xl px-4 py-3 shadow-[0_0_30px_rgba(0,214,255,0.12)]">
            <div>
              <div className="text-xs text-cyan-200/70 uppercase tracking-widest">Revenue</div>
              <div className="text-2xl font-bold text-emerald-300 font-mono">{metrics.revenue}</div>
              <div className="text-xs text-cyan-200/50 uppercase tracking-wider">Today</div>
            </div>
            <div className="flex-1">
              <div className="h-2 rounded bg-white/5 overflow-hidden">
                <div
                  className="h-full bg-emerald-400/60"
                  style={{ width: `${Math.round(metrics.revenueProgress * 100)}%` }}
                />
              </div>
            </div>
          </div>

          <PanelMetric
            label="Active Trigs"
            value={metrics.activeTrades}
            color="text-cyan-300"
            onClick={() => setDetailKey('activeTrigs')}
          />
          <PanelMetric label="Outputs" value={metrics.apps} color="text-blue-300" onClick={() => setDetailKey('outputs')} />
          <PanelMetric label="Errors" value={metrics.errors} color="text-amber-300" onClick={() => setDetailKey('errors')} />
        </div>
        {error && <div className="mt-2 text-[10px] text-amber-300/80">{error}</div>}
      </div>
      <DetailModal
        isOpen={detailKey !== null}
        onClose={() => setDetailKey(null)}
        title={
          detailKey === 'activeTrigs'
            ? 'Active Triggers'
            : detailKey === 'outputs'
            ? 'Outputs'
            : 'Errors'
        }
        subtitle="Click-through detail from live metrics"
      >
        {detailKey === 'activeTrigs' && (
          <div className="space-y-4 text-sm text-slate-200">
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div>
                <span className="text-slate-400">Pending</span>
                <div className="text-white">{opsMetrics?.queue?.pending ?? 0}</div>
              </div>
              <div>
                <span className="text-slate-400">At risk</span>
                <div className="text-white">{opsMetrics?.queue?.at_risk ?? 0}</div>
              </div>
              <div>
                <span className="text-slate-400">Overdue</span>
                <div className="text-white">{opsMetrics?.queue?.overdue ?? 0}</div>
              </div>
            </div>
            <div>
              <h4 className="text-sm text-cyan-300 font-semibold mb-2">Delegated directives</h4>
              {(opsMetrics?.requests ?? []).length === 0 && <div className="text-xs text-slate-400">No directives available.</div>}
              <div className="space-y-2">
                {(opsMetrics?.requests ?? []).slice(0, 12).map((req) => (
                  <div key={`${req.id ?? req.timestamp}`} className="p-3 bg-slate-800/60 border border-cyan-500/20 rounded">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-white">{req.title ?? 'Directive'}</div>
                      <div className="text-xs text-cyan-200/70">{req.status ?? 'pending'}</div>
                    </div>
                    <div className="text-xs text-slate-300 mt-1">{req.description ?? 'No description provided.'}</div>
                    {req.payload && (
                      <pre className="text-[10px] mt-2 bg-black/40 border border-cyan-500/20 rounded p-2 overflow-x-auto">
                        {JSON.stringify(req.payload, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        {detailKey === 'outputs' && (
          <div className="space-y-3 text-sm text-slate-200">
            <h4 className="text-sm text-cyan-300 font-semibold">Recent automation outputs</h4>
            {(opsMetrics?.activity ?? []).length === 0 && <div className="text-xs text-slate-400">No outputs yet.</div>}
            {(opsMetrics?.activity ?? []).slice(0, 12).map((activity) => (
              <div key={`${activity.timestamp}-${activity.pipeline_id ?? activity.agent ?? ''}`} className="p-3 bg-slate-800/60 border border-cyan-500/20 rounded">
                <div className="flex items-center justify-between">
                  <div className="font-semibold text-white">{activity.agent ?? 'Automation'}</div>
                  <div className="text-xs text-cyan-200/70">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="text-xs text-slate-300 mt-1">{activity.summary ?? 'Automation update'}</div>
                <div className="text-[10px] text-slate-400 mt-1">{activity.stage ?? activity.status ?? 'activity'}</div>
              </div>
            ))}
          </div>
        )}
        {detailKey === 'errors' && (
          <div className="space-y-3 text-sm text-slate-200">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-slate-400">Activity errors</span>
                <div className="text-white">
                  {(opsMetrics?.activity ?? []).filter((entry) => entry.status === 'error').length}
                </div>
              </div>
              <div>
                <span className="text-slate-400">Failed payouts</span>
                <div className="text-white">{financialMetrics?.failed_payouts_count ?? 0}</div>
              </div>
            </div>
            <h4 className="text-sm text-cyan-300 font-semibold">Error log</h4>
            {(opsMetrics?.activity ?? []).filter((entry) => entry.status === 'error').length === 0 && (
              <div className="text-xs text-slate-400">No error entries yet.</div>
            )}
            {(opsMetrics?.activity ?? [])
              .filter((entry) => entry.status === 'error')
              .slice(0, 12)
              .map((entry) => (
                <div key={`${entry.timestamp}-${entry.pipeline_id ?? entry.agent ?? ''}`} className="p-3 bg-red-500/10 border border-red-500/30 rounded">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-red-300">{entry.agent ?? 'Automation'}</div>
                    <div className="text-xs text-red-200/70">{new Date(entry.timestamp).toLocaleString()}</div>
                  </div>
                  <div className="text-xs text-slate-200 mt-1">{entry.summary ?? 'Error event'}</div>
                </div>
              ))}
          </div>
        )}
      </DetailModal>
    </div>
  );
};

const PanelMetric: React.FC<{ label: string; value: string | number; color: string; onClick?: () => void }> = ({
  label,
  value,
  color,
  onClick,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/70 border border-cyan-500/20 rounded-xl px-4 py-3 flex items-center justify-between shadow-[0_0_24px_rgba(0,214,255,0.08)] cursor-pointer hover:border-cyan-500/40 transition-colors"
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(event) => {
        if (!onClick) return;
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          onClick();
        }
      }}
    >
      <div>
        <div className="text-[10px] text-cyan-200/70 uppercase tracking-widest">{label}</div>
        <div className={`text-xl font-bold ${color} font-mono`}>{value}</div>
      </div>
      <div className="h-8 w-8 rounded-full border border-cyan-500/30 bg-cyan-500/10 flex items-center justify-center text-xs text-cyan-200/70">
        ✓
      </div>
    </motion.div>
  );
};
