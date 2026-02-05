import React from 'react';
import { fetchPlaybooks, PlaybookTemplate } from '../../api/playbooksApi';

export const PlaybookLibraryPanel: React.FC = () => {
  const [templates, setTemplates] = React.useState<PlaybookTemplate[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchPlaybooks(controller.signal);
        if (!mounted) return;
        const nextTemplates = Array.isArray(response)
          ? response
          : Array.isArray(response.templates)
          ? response.templates
          : [];
        setTemplates(nextTemplates);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load playbooks');
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
          <h3 className="text-xl text-white">Reusable Playbook Library</h3>
          <p className="text-sm text-slate-300">Approved automation templates.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {templates.length} playbooks
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : templates.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No playbooks available.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {templates.map((template) => (
            <div key={template.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h4 className="text-base text-white">{template.name || template.id}</h4>
              <p className="text-xs text-slate-400">{template.category || 'general'}</p>
              {template.description && <p className="mt-2 text-sm text-slate-200">{template.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
