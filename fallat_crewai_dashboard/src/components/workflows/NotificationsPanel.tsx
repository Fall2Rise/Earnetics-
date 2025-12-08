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

  const loadSettings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getNotificationSettings();
      setSettings(data);
      setRecipientsText((data.email_recipients || []).join(','));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notification settings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  const handleToggle = (key: keyof NotificationSettings) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.checked;
    setSettings((prev) => ({ ...prev, [key]: value }));
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
    <div className="notifications-panel glass-panel">
      <header className="panel-header">
        <div>
          <h3>Notifications</h3>
          <span>Configure email alerts and desktop logs</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadSettings()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Reload'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}
      {success && <p className="panel-success">{success}</p>}

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
