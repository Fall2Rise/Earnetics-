import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { API_BASE_URL } from '../../api/config';

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  category: string | null;
  type: string;
  interval: string | null;
  development_status: string;
  launch_date: string | null;
  revenue_generated: number;
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: string;
  title: string;
  department: string;
  priority: string;
  status: string;
  description: string | null;
  assigned_agent: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface Customer {
  email: string;
  transaction_count: number;
  total_spent: number;
  last_purchase: string;
}

interface MetricDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  metricType: 'products' | 'workflows' | 'customers' | 'revenue' | 'directives';
  title: string;
}

export const MetricDetailModal: React.FC<MetricDetailModalProps> = ({
  isOpen,
  onClose,
  metricType,
  title,
}) => {
  const [data, setData] = useState<Product[] | Workflow[] | Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        let url = '';
        if (metricType === 'products') {
          url = `${API_BASE_URL || ''}/api/products/list`;
        } else if (metricType === 'workflows') {
          url = `${API_BASE_URL || ''}/api/workflows/pending`;
        } else if (metricType === 'customers') {
          url = `${API_BASE_URL || ''}/api/customers/list`;
        } else {
          setError('Unsupported metric type');
          setLoading(false);
          return;
        }

        const response = await fetch(url, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Failed to fetch ${metricType}: ${response.status} ${errorText}`);
        }

        const result = await response.json();
        
        // Handle workflows response
        if (metricType === 'workflows') {
          // Check if result has workflows array or if it's the array directly
          if (Array.isArray(result)) {
            setData(result);
          } else if (result.workflows && Array.isArray(result.workflows)) {
            setData(result.workflows);
          } else if (result.error) {
            throw new Error(result.error);
          } else {
            setData([]);
          }
        } else if (metricType === 'products') {
          setData(result.products || []);
        } else if (metricType === 'customers') {
          setData(result.customers || []);
        }
      } catch (err) {
        console.error(`Error fetching ${metricType}:`, err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setData([]); // Set empty array on error to prevent crashes
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isOpen, metricType]);

  if (!isOpen) return null;

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-slate-900 border border-cyan-500/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-cyan-500/20 bg-slate-800/50">
          <h2 className="text-2xl font-bold text-cyan-400">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
              {error}
            </div>
          )}

          {!loading && !error && data.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <p>No {metricType} found.</p>
            </div>
          )}

          {!loading && !error && data.length > 0 && (
            <div className="space-y-4">
              {metricType === 'products' && (
                <div className="grid gap-4">
                  {(data as Product[]).map((product) => (
                    <div
                      key={product.id}
                      className="p-4 bg-slate-800/50 border border-cyan-500/20 rounded-lg hover:border-cyan-500/40 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-lg font-semibold text-white">{product.name}</h3>
                        <span className="text-cyan-400 font-bold">{formatCurrency(product.price)}</span>
                      </div>
                      {product.description && (
                        <p className="text-gray-300 text-sm mb-3">{product.description}</p>
                      )}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500">Category:</span>
                          <span className="ml-2 text-white">{product.category || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Type:</span>
                          <span className="ml-2 text-white">{product.type}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Status:</span>
                          <span className="ml-2 text-emerald-400">{product.development_status}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Revenue:</span>
                          <span className="ml-2 text-emerald-400">
                            {formatCurrency(product.revenue_generated)}
                          </span>
                        </div>
                        {product.launch_date && (
                          <div>
                            <span className="text-gray-500">Launched:</span>
                            <span className="ml-2 text-white">{formatDate(product.launch_date)}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-500">Created:</span>
                          <span className="ml-2 text-white">{formatDate(product.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {metricType === 'workflows' && (
                <div className="grid gap-4">
                  {(data as Workflow[]).map((workflow) => (
                    <div
                      key={workflow.id}
                      className="p-4 bg-slate-800/50 border border-cyan-500/20 rounded-lg hover:border-cyan-500/40 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-lg font-semibold text-white">{workflow.title}</h3>
                        <span
                          className={`px-2 py-1 rounded text-xs font-bold ${
                            workflow.priority === 'critical'
                              ? 'bg-red-500/20 text-red-400'
                              : workflow.priority === 'high'
                              ? 'bg-orange-500/20 text-orange-400'
                              : workflow.priority === 'medium'
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}
                        >
                          {workflow.priority.toUpperCase()}
                        </span>
                      </div>
                      {workflow.description && (
                        <p className="text-gray-300 text-sm mb-3">{workflow.description}</p>
                      )}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500">Department:</span>
                          <span className="ml-2 text-white">{workflow.department}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Status:</span>
                          <span className="ml-2 text-cyan-400">{workflow.status}</span>
                        </div>
                        {workflow.assigned_agent && (
                          <div>
                            <span className="text-gray-500">Agent:</span>
                            <span className="ml-2 text-white">{workflow.assigned_agent}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-500">Created:</span>
                          <span className="ml-2 text-white">{formatDate(workflow.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {metricType === 'customers' && (
                <div className="grid gap-4">
                  {(data as Customer[]).map((customer, index) => (
                    <div
                      key={customer.email || index}
                      className="p-4 bg-slate-800/50 border border-cyan-500/20 rounded-lg hover:border-cyan-500/40 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-lg font-semibold text-white">{customer.email}</h3>
                        <span className="text-emerald-400 font-bold">
                          {formatCurrency(customer.total_spent)}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500">Transactions:</span>
                          <span className="ml-2 text-white">{customer.transaction_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Total Spent:</span>
                          <span className="ml-2 text-emerald-400">
                            {formatCurrency(customer.total_spent)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">Last Purchase:</span>
                          <span className="ml-2 text-white">{formatDate(customer.last_purchase)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-cyan-500/20 bg-slate-800/50">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>Total: {data.length} {metricType}</span>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

