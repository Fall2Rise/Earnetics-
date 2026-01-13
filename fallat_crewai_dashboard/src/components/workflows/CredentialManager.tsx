import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  StoreCredentialRequest,
  VaultCredential,
  CredentialSuggestion,
  deleteCredential,
  listCredentials,
  storeCredential,
  getCredentialSuggestions,
  markSuggestionAdded,
  dismissSuggestion,
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
  const [suggestions, setSuggestions] = useState<CredentialSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [form, setForm] = useState(DEFAULT_FORM);
  const [metadataText, setMetadataText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [filterStream, setFilterStream] = useState<string>('');

  const loadCredentials = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listCredentials(undefined, abortSignal);
      if (abortSignal?.aborted) return; // Don't update state if request was cancelled
      setCredentials(data);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return; // Ignore errors from cancelled requests
      setError(err instanceof Error ? err.message : 'Failed to load credentials');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    void loadCredentials(abortController.signal);
    return () => {
      abortController.abort(); // Cancel request on unmount
    };
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
    if (!form.service.trim() || !form.name.trim()) {
      setError('Service and name are required.');
      return;
    }
    setLoading(true);
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
      await loadSuggestions(); // Refresh suggestions to mark as added
      // Mark suggestion as added if it was from a suggestion
      const matchingSuggestion = suggestions.find(
        s => s.service === form.service.trim() && s.name === form.name.trim()
      );
      if (matchingSuggestion && !matchingSuggestion.is_added) {
        try {
          await markSuggestionAdded(form.service.trim(), form.name.trim());
          await loadSuggestions();
        } catch (e) {
          // Non-critical error, just log it
          console.warn('Failed to mark suggestion as added:', e);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to store credential');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (service: string, name: string) => {
    setError(null);
    setSuccess(null);
    try {
      await deleteCredential(service, name);
      setSuccess('Credential removed.');
      await loadCredentials();
      await loadSuggestions(); // Refresh suggestions
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete credential');
    }
  };

  const handleDismissSuggestion = async (service: string, name: string) => {
    try {
      await dismissSuggestion(service, name);
      await loadSuggestions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to dismiss suggestion');
    }
  };

  const handleAddFromSuggestion = (suggestion: CredentialSuggestion) => {
    setForm({
      service: suggestion.service,
      name: suggestion.name,
      secret: '',
      confirmSecret: '',
      metadata: {},
    });
    setMetadataText(JSON.stringify(suggestion.metadata || {}, null, 2));
    // Scroll to form
    document.querySelector('.credential-form')?.scrollIntoView({ behavior: 'smooth' });
  };

  const revenueStreams = useMemo(() => {
    const streams = new Set<string>();
    suggestions.forEach(s => {
      if (s.revenue_stream) streams.add(s.revenue_stream);
    });
    return Array.from(streams).sort();
  }, [suggestions]);

  const pendingSuggestions = useMemo(() => {
    return suggestions.filter(s => !s.is_added && s.status === 'suggested');
  }, [suggestions]);

  return (
    <div className="credential-manager">
      <header className="panel-header">
        <div>
          <h3>🔐 Credential Vault</h3>
          <span className="credential-manager__subtitle">Securely store API keys, tokens, and account credentials for agents to use</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadCredentials()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}
      {success && <p className="panel-success">{success}</p>}

      <div className="credential-manager__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Add your external account credentials here (Stripe, PayPal, SMTP, API keys, etc.). 
          Agents will automatically retrieve and use these credentials when they need to access external services. 
          All credentials are encrypted and stored securely.
        </p>
      </div>

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

      <section className="credential-suggestions">
        <header className="flex items-center justify-between mb-4">
          <div>
            <h4>💡 Suggested Credentials</h4>
            <p className="text-xs text-slate-400 mt-1">
              {pendingSuggestions.length} pending suggestions • {suggestions.filter(s => s.is_added).length} already added
            </p>
          </div>
          <div className="flex gap-2">
            <select
              value={filterStream}
              onChange={(e) => setFilterStream(e.target.value)}
              className="px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white text-sm"
            >
              <option value="">All Revenue Streams</option>
              {revenueStreams.map(stream => (
                <option key={stream} value={stream}>{stream}</option>
              ))}
            </select>
            <button
              type="button"
              className="refresh-button"
              onClick={() => void loadSuggestions()}
              disabled={loadingSuggestions}
            >
              {loadingSuggestions ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </header>
        
        {pendingSuggestions.length === 0 ? (
          <p className="panel-empty">All suggested credentials have been added! 🎉</p>
        ) : (
          <div className="suggestions-grid">
            {pendingSuggestions.map((suggestion) => (
              <div
                key={`${suggestion.service}-${suggestion.name}`}
                className={`suggestion-card suggestion-card--${suggestion.revenue_impact}`}
              >
                <div className="suggestion-card__header">
                  <div>
                    <h5>{suggestion.service} / {suggestion.name}</h5>
                    <span className="suggestion-card__stream">{suggestion.revenue_stream}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`badge badge--${suggestion.revenue_impact === 'high' ? 'error' : suggestion.revenue_impact === 'medium' ? 'warn' : 'ok'}`}>
                      {suggestion.revenue_impact} impact
                    </span>
                    <span className="text-xs text-slate-400">Priority: {suggestion.priority}/10</span>
                  </div>
                </div>
                <p className="suggestion-card__description">{suggestion.description}</p>
                {suggestion.discovered_by && (
                  <p className="text-xs text-slate-500 mt-2">
                    Discovered by: {suggestion.discovered_by}
                  </p>
                )}
                <div className="suggestion-card__actions">
                  <button
                    type="button"
                    className="primary-button"
                    onClick={() => handleAddFromSuggestion(suggestion)}
                  >
                    Add Credential
                  </button>
                  <button
                    type="button"
                    className="refresh-button"
                    onClick={() => void handleDismissSuggestion(suggestion.service, suggestion.name)}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {pendingSuggestions.length > 0 && (
        <section className="credential-suggestions">
          <header className="flex items-center justify-between mb-4">
            <div>
              <h4>💡 Suggested Credentials</h4>
              <p className="text-xs text-slate-400 mt-1">
                {pendingSuggestions.length} pending suggestions • {suggestions.filter(s => s.is_added).length} already added
              </p>
            </div>
            <div className="flex gap-2">
              <select
                value={filterStream}
                onChange={(e) => setFilterStream(e.target.value)}
                className="px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white text-sm"
              >
                <option value="">All Revenue Streams</option>
                {revenueStreams.map(stream => (
                  <option key={stream} value={stream}>{stream}</option>
                ))}
              </select>
              <button
                type="button"
                className="refresh-button"
                onClick={() => void loadSuggestions()}
                disabled={loadingSuggestions}
              >
                {loadingSuggestions ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </header>
          
          <div className="suggestions-grid">
            {pendingSuggestions.map((suggestion) => (
              <div
                key={`${suggestion.service}-${suggestion.name}`}
                className={`suggestion-card suggestion-card--${suggestion.revenue_impact}`}
              >
                <div className="suggestion-card__header">
                  <div>
                    <h5>{suggestion.service} / {suggestion.name}</h5>
                    <span className="suggestion-card__stream">{suggestion.revenue_stream}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`badge badge--${suggestion.revenue_impact === 'high' ? 'error' : suggestion.revenue_impact === 'medium' ? 'warn' : 'ok'}`}>
                      {suggestion.revenue_impact} impact
                    </span>
                    <span className="text-xs text-slate-400">Priority: {suggestion.priority}/10</span>
                  </div>
                </div>
                <p className="suggestion-card__description">{suggestion.description}</p>
                {suggestion.discovered_by && (
                  <p className="text-xs text-slate-500 mt-2">
                    Discovered by: {suggestion.discovered_by}
                  </p>
                )}
                <div className="suggestion-card__actions">
                  <button
                    type="button"
                    className="primary-button"
                    onClick={() => handleAddFromSuggestion(suggestion)}
                  >
                    Add Credential
                  </button>
                  <button
                    type="button"
                    className="refresh-button"
                    onClick={() => void handleDismissSuggestion(suggestion.service, suggestion.name)}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

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
