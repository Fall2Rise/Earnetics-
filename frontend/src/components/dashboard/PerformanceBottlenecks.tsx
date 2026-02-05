import React, { useCallback, useEffect, useState } from 'react';
import { API_BASE_URL } from '../../api/config';
import { AlertTriangle, Clock, TrendingDown } from 'lucide-react';

interface Bottleneck {
  id: string;
  component: string;
  severity: 'critical' | 'high' | 'medium';
  description: string;
  impact: string;
  recommendation: string;
  detected_at: string;
}

export const PerformanceBottlenecks: React.FC = () => {
  const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
  const [loading, setLoading] = useState(false);

  const loadBottlenecks = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/bottlenecks?timeframe_hours=24`);
      if (!response.ok) throw new Error('Failed to fetch bottlenecks');
      const data = await response.json();
      
      // Transform backend data to frontend format
      const transformed = (data.bottlenecks || []).map((b: any, idx: number) => ({
        id: b.id || `bottleneck-${idx}`,
        component: b.component || b.name || 'Unknown',
        severity: b.severity || 'medium',
        description: b.description || b.message || 'Performance issue detected',
        impact: b.impact || 'System performance degradation',
        recommendation: b.recommendation || b.suggestion || 'Review and optimize',
        detected_at: b.detected_at || new Date().toISOString()
      }));
      
      setBottlenecks(transformed);
    } catch (err) {
      console.error('Failed to load bottlenecks:', err);
      setBottlenecks([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBottlenecks();
    const interval = setInterval(loadBottlenecks, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [loadBottlenecks]);

  const getSeverityColor = (severity: Bottleneck['severity']) => {
    switch (severity) {
      case 'critical': return 'border-red-500/50 bg-red-900/20';
      case 'high': return 'border-orange-500/50 bg-orange-900/20';
      case 'medium': return 'border-yellow-500/50 bg-yellow-900/20';
    }
  };

  return (
    <div className="performance-bottlenecks">
      <header className="panel-header">
        <div>
          <h3>⚠️ Performance Bottlenecks</h3>
          <span className="text-xs text-slate-400">Detected system performance issues</span>
        </div>
        <button
          type="button"
          className="refresh-button"
          onClick={() => void loadBottlenecks()}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      <div className="bottlenecks-list">
        {bottlenecks.length === 0 ? (
          <p className="panel-empty">No bottlenecks detected. System running smoothly! ✅</p>
        ) : (
          bottlenecks.map((bottleneck) => (
            <div
              key={bottleneck.id}
              className={`bottleneck-card ${getSeverityColor(bottleneck.severity)}`}
            >
              <div className="bottleneck-card__header">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={16} className="text-red-400" />
                  <h4>{bottleneck.component}</h4>
                </div>
                <span className={`badge badge--${bottleneck.severity === 'critical' ? 'error' : bottleneck.severity === 'high' ? 'warn' : 'ok'}`}>
                  {bottleneck.severity}
                </span>
              </div>
              <p className="bottleneck-card__description">{bottleneck.description}</p>
              <div className="bottleneck-card__details">
                <div>
                  <span className="text-xs text-slate-400">Impact:</span>
                  <span className="text-xs text-slate-300 ml-2">{bottleneck.impact}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400">Recommendation:</span>
                  <span className="text-xs text-indigo-300 ml-2">{bottleneck.recommendation}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
