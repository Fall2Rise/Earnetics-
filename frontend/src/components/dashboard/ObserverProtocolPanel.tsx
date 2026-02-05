import React from 'react';
import { fetchAuditEvents } from '../../api/auditApi';
import { fetchSystemStatus } from '../../api/systemStatusApi';

export const ObserverProtocolPanel: React.FC = () => {
  const [anomalies, setAnomalies] = React.useState<any[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [safeMode, setSafeMode] = React.useState(false);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const [audit, status] = await Promise.all([
          fetchAuditEvents(controller.signal),
          fetchSystemStatus(),
        ]);
        if (!mounted) return;
        const flagged = audit.events.filter((event) =>
          ['guardian_violation', 'kill_switch', 'system_control_update'].includes(event.action)
        );
        setAnomalies(flagged.slice(0, 10));
        setSafeMode(status.safe_mode);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load observer data');
      }
    };

    void load();
    const interval = setInterval(load, 25000);

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Observer Protocol</h3>
          <p className="text-sm text-slate-300">Drift and corruption monitoring.</p>
        </div>
        <span className="text-xs text-amber-300 uppercase tracking-[0.2em]">
          {safeMode ? 'SAFE MODE' : 'NORMAL'}
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : anomalies.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No anomalies detected.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {anomalies.map((event) => (
            <div key={event.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs text-slate-400">{event.timestamp}</p>
              <p className="text-sm text-white">{event.action}</p>
              {event.message && <p className="text-sm text-slate-300">{event.message}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
