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
    }
  };

  return (
    <div className='model-manager glass-panel'>
      <header className='panel-header'>
        <div>
          <h3>Model Registry</h3>
          <span>Manage embedding and LLM models</span>
        </div>
        <button type='button' className='refresh-button' onClick={() => void loadModels()} disabled={loading}>
          {loading ? 'Refreshing...' : 'Reload'}
        </button>
      </header>

      {error && <p className='panel-error'>{error}</p>}

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
