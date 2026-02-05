import React from 'react';
import { fetchAuditEvents, logAuditReason, ReasonLogPayload } from '../../api/auditApi';

export const ReasonExplainEnginePanel: React.FC = () => {
  const [events, setEvents] = React.useState([]);
  const [error, setError] = React.useState<string | null>(null);
  const [form, setForm] = React.useState<ReasonLogPayload>({
    action: '',
    reason: '',
    directive_ref: '',
    risk_level: 'GREEN',
    context: {},
  });
  const [saving, setSaving] = React.useState(false);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchAuditEvents(controller.signal);
        if (!mounted) return;
        setEvents(response.events.slice(0, 8));
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load audit events');
      }
    };

    void load();
    const interval = setInterval(load, 20000);

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    try {
      await logAuditReason(form);
      setForm({ action: '', reason: '', directive_ref: '', risk_level: 'GREEN', context: {} });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log reason');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Reason Explain Engine</h3>
          <p className="text-sm text-slate-300">Log justification + directive linkage for actions.</p>
        </div>
      </header>

      <form onSubmit={onSubmit} className="mt-6 grid gap-4 md:grid-cols-2">
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Action name"
          value={form.action}
          onChange={(e) => setForm((prev) => ({ ...prev, action: e.target.value }))}
          required
        />
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Directive reference (e.g., non_negotiables)"
          value={form.directive_ref}
          onChange={(e) => setForm((prev) => ({ ...prev, directive_ref: e.target.value }))}
          required
        />
        <select
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          value={form.risk_level}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, risk_level: e.target.value as ReasonLogPayload['risk_level'] }))
          }
        >
          <option value="GREEN">GREEN</option>
          <option value="YELLOW">YELLOW</option>
          <option value="RED">RED</option>
        </select>
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason (justification)"
          value={form.reason}
          onChange={(e) => setForm((prev) => ({ ...prev, reason: e.target.value }))}
          required
        />
        <div className="md:col-span-2 flex items-center justify-between">
          <span className="text-xs text-slate-400">All submissions are logged to audit trail.</span>
          <button
            type="submit"
            disabled={saving}
            className="rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
          >
            {saving ? 'Logging…' : 'Log Reason'}
          </button>
        </div>
      </form>

      {error && <p className="mt-4 text-sm text-red-300">{error}</p>}

      <div className="mt-6 space-y-3">
        {events.map((event: any) => (
          <div key={event.id} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
            <p className="text-xs text-slate-400">{event.timestamp}</p>
            <p className="text-white">{event.action}</p>
            {event.message && <p className="text-slate-300">{event.message}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};
