// Combine all 3 panels into one "Agent Headquarters"
import React, { useState } from 'react';
import { AgentsPanel } from '../dashboard/AgentsPanel';
import { AgentNexusPanel } from '../dashboard/AgentNexusPanel';
import { AgentDnaRegistryPanel } from '../dashboard/AgentDnaRegistryPanel';
import { AgentInspector } from '../3d/AgentInspector';
import type { Agent } from '../../stores/agentStore';

export const AgentManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roster' | 'nexus' | 'dna'>('roster');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const handleAgentSelect = (agent: any) => {
    // Normalize agent data structure if needed since AgentsPanel uses a different type locally
    const normalizedAgent: Agent = {
      id: agent.id || agent.name,
      name: agent.name,
      role: agent.role,
      department: agent.division || agent.department || 'Unassigned',
      status: agent.status || 'active',
      currentTask: agent.currentTask,
      division: agent.division,
      performance: agent.performance || 95,
      memoryEntries: agent.memoryEntries || 0
    };
    setSelectedAgent(normalizedAgent);
  };

  return (
    <div className="agent-manager glass-panel flex flex-col h-full relative">
      <header className="panel-header border-b border-white/5 pb-4">
        <div>
          <h3 className="text-xl text-white">Agent Headquarters</h3>
          <p className="text-sm text-slate-300">Command, Control, and Configuration</p>
        </div>
        <div className="flex gap-2">
          <button 
            className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'roster' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:bg-white/5'}`}
            onClick={() => setActiveTab('roster')}
          >
            Roster
          </button>
          <button 
            className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'nexus' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:bg-white/5'}`}
            onClick={() => setActiveTab('nexus')}
          >
            Nexus (Live)
          </button>
          <button 
            className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'dna' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:bg-white/5'}`}
            onClick={() => setActiveTab('dna')}
          >
            DNA Registry
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto mt-4">
        {activeTab === 'roster' && <AgentsPanel onSelectAgent={handleAgentSelect} />}
        {activeTab === 'nexus' && <AgentNexusPanel onSelectAgent={handleAgentSelect} />}
        {activeTab === 'dna' && <AgentDnaRegistryPanel />}
      </div>

      {selectedAgent && (
        <AgentInspector 
          agent={selectedAgent} 
          onClose={() => setSelectedAgent(null)} 
        />
      )}
    </div>
  );
};

