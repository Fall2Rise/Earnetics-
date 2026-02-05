import React from 'react';
import { fetchIntegrations, IntegrationsResponse } from '../../api/integrationsApi';

export const IntegrationRegistryPanel: React.FC = () => {
  const [integrations, setIntegrations] = React.useState<IntegrationsResponse>({});
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchIntegrations(controller.signal);
        if (!mounted) return;
        setIntegrations(response);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load integrations');
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

  const entries = Object.entries(integrations);

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Integration Registry</h3>
          <p className="text-sm text-slate-300">Connected services and missing credentials.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {entries.length} integrations
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : entries.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No integrations detected.</p>
      ) : (
        <div className="mt-6 grid gap-3 md:grid-cols-2">
          {entries.map(([name, info]) => (
            <div key={name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h4 className="text-base text-white">{name}</h4>
                  <p className="text-xs text-slate-400">{info.status}</p>
                </div>
                <span className="text-xs uppercase text-slate-300">
                  {info.production_mode ? 'prod' : 'safe'}
                </span>
              </div>
              {info.missing_vars && info.missing_vars.length > 0 && (
                <p className="mt-2 text-xs text-amber-300">
                  Missing: {info.missing_vars.join(', ')}
                </p>
              )}
              {info.found_in_vault && info.found_in_vault.length > 0 && (
                <p className="mt-2 text-xs text-emerald-300">
                  Vault: {info.found_in_vault.join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
