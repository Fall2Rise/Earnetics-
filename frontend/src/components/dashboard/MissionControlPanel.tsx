import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FinancialDashboard } from './FinancialDashboard';
import { ContentEnginePanel } from './ContentEnginePanel';
import { IntegrationsPanel } from './IntegrationsPanel';
import { IntelligencePanel } from './IntelligencePanel';
import { LeadManagementPanel } from './LeadManagementPanel';
import { AuditLogPanel } from '../workflows/AuditLogPanel';
import { SecurityPanel } from './SecurityPanel';
import { EvolutionView } from './EvolutionView';
import { DirectiveCorePanel } from './DirectiveCorePanel';
import { OpportunityBacklogKanban } from './OpportunityBacklogKanban';

interface MissionControlPanelProps {
  onClose: () => void;
}

type TabId = 
  | 'financial' 
  | 'content' 
  | 'integrations' 
  | 'intelligence' 
  | 'leads' 
  | 'audit' 
  | 'security'
  | 'evolution'
  | 'directives'
  | 'opportunities';

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'financial', label: 'Financial', icon: '💰' },
  { id: 'content', label: 'Content Engine', icon: '📝' },
  { id: 'leads', label: 'Lead Gen', icon: '🎯' },
  { id: 'opportunities', label: 'Strategy', icon: '💡' },
  { id: 'directives', label: 'Directives', icon: '⚡' },
  { id: 'intelligence', label: 'Intelligence', icon: '🧠' },
  { id: 'evolution', label: 'Evolution', icon: '🧬' },
  { id: 'integrations', label: 'Integrations', icon: '🔌' },
  { id: 'security', label: 'Security', icon: '🔒' },
  { id: 'audit', label: 'Audit Log', icon: '📋' },
];

export const MissionControlPanel: React.FC<MissionControlPanelProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<TabId>('financial');

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/80 backdrop-blur-md"
    >
      <div className="w-full h-full max-w-7xl bg-slate-900 border border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-500/20 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-cyan-500/30 bg-slate-900/50">
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
            <h2 className="text-2xl font-bold text-white tracking-wide">
              MISSION CONTROL <span className="text-cyan-400">NEXUS</span>
            </h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-full transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>

        {/* Layout */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar Navigation */}
          <div className="w-64 bg-slate-950/50 border-r border-cyan-500/20 overflow-y-auto">
            <div className="p-4 space-y-2">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    activeTab === tab.id 
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(34,211,238,0.1)]' 
                      : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 overflow-y-auto bg-slate-900 relative">
            <div className="p-6 h-full">
              {activeTab === 'financial' && <FinancialDashboard />}
              {activeTab === 'content' && <ContentEnginePanel />}
              {activeTab === 'integrations' && <IntegrationsPanel />}
              {activeTab === 'intelligence' && <IntelligencePanel />}
              {activeTab === 'leads' && <LeadManagementPanel />}
              {activeTab === 'audit' && <AuditLogPanel />}
              {activeTab === 'security' && <SecurityPanel />}
              {activeTab === 'evolution' && <EvolutionView />}
              {activeTab === 'directives' && <DirectiveCorePanel />}
              {activeTab === 'opportunities' && <OpportunityBacklogKanban />}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
