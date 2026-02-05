import React from 'react';
import { fetchTools, ToolSpec } from '../../api/toolsApi';

export const ToolForgePanel: React.FC = () => {
  const [tools, setTools] = React.useState<ToolSpec[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchTools(controller.signal);
        if (!mounted) return;
        setTools(response.tools || []);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load tools');
      }
    };

    void load();
    return () => {
      mounted = false;
      controller.abort();
    };
  }, []);

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Tool Forge</h3>
          <p className="text-sm text-slate-300">Registered tools and execution categories.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {tools.length} tools
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : tools.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No tools registered.</p>
      ) : (
        <div className="mt-6 grid gap-3 md:grid-cols-2">
          {tools.map((tool) => (
            <div key={tool.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h4 className="text-base text-white">{tool.name}</h4>
              <p className="text-xs text-slate-400">{tool.category}</p>
              <p className="mt-2 text-sm text-slate-200">{tool.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
