import React, { useState, useEffect } from 'react';
import { revenueLoopsApi, RevenueCycle } from '../../api/revenueLoopsApi';
import { Activity, Play, Settings, Trash2, DollarSign, CheckCircle, AlertTriangle } from 'lucide-react';

export const RevenueLoopsPanel: React.FC = () => {
  const [cycles, setCycles] = useState<RevenueCycle[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCycle, setSelectedCycle] = useState<RevenueCycle | null>(null);
  const [injecting, setInjecting] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await revenueLoopsApi.getHistory();
      setCycles(data.cycles);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const runNewLoop = async () => {
    setLoading(true);
    try {
      await revenueLoopsApi.runLoop({ focus: 'autonomous_growth' });
      await loadHistory();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const injectTools = async () => {
    setInjecting(true);
    try {
      await revenueLoopsApi.injectTools(['stripe.create_product', 'email.send_campaign', 'scrape.website']);
      alert("Tools Injected: Stripe, Email, Scraping enabled for Revenue Loop agents.");
    } catch (e) {
      console.error(e);
      alert("Failed to inject tools.");
    } finally {
      setInjecting(false);
    }
  };

  // Helper to determine status color
  const getStatusColor = (cycle: RevenueCycle) => {
    const report = cycle.revenue_play_report || {};
    const potential = report.estimated_revenue || 0;
    if (potential > 5000) return 'text-emerald-400';
    if (potential > 0) return 'text-yellow-400';
    return 'text-slate-400';
  };

  // Helper to filter "Tossed" loops (earning potential < half of target? or just low)
  // User said "tossed out if the earning potential is less thatn half"
  // Let's assume a target of $10k, so < $5k is "Tossed/Warning"
  const isTossed = (cycle: RevenueCycle) => {
    const report = cycle.revenue_play_report || {};
    const potential = report.estimated_revenue || 0;
    return potential < 5000 && potential > 0; // arbitrary threshold based on user prompt
  };

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      <header className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="text-cyan-400" />
            Revenue Loops
          </h2>
          <p className="text-slate-400 text-sm">Autonomous revenue generation cycles.</p>
        </div>
        <div className="flex gap-2">
            <button 
                onClick={injectTools}
                disabled={injecting}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-300 rounded-lg hover:bg-purple-500/30 border border-purple-500/30 transition-all"
            >
                <Settings size={16} />
                {injecting ? 'Injecting...' : 'Inject Tools'}
            </button>
            <button 
                onClick={runNewLoop}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 text-cyan-300 rounded-lg hover:bg-cyan-500/30 border border-cyan-500/30 transition-all shadow-[0_0_15px_rgba(6,182,212,0.2)]"
            >
                <Play size={16} />
                Start New Loop
            </button>
        </div>
      </header>

      <div className="flex gap-6 flex-1 min-h-0">
        {/* List of Loops */}
        <div className="w-1/3 overflow-y-auto pr-2 space-y-3">
          {cycles.length === 0 && !loading && (
            <div className="text-slate-500 text-center py-8">No revenue loops recorded.</div>
          )}
          
          {cycles.map(cycle => {
            const report = cycle.revenue_play_report || {};
            const title = report.play_name || cycle.validated_opportunity?.title || `Loop ${cycle.id.slice(0, 8)}`;
            const potential = report.estimated_revenue;
            
            return (
              <div 
                key={cycle.id}
                onClick={() => setSelectedCycle(cycle)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedCycle?.id === cycle.id 
                    ? 'bg-white/10 border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.1)]' 
                    : 'bg-black/20 border-white/5 hover:bg-white/5'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-white truncate w-3/4">{title}</span>
                  {isTossed(cycle) && <Trash2 size={14} className="text-rose-400" />}
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">{new Date(cycle.created_at).toLocaleDateString()}</span>
                  <span className={`font-mono ${getStatusColor(cycle)}`}>
                    {potential ? `$${potential.toLocaleString()}` : 'Calculating...'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detail View */}
        <div className="flex-1 bg-black/20 rounded-xl border border-white/5 p-6 overflow-y-auto">
          {selectedCycle ? (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                 <div>
                    <h3 className="text-xl text-white font-bold mb-1">
                        {selectedCycle.revenue_play_report?.play_name || "Revenue Loop Analysis"}
                    </h3>
                    <p className="text-slate-400 font-mono text-xs uppercase tracking-wider">
                        ID: {selectedCycle.id}
                    </p>
                 </div>
                 <div className="text-right">
                    <div className="text-sm text-slate-400">Earning Potential</div>
                    <div className="text-2xl text-emerald-400 font-bold font-mono">
                        ${selectedCycle.revenue_play_report?.estimated_revenue?.toLocaleString() || "0"}
                    </div>
                 </div>
              </div>

              {/* Loop Stages Visualization */}
              <div className="grid grid-cols-4 gap-4">
                 <StageCard 
                    label="Strategy" 
                    status={selectedCycle.product_roadmap ? 'complete' : 'pending'} 
                    data={selectedCycle.product_roadmap}
                 />
                 <StageCard 
                    label="Research" 
                    status={selectedCycle.validated_opportunity ? 'complete' : 'pending'} 
                    data={selectedCycle.validated_opportunity}
                 />
                 <StageCard 
                    label="Build" 
                    status={selectedCycle.automation_module_spec ? 'complete' : 'pending'} 
                    data={selectedCycle.automation_module_spec}
                 />
                 <StageCard 
                    label="Launch" 
                    status={selectedCycle.revenue_play_report ? 'complete' : 'pending'} 
                    data={selectedCycle.revenue_play_report}
                 />
              </div>

              {/* Deep Dive Data */}
              <div className="space-y-4">
                <div className="p-4 bg-white/5 rounded-lg border border-white/5">
                    <h4 className="text-sm font-bold text-cyan-300 mb-2 uppercase tracking-wide">Market Context</h4>
                    <pre className="text-xs text-slate-300 overflow-x-auto">
                        {JSON.stringify(selectedCycle.market_context, null, 2)}
                    </pre>
                </div>

                {selectedCycle.validated_opportunity && (
                    <div className="p-4 bg-white/5 rounded-lg border border-white/5">
                        <h4 className="text-sm font-bold text-cyan-300 mb-2 uppercase tracking-wide">Validated Opportunity</h4>
                        <div className="text-sm text-slate-200">
                            {selectedCycle.validated_opportunity.description || "No description provided."}
                        </div>
                    </div>
                )}
                
                {selectedCycle.revenue_play_report?.tactics && (
                     <div className="p-4 bg-white/5 rounded-lg border border-white/5">
                        <h4 className="text-sm font-bold text-cyan-300 mb-2 uppercase tracking-wide">Execution Tactics</h4>
                        <ul className="list-disc list-inside text-sm text-slate-300 space-y-1">
                            {selectedCycle.revenue_play_report.tactics.map((t: any, i: number) => (
                                <li key={i}>{t}</li>
                            ))}
                        </ul>
                    </div>
                )}
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
                <Activity size={48} className="mb-4 opacity-20" />
                <p>Select a revenue loop to inspect details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const StageCard: React.FC<{ label: string; status: 'complete' | 'pending' | 'error'; data: any }> = ({ label, status, data }) => (
    <div className={`p-3 rounded-lg border ${status === 'complete' ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-white/5 border-white/5'}`}>
        <div className="flex items-center gap-2 mb-2">
            {status === 'complete' ? <CheckCircle size={14} className="text-emerald-400" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-600" />}
            <span className={`text-xs font-bold uppercase ${status === 'complete' ? 'text-emerald-300' : 'text-slate-500'}`}>{label}</span>
        </div>
        <div className="text-xs text-slate-400 truncate">
            {status === 'complete' ? (Object.keys(data).length + " items") : "Waiting..."}
        </div>
    </div>
);
