export interface PerformanceMetric {
  id: string;
  label: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  change: number;
}
