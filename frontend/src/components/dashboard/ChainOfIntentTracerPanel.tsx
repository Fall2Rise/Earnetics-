import React from 'react';
import { fetchAuditEvents, AuditEvent } from '../../api/auditApi';

export const ChainOfIntentTracerPanel: React.FC = () => {
  const [events, setEvents] = React.useState<AuditEvent[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchAuditEvents(controller.signal);
        if (!mounted) return;
        setEvents(response.events.slice(0, 12));
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load audit events');
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
          <h3 className="text-xl text-white">Chain of Intent Tracer</h3>
          <p className="text-sm text-slate-300">Map outputs back to inputs and directive references.</p>
        </div>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : (
        <div className="mt-6 space-y-3">
          {events.map((event) => (
            <div key={event.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-4 text-xs text-slate-400">
                <span>{event.timestamp}</span>
                <span>{event.status}</span>
              </div>
              <p className="mt-1 text-sm text-white">{event.action}</p>
              {event.message && <p className="mt-1 text-sm text-slate-300">{event.message}</p>}
              {event.details && (
                <pre className="mt-2 max-h-32 overflow-auto rounded-lg bg-slate-900/60 p-2 text-[11px] text-slate-300">
                  {JSON.stringify(event.details, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
