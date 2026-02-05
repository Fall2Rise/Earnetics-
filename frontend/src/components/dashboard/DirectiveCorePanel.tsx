import React from 'react';
import { fetchPrimeDirective } from '../../api/primeDirectiveApi';

type PrimeDirective = Record<string, unknown>;

const formatValue = (value: unknown) => {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (value && typeof value === 'object') {
    return null;
  }
  return value ?? '—';
};

export const DirectiveCorePanel: React.FC = () => {
  const [directive, setDirective] = React.useState<PrimeDirective | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchPrimeDirective(controller.signal);
        setDirective(response.prime_directive);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load Prime Directive');
      }
    };

    void load();
    return () => controller.abort();
  }, []);

  const meta = directive ?? {};

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Directive Core</h3>
          <p className="text-sm text-slate-300">Prime Directive authority and alignment snapshot.</p>
        </div>
        <span className="text-xs text-emerald-300 uppercase tracking-[0.2em]">Read Only</span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Version</p>
            <p className="text-lg text-white">{formatValue(meta.version)}</p>
            <p className="mt-2 text-xs uppercase text-slate-400">Codename</p>
            <p className="text-sm text-slate-200">{formatValue(meta.codename)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Owner</p>
            <p className="text-lg text-white">{formatValue(meta.owner)}</p>
            <p className="mt-2 text-xs uppercase text-slate-400">Agent Role</p>
            <p className="text-sm text-slate-200">{formatValue(meta.agent_role)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 md:col-span-2">
            <p className="text-xs uppercase text-slate-400">Alignment Hierarchy</p>
            <p className="text-sm text-slate-200">
              {formatValue(meta.alignment_hierarchy)}
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Non‑Negotiables</p>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              {meta.non_negotiables && typeof meta.non_negotiables === 'object'
                ? Object.entries(meta.non_negotiables as Record<string, unknown>).map(([key, value]) => (
                    <li key={key} className="flex items-center justify-between">
                      <span>{key.replace(/_/g, ' ')}</span>
                      <span className="text-xs text-emerald-300">
                        {String(value)}
                      </span>
                    </li>
                  ))
                : '—'}
            </ul>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase text-slate-400">Risk Governance</p>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              {meta.risk_governance && typeof meta.risk_governance === 'object'
                ? Object.entries(meta.risk_governance as Record<string, unknown>).map(([key, value]) => (
                    <li key={key}>
                      <span className="text-xs uppercase text-slate-400">{key}</span>
                      <p className="text-sm text-slate-200">{formatValue(value)}</p>
                    </li>
                  ))
                : '—'}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
