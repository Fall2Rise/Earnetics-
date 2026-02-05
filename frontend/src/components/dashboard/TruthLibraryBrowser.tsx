import React, { useCallback, useEffect, useState } from 'react';
import { listTruthLibrary, getTruthAsset, TruthLibraryAsset } from '../../api/intelligenceApi';
import { motion } from 'framer-motion';
import { BookOpen, Search, Filter, CheckCircle, FileText, Play, Target, FlaskConical } from 'lucide-react';

type AssetType = 'All' | 'reference' | 'sop' | 'playbook' | 'strategy' | 'experiment';
type AssetStatus = 'All' | 'draft' | 'validated' | 'deprecated';

const ASSET_TYPE_ICONS: Record<string, React.ElementType> = {
  reference: FileText,
  sop: FileText,
  playbook: Play,
  strategy: Target,
  experiment: FlaskConical,
};

export const TruthLibraryBrowser: React.FC = () => {
  const [assets, setAssets] = useState<TruthLibraryAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [assetType, setAssetType] = useState<AssetType>('All');
  const [status, setStatus] = useState<AssetStatus>('All');
  const [selectedAsset, setSelectedAsset] = useState<TruthLibraryAsset | null>(null);

  const loadAssets = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listTruthLibrary(
        searchTerm || undefined,
        assetType !== 'All' ? assetType : undefined,
        status !== 'All' ? status : undefined,
        50,
        abortSignal
      );
      if (abortSignal?.aborted) return;
      setAssets(data.assets);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return;
      setError(err instanceof Error ? err.message : 'Failed to load assets');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [searchTerm, assetType, status]);

  useEffect(() => {
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => {
      void loadAssets(abortController.signal);
    }, 300);
    return () => {
      clearTimeout(timeoutId);
      abortController.abort();
    };
  }, [loadAssets]);

  const handleAssetClick = async (assetId: string) => {
    try {
      const asset = await getTruthAsset(assetId);
      setSelectedAsset(asset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load asset details');
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'validated') return 'text-emerald-400 border-emerald-500/30 bg-emerald-900/20';
    if (status === 'deprecated') return 'text-slate-400 border-slate-500/30 bg-slate-900/20';
    return 'text-yellow-400 border-yellow-500/30 bg-yellow-900/20';
  };

  return (
    <section className="truth-library-browser">
      <header className="panel-header">
        <div>
          <h3>📚 Truth Library</h3>
          <span className="truth-library-browser__subtitle">Validated playbooks, SOPs, strategies, and experiments</span>
        </div>
        <div className="panel-header__actions">
          <button
            type="button"
            className="refresh-button"
            onClick={() => void loadAssets()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="truth-library-browser__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> The Truth Library contains validated knowledge assets that agents use for operations.
          Only validated assets are used in production. Draft assets are works in progress.
        </p>
      </div>

      <div className="truth-library-filters">
        <div className="search-input">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            placeholder="Search Truth Library..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="category-filter">
          <Filter size={16} className="text-slate-400" />
          <select value={assetType} onChange={(e) => setAssetType(e.target.value as AssetType)}>
            <option value="All">All Types</option>
            <option value="reference">Reference</option>
            <option value="sop">SOP</option>
            <option value="playbook">Playbook</option>
            <option value="strategy">Strategy</option>
            <option value="experiment">Experiment</option>
          </select>
        </div>
        <div className="category-filter">
          <select value={status} onChange={(e) => setStatus(e.target.value as AssetStatus)}>
            <option value="All">All Status</option>
            <option value="validated">Validated</option>
            <option value="draft">Draft</option>
            <option value="deprecated">Deprecated</option>
          </select>
        </div>
      </div>

      <div className="truth-library-list">
        {loading && <p className="panel-loading">Loading assets...</p>}
        {!loading && assets.length === 0 && (
          <p className="panel-empty">No assets found for the current filters.</p>
        )}

        {assets.map((asset) => {
          const Icon = ASSET_TYPE_ICONS[asset.type] || FileText;
          return (
            <motion.div
              key={asset.asset_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`truth-asset-card ${getStatusColor(asset.status)}`}
              onClick={() => void handleAssetClick(asset.asset_id)}
            >
              <div className="truth-asset-card__header">
                <Icon size={20} className="text-indigo-400" />
                <div>
                  <h4>{asset.title}</h4>
                  <span className="text-xs text-slate-400">{asset.type} • v{asset.version}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className={`status-pill status-pill--${asset.status === 'validated' ? 'success' : asset.status === 'deprecated' ? 'warning' : 'info'}`}>
                  {asset.status}
                </span>
                <span className="text-xs text-slate-400">Confidence: {Math.round(asset.confidence * 100)}%</span>
              </div>
              {asset.tags && asset.tags.length > 0 && (
                <div className="truth-asset-card__tags">
                  {asset.tags.slice(0, 5).map((tag) => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              )}
              {asset.measurable_results && (
                <div className="truth-asset-card__results">
                  <strong>Results:</strong> {JSON.stringify(asset.measurable_results, null, 2).substring(0, 100)}...
                </div>
              )}
              <footer className="truth-asset-card__footer">
                <span className="text-xs text-slate-500">Owner: {asset.owner}</span>
                <span className="text-xs text-slate-500">
                  {new Date(asset.updated_at).toLocaleString()}
                </span>
              </footer>
            </motion.div>
          );
        })}
      </div>

      {selectedAsset && (
        <div className="modal-overlay" onClick={() => setSelectedAsset(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedAsset.title}</h3>
              <button onClick={() => setSelectedAsset(null)}>×</button>
            </div>
            <div className="modal-body">
              <pre>{JSON.stringify(selectedAsset.content, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
