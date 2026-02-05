import React from 'react';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';

export const ResourceMonitorPanel: React.FC = () => {
  const [status, setStatus] = React.useState<SystemStatusResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchSystemStatus();
        if (!mounted) return;
        setStatus(response);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load system status');
      }
    };

    void load();
    const interval = setInterval(load, 15000);

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  const metrics = status?.metrics;

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Resource Monitor</h3>
          <p className="text-sm text-slate-300">System uptime, services, and control state.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {status?.status ?? 'offline'}
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Uptime</p>
            <p className="text-lg text-white">{metrics?.uptime_hours ?? 0}h</p>
            <p className="mt-2 text-xs uppercase text-slate-400">Requests</p>
            <p className="text-sm text-slate-200">{metrics?.total_requests ?? 0}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Connected Modules</p>
            <p className="text-lg text-white">{metrics?.connected_modules ?? 0}</p>
            <p className="mt-2 text-xs uppercase text-slate-400">Revenue</p>
            <p className="text-sm text-slate-200">${(metrics?.total_revenue ?? 0).toFixed(2)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Services</p>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              <li>Vector Memory: {status?.services?.vector_memory ?? 'unknown'}</li>
              <li>Credential Vault: {status?.services?.credential_vault ?? 'unknown'}</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Control State</p>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              <li>Kill Switch: {status?.kill_switch_active ? 'ACTIVE' : 'standby'}</li>
              <li>Safe Mode: {status?.safe_mode ? 'enabled' : 'normal'}</li>
              <li>Agents Paused: {status?.agent_paused ? 'yes' : 'no'}</li>
              <li>Mail Paused: {status?.mail_paused ? 'yes' : 'no'}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
