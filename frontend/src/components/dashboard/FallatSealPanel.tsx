import React from 'react';
import { logAuditReason } from '../../api/auditApi';

export const FallatSealPanel: React.FC = () => {
  const [reason, setReason] = React.useState('');
  const [approval, setApproval] = React.useState(false);
  const [cryptoApproval, setCryptoApproval] = React.useState(false);
  const [status, setStatus] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handleLog = async () => {
    setStatus(null);
    setError(null);
    try {
      await logAuditReason({
        action: 'fallat_seal_request',
        reason,
        directive_ref: 'proof_of_alignment_ledger',
        risk_level: 'RED',
        owner_approved: approval,
        cryptographic_approval: cryptoApproval,
      });
      setStatus('Request logged. Seal layer remains locked.');
      setReason('');
      setApproval(false);
      setCryptoApproval(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log request');
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Fallat Seal Layer</h3>
          <p className="text-sm text-slate-300">Cryptographic signing and lineage proofs (locked).</p>
        </div>
        <span className="text-xs text-rose-300 uppercase tracking-[0.2em]">Locked</span>
      </header>

      <div className="mt-6 grid gap-3">
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason / directive link"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
        <label className="flex items-center gap-2 text-xs text-slate-300">
          <input type="checkbox" checked={approval} onChange={(e) => setApproval(e.target.checked)} />
          Owner approval acknowledged
        </label>
        <label className="flex items-center gap-2 text-xs text-slate-300">
          <input type="checkbox" checked={cryptoApproval} onChange={(e) => setCryptoApproval(e.target.checked)} />
          Cryptographic approval attached
        </label>
        <button
          className="rounded-full border border-rose-400/50 px-4 py-2 text-xs uppercase text-rose-200"
          onClick={handleLog}
          disabled={!reason}
        >
          Log Seal Request
        </button>
        {status && <p className="text-xs text-emerald-300">{status}</p>}
        {error && <p className="text-xs text-red-300">{error}</p>}
      </div>
    </div>
  );
};
