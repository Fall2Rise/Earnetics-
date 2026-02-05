import React from 'react';
import { createLibraryItem, fetchLibraryItems, LibraryItem } from '../../api/libraryApi';
import { logAuditReason } from '../../api/auditApi';

export const ContentRegistryPanel: React.FC = () => {
  const [items, setItems] = React.useState<LibraryItem[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [title, setTitle] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [reason, setReason] = React.useState('');
  const [saving, setSaving] = React.useState(false);

  const loadItems = React.useCallback(async () => {
    try {
      const response = await fetchLibraryItems('Content');
      setItems(response.items || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load content registry');
    }
  }, []);

  React.useEffect(() => {
    void loadItems();
  }, [loadItems]);

  const handleCreate = async () => {
    if (!title || !reason) return;
    setSaving(true);
    try {
      await logAuditReason({
        action: 'content_registry_entry',
        reason,
        directive_ref: 'wealth_support_systems',
        risk_level: 'GREEN',
      });
      await createLibraryItem({
        title,
        description,
        category: 'Content',
      });
      setTitle('');
      setDescription('');
      setReason('');
      await loadItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create entry');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Content Registry</h3>
          <p className="text-sm text-slate-300">Content assets, scripts, and metadata.</p>
        </div>
      </header>

      <div className="mt-6 grid gap-3 md:grid-cols-3">
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <input
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason / directive link"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
      </div>
      <button
        className="mt-3 rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
        onClick={handleCreate}
        disabled={saving || !title || !reason}
      >
        {saving ? 'Saving…' : 'Add to Registry'}
      </button>

      {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

      <div className="mt-6 space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-300">No content assets registered.</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h4 className="text-base text-white">{item.title}</h4>
              {item.description && <p className="mt-1 text-sm text-slate-200">{item.description}</p>}
              <p className="mt-2 text-xs text-slate-400">
                Last updated: {item.last_updated || 'unknown'}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
