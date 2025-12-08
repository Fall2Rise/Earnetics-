export const toStatusLabel = (status?: string) => {
  if (!status) return 'Unknown';
  const normalized = status.toUpperCase();
  if (normalized === 'OPERATIONAL' || normalized === 'ONLINE' || normalized === 'SUCCESS') {
    return 'Operational';
  }
  if (normalized === 'DEGRADED') {
    return 'Degraded';
  }
  if (normalized === 'OFFLINE' || normalized === 'ERROR' || normalized === 'FAILED') {
    return 'Offline';
  }
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
};

export const toStatusTone = (status?: string) => {
  const normalized = status?.toUpperCase() ?? '';
  if (normalized === 'OPERATIONAL' || normalized === 'ONLINE' || normalized === 'SUCCESS') {
    return 'ok';
  }
  if (normalized === 'DEGRADED' || normalized === 'WARN' || normalized === 'WARNING') {
    return 'warn';
  }
  if (normalized === 'OFFLINE' || normalized === 'ERROR' || normalized === 'FAILED') {
    return 'error';
  }
  return 'idle';
};
