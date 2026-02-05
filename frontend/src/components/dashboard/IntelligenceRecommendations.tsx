import React, { useCallback, useState } from 'react';
import { AlertTriangle, TrendingUp, Lightbulb, Target, Zap } from 'lucide-react';

interface Recommendation {
  id: string;
  type: 'opportunity' | 'action' | 'optimization' | 'alert';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  action?: string;
  source: string;
}

export const IntelligenceRecommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      setRecommendations([]);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getIcon = (type: Recommendation['type']) => {
    switch (type) {
      case 'opportunity': return <TrendingUp size={16} />;
      case 'action': return <Target size={16} />;
      case 'optimization': return <Zap size={16} />;
      case 'alert': return <AlertTriangle size={16} />;
      default: return <Lightbulb size={16} />;
    }
  };

  const getPriorityColor = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'high': return 'border-red-500/30 bg-red-900/10';
      case 'medium': return 'border-yellow-500/30 bg-yellow-900/10';
      case 'low': return 'border-blue-500/30 bg-blue-900/10';
    }
  };

  return (
    <div className="intelligence-recommendations">
      <header className="panel-header">
        <div>
          <h3>💡 Strategic Recommendations</h3>
          <span className="text-xs text-slate-400">AI-powered insights and action items</span>
        </div>
        <button
          type="button"
          className="refresh-button"
          onClick={() => void loadRecommendations()}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      <div className="recommendations-list">
        {recommendations.length === 0 ? (
          <p className="panel-empty">No recommendations available (no feed configured).</p>
        ) : (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className={`recommendation-card ${getPriorityColor(rec.priority)}`}
            >
              <div className="recommendation-card__header">
                <div className="flex items-center gap-2">
                  {getIcon(rec.type)}
                  <h4>{rec.title}</h4>
                </div>
                <span className={`badge badge--${rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warn' : 'ok'}`}>
                  {rec.priority}
                </span>
              </div>
              <p className="recommendation-card__description">{rec.description}</p>
              <div className="recommendation-card__footer">
                <span className="text-xs text-slate-400">Impact: {rec.impact}</span>
                {rec.action && (
                  <button className="text-xs text-indigo-400 hover:text-indigo-300">
                    {rec.action} →
                  </button>
                )}
                <span className="text-xs text-slate-500">Source: {rec.source}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
