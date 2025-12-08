import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  StoreCredentialRequest,
  VaultCredential,
  deleteCredential,
  listCredentials,
  storeCredential,
} from '../../api/credentialsApi';

const SERVICE_PRESETS: string[] = [
  'stripe',
  'paypal',
  'clickbank',
  'digistore24',
  'shopify',
  'gumroad',
  'smtp',
  'llm',
];

const DEFAULT_FORM: StoreCredentialRequest & { confirmSecret: string } = {
  service: '',
  name: '',
  secret: '',
  confirmSecret: '',
  metadata: {},
};

const parseMetadata = (value: string): Record<string, unknown> => {
  if (!value.trim()) return {};
  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error('Metadata must be valid JSON.');
  }
};

export const CredentialManager: React.FC = () => {
  const [credentials, setCredentials] = useState<VaultCredential[]>([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState(DEFAULT_FORM);
  const [metadataText, setMetadataText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadCredentials = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listCredentials();
      setCredentials(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load credentials');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCredentials();
  }, [loadCredentials]);

  const groupedCredentials = useMemo(() => {
    const groups: Record<string, VaultCredential[]> = {};
    for (const credential of credentials) {
      const key = credential.service || 'general';
      groups[key] = groups[key] ? [...groups[key], credential] : [credential];
    }
    return Object.entries(groups);
  }, [credentials]);

  const handleInputChange = (key: keyof StoreCredentialRequest | 'confirmSecret') => (event: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [key]: event.target.value }));
  };

  const handleMetadataChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMetadataText(event.target.value);
  };

  const resetForm = () => {
    setForm(DEFAULT_FORM);
    setMetadataText('');
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (form.secret !== form.confirmSecret) {
      setError('Secret confirmation does not match.');
      return;
    }
    try {
      const metadata = parseMetadata(metadataText);
      await storeCredential({
        service: form.service.trim(),
        name: form.name.trim(),
        secret: form.secret,
        metadata,
      });
      setSuccess('Credential stored successfully.');
      resetForm();
      await loadCredentials();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to store credential');
    }
  };

  const handleDelete = async (service: string, name: string) => {
    setError(null);
    setSuccess(null);
    try {
      await deleteCredential(service, name);
      setSuccess('Credential removed.');
      await loadCredentials();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete credential');
    }
  };

  return (
    <div className="credential-manager glass-panel">
      <header className="panel-header">
        <div>
          <h3>Credential Vault</h3>
          <span>Securely manage API keys and secrets</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadCredentials()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}
      {success && <p className="panel-success">{success}</p>}

      <section className="credential-form">
        <h4>Add Credential</h4>
        <form onSubmit={handleSubmit} className="credential-form__grid">
          <label>
            Service
            <input
              list="service-presets"
              value={form.service}
              onChange={handleInputChange('service')}
              placeholder="stripe"
              required
            />
            <datalist id="service-presets">
              {SERVICE_PRESETS.map((item) => (
                <option key={item} value={item} />
              ))}
            </datalist>
          </label>
          <label>
            Name
            <input value={form.name} onChange={handleInputChange('name')} placeholder="SECRET_KEY" required />
          </label>
          <label>
            Secret
            <input type="password" value={form.secret} onChange={handleInputChange('secret')} required />
          </label>
          <label>
            Confirm Secret
            <input type="password" value={form.confirmSecret} onChange={handleInputChange('confirmSecret')} required />
          </label>
          <label className="credential-form__metadata">
            Metadata (JSON, optional)
            <textarea value={metadataText} onChange={handleMetadataChange} rows={4} placeholder='{"account_id": "acct_123"}' />
          </label>
          <button type="submit" className="primary-button">
            Save Credential
          </button>
        </form>
      </section>

      <section className="credential-list">
        <header>
          <h4>Stored Credentials</h4>
        </header>
        {groupedCredentials.length === 0 ? (
          <p className="panel-empty">No credentials stored yet.</p>
        ) : (
          groupedCredentials.map(([service, items]) => (
            <div key={service} className="credential-card">
              <div className="credential-card__header">
                <h5>{service}</h5>
                <span>{items.length} key(s)</span>
              </div>
              <ul>
                {items.map((item) => (
                  <li key={`${service}-${item.name}`}>
                    <div>
                      <strong>{item.name}</strong>
                      {item.metadata && Object.keys(item.metadata).length > 0 && (
                        <pre>{JSON.stringify(item.metadata, null, 2)}</pre>
                      )}
                      <span className="credential-card__timestamp">
                        Last updated: {item.updated_at ? new Date(item.updated_at).toLocaleString() : 'unknown'}
                      </span>
                    </div>
                    <button type="button" className="refresh-button" onClick={() => void handleDelete(service, item.name)}>
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </section>
    </div>
  );
};
