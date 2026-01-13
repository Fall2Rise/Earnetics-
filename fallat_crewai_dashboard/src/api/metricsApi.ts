import { API_BASE_URL } from './config';

export interface Metric {
  id: string;
  label: string;
  value: string;
  trend: string;
}

export interface MetricsResult {
  metrics: Metric[];
  overviewStatus: string;
  progressPercentage: number;
  updatedAt?: string;
  totalRequests?: number;
  errorMessage?: string;
}

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);

export const getMetrics = async (): Promise<MetricsResult> => {
  // Debug logging removed to reduce request spam
  try {
    const url = `${API_BASE_URL}/api/system_status`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    // Debug logging removed to reduce request spam
    if (!response.ok) {
      throw new Error(`Failed to fetch system status: ${response.status}`);
    }

    const data = await response.json();
    // Debug logging removed to reduce request spam
    const overview = data?.system_health?.system_overview ?? {};
    const metrics = overview?.performance_metrics ?? {};

    const totalRevenue = Number(metrics.total_revenue ?? 0);
    const monthlyTarget = Number(metrics.monthly_target ?? 0);
    const activeCustomers = Number(metrics.active_customers ?? 0);
    const productsCreated = Number(metrics.products_created ?? 0);
    const directivesExecuted = Number(metrics.directives_executed ?? 0);
    const progress = monthlyTarget > 0 ? Math.min(100, (totalRevenue / monthlyTarget) * 100) : 0;

    const metricsList: Metric[] = [
      {
        id: 'total_revenue',
        label: 'Total Revenue',
        value: formatCurrency(totalRevenue),
        trend:
          monthlyTarget > 0 && totalRevenue > 0
            ? `${progress.toFixed(1)}% of target`
            : 'Launch your first offer',
      },
      {
        id: 'monthly_target',
        label: 'Monthly Target',
        value: formatCurrency(monthlyTarget || 150000),
        trend: progress > 0 ? 'Target tracking live' : 'Configured by CFO',
      },
      {
        id: 'active_customers',
        label: 'Active Customers',
        value: activeCustomers.toString(),
        trend: activeCustomers ? 'Accounts engaged' : 'Pipeline forming',
      },
      {
        id: 'products_created',
        label: 'Products Live',
        value: productsCreated.toString(),
        trend: productsCreated ? 'Portfolio expanding' : 'Ready to launch',
      },
      {
        id: 'directives_executed',
        label: 'Directives Executed',
        value: directivesExecuted.toString(),
        trend: directivesExecuted ? 'Automation cycling' : 'Standing by',
      },
    ];

    return {
      metrics: metricsList,
      overviewStatus: overview?.status ?? data?.status ?? 'ONLINE',
      progressPercentage: progress,
      updatedAt: metrics?.last_updated ?? data?.timestamp,
      totalRequests: data?.app_state?.total_requests,
    };
  } catch (error) {
    console.error('Failed to fetch metrics:', error);
    // Don't show OFFLINE on timeout - show a retry message instead
    const errorMessage = error instanceof Error 
      ? (error.name === 'AbortError' ? 'Connection timeout - retrying...' : error.message)
      : 'Unknown error loading metrics';
    
    const fallback: MetricsResult = {
      metrics: [
        { id: 'total_revenue', label: 'Total Revenue', value: '$0.00', trend: 'Awaiting launch' },
        { id: 'monthly_target', label: 'Monthly Target', value: '$150,000.00', trend: 'Configured by CFO' },
        { id: 'active_customers', label: 'Active Customers', value: '0', trend: 'Pipeline forming' },
        { id: 'products_created', label: 'Products Live', value: '0', trend: 'Ready to launch' },
        { id: 'directives_executed', label: 'Directives Executed', value: '0', trend: 'Standing by' },
      ],
      overviewStatus: 'CONNECTING', // Changed from OFFLINE to CONNECTING
      progressPercentage: 0,
      errorMessage: errorMessage,
    };

    return fallback;
  }
};
