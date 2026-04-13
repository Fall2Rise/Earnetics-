import React, { useState, useEffect } from 'react';
import { contentEngineApi, ContentAsset } from '../../api/contentEngineApi';
import { FileText, Plus, RefreshCw, Type, Twitter, Video } from 'lucide-react';

export const ContentEnginePanel: React.FC = () => {
  const [assets, setAssets] = useState<ContentAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('viral');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    setLoading(true);
    try {
      const data = await contentEngineApi.listContent();
      setAssets(data.assets);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!topic) return;
    setGenerating(true);
    try {
      await contentEngineApi.generateMaster(topic, tone);
      setTopic('');
      await loadContent();
    } catch (e) {
      console.error(e);
      alert("Failed to generate content");
    } finally {
      setGenerating(false);
    }
  };

  const getIcon = (type: string) => {
    if (type.includes('video') || type.includes('script')) return <Video size={16} className="text-pink-400" />;
    if (type.includes('social')) return <Twitter size={16} className="text-blue-400" />;
    return <FileText size={16} className="text-emerald-400" />;
  };

  return (
    <div className="command-panel h-full flex flex-col">
      <header className="panel-header mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/20 rounded-lg border border-emerald-500/30">
            <Type className="text-emerald-400" size={20} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Content Engine</h3>
            <p className="text-xs text-slate-400">Generate and manage creative assets</p>
          </div>
        </div>
        <button 
          onClick={loadContent}
          className="p-2 hover:bg-white/10 rounded-lg text-slate-400 transition-colors"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </header>

      {/* Generation Controls */}
      <div className="bg-black/20 rounded-xl p-4 mb-4 border border-white/5">
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            placeholder="Enter topic (e.g., 'Future of AI Revenue')"
            className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-500/50 outline-none transition-colors"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
          <select 
            value={tone} 
            onChange={(e) => setTone(e.target.value)}
            className="bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none"
          >
            <option value="viral">Viral</option>
            <option value="professional">Professional</option>
            <option value="educational">Educational</option>
          </select>
          <button
            onClick={handleGenerate}
            disabled={generating || !topic}
            className={`flex items-center gap-2 px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg border border-emerald-500/30 transition-all ${generating ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {generating ? <RefreshCw size={14} className="animate-spin" /> : <Plus size={14} />}
            Generate
          </button>
        </div>
      </div>

      {/* Content List */}
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-2">
        {assets.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No content assets found. Start generating!</div>
        ) : (
          assets.map((asset) => (
            <div key={asset.id} className="bg-white/5 border border-white/5 rounded-lg p-3 hover:border-emerald-500/30 transition-colors group">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="mt-1">{getIcon(asset.type)}</div>
                  <div>
                    <h4 className="text-sm font-medium text-white group-hover:text-emerald-300 transition-colors">{asset.title}</h4>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{asset.content}</p>
                    <div className="flex gap-2 mt-2">
                      <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-slate-400 uppercase tracking-wide">{asset.type}</span>
                      <span className="text-[10px] text-slate-600">{new Date(asset.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${asset.status === 'published' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
                    {asset.status}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
