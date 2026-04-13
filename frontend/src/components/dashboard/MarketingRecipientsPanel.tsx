import React, { useState, useEffect } from 'react';
import { campaignApi, Campaign } from '../../api/campaignApi';
import { Mail, MessageCircle, Play, Pause, Plus, Rocket } from 'lucide-react';

export const MarketingRecipientsPanel: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [newCampaignName, setNewCampaignName] = useState('');
  const [newCampaignType, setNewCampaignType] = useState('email');

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const data = await campaignApi.listCampaigns();
      setCampaigns(data.campaigns);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newCampaignName) return;
    try {
      await campaignApi.createCampaign({
        name: newCampaignName,
        type: newCampaignType,
      });
      setNewCampaignName('');
      loadCampaigns();
    } catch (e) {
      console.error(e);
      alert('Failed to create campaign');
    }
  };

  const handleToggleStatus = async (campaign: Campaign) => {
    try {
      if (campaign.status === 'active') {
        await campaignApi.pauseCampaign(campaign.id);
      } else {
        await campaignApi.startCampaign(campaign.id);
      }
      loadCampaigns();
    } catch (e) {
      console.error(e);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'paused': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'completed': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="command-panel h-full flex flex-col">
      <header className="panel-header mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-orange-500/20 rounded-lg border border-orange-500/30">
            <Rocket className="text-orange-400" size={20} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Marketing Campaigns</h3>
            <p className="text-xs text-slate-400">Manage email & social blasts</p>
          </div>
        </div>
      </header>

      {/* Create Controls */}
      <div className="bg-black/20 rounded-xl p-4 mb-4 border border-white/5">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Campaign Name (e.g., 'Winter Sale Blast')"
            className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-orange-500/50 outline-none transition-colors"
            value={newCampaignName}
            onChange={(e) => setNewCampaignName(e.target.value)}
          />
          <select 
            value={newCampaignType} 
            onChange={(e) => setNewCampaignType(e.target.value)}
            className="bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none"
          >
            <option value="email">Email</option>
            <option value="social">Social</option>
          </select>
          <button
            onClick={handleCreate}
            disabled={!newCampaignName}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 rounded-lg border border-orange-500/30 transition-all disabled:opacity-50"
          >
            <Plus size={14} />
            Create
          </button>
        </div>
      </div>

      {/* Campaign List */}
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-2">
        {campaigns.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No campaigns found. Launch one!</div>
        ) : (
          campaigns.map((campaign) => (
            <div key={campaign.id} className="bg-white/5 border border-white/5 rounded-lg p-3 hover:border-orange-500/30 transition-colors flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${campaign.type === 'email' ? 'bg-blue-500/10 text-blue-400' : 'bg-pink-500/10 text-pink-400'}`}>
                  {campaign.type === 'email' ? <Mail size={16} /> : <MessageCircle size={16} />}
                </div>
                <div>
                  <h4 className="text-sm font-medium text-white">{campaign.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getStatusColor(campaign.status)}`}>
                      {campaign.status.toUpperCase()}
                    </span>
                    <span className="text-[10px] text-slate-600">{new Date(campaign.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => handleToggleStatus(campaign)}
                className={`p-2 rounded-full hover:bg-white/10 transition-colors ${campaign.status === 'active' ? 'text-yellow-400' : 'text-green-400'}`}
                title={campaign.status === 'active' ? "Pause Campaign" : "Start Campaign"}
              >
                {campaign.status === 'active' ? <Pause size={16} /> : <Play size={16} />}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
