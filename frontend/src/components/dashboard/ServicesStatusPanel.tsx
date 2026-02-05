import React from 'react';
import { fetchServices, ServiceInfo } from '../../api/servicesApi';

export const ServicesStatusPanel: React.FC = () => {
  const [services, setServices] = React.useState<ServiceInfo[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchServices(controller.signal);
        if (!mounted) return;
        setServices(response.services || []);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load services');
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
          <h3 className="text-xl text-white">Service Registry</h3>
          <p className="text-sm text-slate-300">Operational status and dependencies.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {services.length} services
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : services.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No services reported.</p>
      ) : (
        <div className="mt-6 grid gap-3 md:grid-cols-2">
          {services.map((service) => (
            <div key={service.key} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h4 className="text-base text-white">{service.name}</h4>
                  <p className="text-xs text-slate-400">{service.category}</p>
                </div>
                <span className="text-xs uppercase text-emerald-300">{service.status}</span>
              </div>
              <p className="mt-2 text-sm text-slate-200">{service.description}</p>
              {service.dependencies && service.dependencies.length > 0 && (
                <p className="mt-2 text-xs text-slate-400">
                  Dependencies: {service.dependencies.join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
