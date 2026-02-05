import React from 'react';
import { fetchSystemStatus } from '../../api/systemStatusApi';

export const ForecastEnginePanel: React.FC = () => {
  const [forecast, setForecast] = React.useState<{ revenue: number; target: number } | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchSystemStatus();
        if (!mounted) return;
        const perf = (response as any)?.system_health?.system_overview?.performance_metrics ?? {};
        const revenue = Number(perf.total_revenue ?? 0);
        const target = Number(perf.monthly_target ?? 0);
        setForecast({ revenue, target });
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load forecast data');
      }
    };

    void load();
    return () => {
      mounted = false;
      controller.abort();
    };
  }, []);

  const projected = forecast?.target && forecast?.revenue
    ? Math.max(0, forecast.target - forecast.revenue)
    : 0;

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Forecast Engine</h3>
          <p className="text-sm text-slate-300">ROI projection based on current revenue pacing.</p>
        </div>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Current Revenue</p>
            <p className="text-lg text-white">${forecast?.revenue.toFixed(2)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Target Gap</p>
            <p className="text-lg text-white">${projected.toFixed(2)}</p>
          </div>
        </div>
      )}
    </div>
  );
};
