import React from 'react';
import { logAuditReason } from '../../api/auditApi';

export const ContentEnginePanel: React.FC = () => {
  const [reason, setReason] = React.useState('');
  const [status, setStatus] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handleRequest = async () => {
    setStatus(null);
    setError(null);
    try {
      await logAuditReason({
        action: 'content_engine_request',
        reason,
        directive_ref: 'wealth_support_systems',
        risk_level: 'YELLOW',
        owner_approved: true,
      });
      setStatus('Content request logged. Awaiting backend content pipeline.');
      setReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log request');
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Content Engine</h3>
          <p className="text-sm text-slate-300">
            Directive‑bound content generation requests (manual approval required).
          </p>
        </div>
      </header>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <input
          className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason / directive link"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
        <button
          className="rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
          onClick={handleRequest}
          disabled={!reason}
        >
          Log Request
        </button>
      </div>

      {status && <p className="mt-3 text-xs text-emerald-300">{status}</p>}
      {error && <p className="mt-3 text-xs text-red-300">{error}</p>}
    </div>
  );
};
