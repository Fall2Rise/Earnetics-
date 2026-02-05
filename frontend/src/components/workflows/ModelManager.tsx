import React, { useCallback, useEffect, useState } from 'react';
import { activateModel, listModels, ModelFamily, ModelInfo, registerModel } from '../../api/modelApi';

const families: ModelFamily[] = ['embedding', 'llm'];

export const ModelManager: React.FC = () => {
  const [models, setModels] = useState<Record<ModelFamily, ModelInfo[]>>({ embedding: [], llm: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [family, setFamily] = useState<ModelFamily>('embedding');
  const [form, setForm] = useState({ name: '', version: '', localPath: '' });

  const loadModels = useCallback(async () => {
    setLoading(true);
    try {
      const result: Record<ModelFamily, ModelInfo[]> = {} as Record<ModelFamily, ModelInfo[]>;
      for (const fam of families) {
        result[fam] = await listModels(fam);
      }
      setModels(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load models');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadModels();
  }, [loadModels]);

  const handleActivate = async (fam: ModelFamily, name: string) => {
    try {
      await activateModel(fam, name);
      await loadModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to activate model');
    }
  };

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!form.name || !form.version) {
      setError('Name and version are required.');
      return;
    }
    setLoading(true);
    try {
      await registerModel({
        name: form.name,
        family,
        version: form.version,
        local_path: form.localPath || undefined,
        active: false,
      });
      setForm({ name: '', version: '', localPath: '' });
      await loadModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register model');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='model-manager'>
      <header className='panel-header'>
        <div>
          <h3>🤖 Model Registry</h3>
          <span className="model-manager__subtitle">Manage embedding and LLM models for agent operations</span>
        </div>
        <button type='button' className='refresh-button' onClick={() => void loadModels()} disabled={loading}>
          {loading ? 'Refreshing...' : 'Reload'}
        </button>
      </header>

      {error && <p className='panel-error'>{error}</p>}

      <div className="model-manager__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Register and activate LLM and embedding models for agent use. 
          Models can be local files or remote services. Activate models to make them available for agent operations.
        </p>
      </div>

      <section className='model-register'>
        <h4>Register Model</h4>
        <form onSubmit={handleRegister} className='model-form'>
          <label>
            Family
            <select value={family} onChange={(event) => setFamily(event.target.value as ModelFamily)}>
              {families.map((fam) => (
                <option key={fam} value={fam}>
                  {fam}
                </option>
              ))}
            </select>
          </label>
          <label>
            Name
            <input value={form.name} onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))} required />
          </label>
          <label>
            Version
            <input value={form.version} onChange={(event) => setForm((prev) => ({ ...prev, version: event.target.value }))} required />
          </label>
          <label>
            Local Path (optional)
            <input value={form.localPath} onChange={(event) => setForm((prev) => ({ ...prev, localPath: event.target.value }))} />
          </label>
          <button type='submit' className='primary-button'>Register</button>
        </form>
      </section>

      <section className='model-list'>
        {families.map((fam) => (
          <div key={fam} className='model-card'>
            <header>
              <h4>{fam.toUpperCase()} Models</h4>
            </header>
            {models[fam]?.length ? (
              <ul>
                {models[fam].map((model) => (
                  <li key={model.name}>
                    <div>
                      <strong>{model.name}</strong>
                      <span>Version: {model.version}</span>
                      {model.local_path && <span>Local: {model.local_path}</span>}
                    </div>
                    <div className='model-actions'>
                      <span className={model.active ? 'badge badge--ok' : 'badge'}>{model.active ? 'Active' : 'Inactive'}</span>
                      <button type='button' className='refresh-button' onClick={() => void handleActivate(fam, model.name)}>
                        Activate
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className='panel-empty'>No models registered.</p>
            )}
          </div>
        ))}
      </section>
    </div>
  );
};
