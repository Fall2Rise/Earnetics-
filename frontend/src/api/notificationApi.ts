import { API_BASE_URL } from './config';

export interface NotificationSettings {
  email_enabled: boolean;
  email_recipients: string[];
  desktop_log: boolean;
}

export const getNotificationSettings = async (signal?: AbortSignal): Promise<NotificationSettings> => {
  const response = await fetch(`${API_BASE_URL}/api/notifications/settings`, { signal });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
};

export const updateNotificationSettings = async (settings: NotificationSettings): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/notifications/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
};
