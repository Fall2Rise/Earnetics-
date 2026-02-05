import React, { useCallback, useEffect, useState } from 'react';
import { NotificationSettings, getNotificationSettings, updateNotificationSettings } from '../../api/notificationApi';

const DEFAULT_SETTINGS: NotificationSettings = {
  email_enabled: false,
  email_recipients: [],
  desktop_log: true,
};

export const NotificationsPanel: React.FC = () => {
  const [settings, setSettings] = useState<NotificationSettings>(DEFAULT_SETTINGS);
  const [recipientsText, setRecipientsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadSettings = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await getNotificationSettings();
      if (abortSignal?.aborted) return; // Don't update state if request was cancelled
      setSettings(data);
      setRecipientsText((data.email_recipients || []).join(','));
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return; // Ignore errors from cancelled requests
      setError(err instanceof Error ? err.message : 'Failed to load notification settings');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    void loadSettings(abortController.signal);
    return () => {
      abortController.abort(); // Cancel request on unmount
    };
  }, [loadSettings]);

  const handleToggle = (key: keyof NotificationSettings) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.checked;
    setSettings((prev) => ({ ...prev, [key]: value }));
    // Settings update immediately in UI, saved on form submit
  };

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const payload: NotificationSettings = {
        ...settings,
        email_recipients: recipientsText
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
      };
      await updateNotificationSettings(payload);
      setSuccess('Notification settings updated.');
      await loadSettings();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update notification settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="notifications-panel">
      <header className="panel-header">
        <div>
          <h3>🔔 Notifications</h3>
          <span className="notifications-panel__subtitle">Configure email alerts and desktop notifications for system events</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadSettings()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Reload'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}
      {success && <p className="panel-success">{success}</p>}

      <div className="notifications-panel__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Enable email notifications to receive alerts about important system events, 
          revenue milestones, errors, and approval requests. Desktop logs show real-time activity in the dashboard.
        </p>
      </div>

      <form onSubmit={handleSave} className="notifications-form">
        <label>
          <input type="checkbox" checked={settings.desktop_log} onChange={handleToggle('desktop_log')} /> Desktop log notifications
        </label>
        <label>
          <input type="checkbox" checked={settings.email_enabled} onChange={handleToggle('email_enabled')} /> Email notifications
        </label>
        <label>
          Email recipients (comma-separated)
          <textarea
            value={recipientsText}
            onChange={(event) => setRecipientsText(event.target.value)}
            rows={2}
            placeholder="user@example.com,user2@example.com"
            disabled={!settings.email_enabled}
          />
        </label>
        <button type="submit" className="primary-button" disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </form>
    </div>
  );
};
