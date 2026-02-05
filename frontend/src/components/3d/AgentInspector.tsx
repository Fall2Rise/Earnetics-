import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, CheckCircle2 } from 'lucide-react';
import type { Agent } from '../../stores/agentStore';

interface AgentInspectorProps {
  agent: Agent;
  onClose: () => void;
}

export const AgentInspector: React.FC<AgentInspectorProps> = ({ agent, onClose }) => {
  const [command, setCommand] = useState('');
  
  // Defensive check - should never happen due to conditional rendering, but safety first
  if (!agent) {
    return null;
  }

  const handleSendCommand = () => {
    if (command.trim()) {
      // TODO: Send command to backend
      console.log('[AgentInspector] Sending command to', agent.name, ':', command);
      setCommand('');
    }
  };

  const statusColor = agent.status === 'active' ? '#FFD700' : 
                     agent.status === 'idle' ? '#00D4FF' : 
                     agent.status === 'error' ? '#FF4444' : '#888888';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 30 }}
        className="absolute top-24 right-6 z-40 w-[360px]"
      >
        <div
          className="bg-gradient-to-br from-slate-950/95 via-slate-900/90 to-slate-950/95 border border-cyan-500/30 rounded-xl shadow-2xl overflow-hidden"
          style={{ boxShadow: '0 0 45px rgba(0, 214, 255, 0.2)' }}
        >
          <div className="px-4 py-3 border-b border-cyan-500/20 flex items-center justify-between bg-gradient-to-r from-cyan-900/30 to-transparent">
            <div className="text-xs text-cyan-200/60 uppercase tracking-widest">Agent Inspector</div>
            <button
              onClick={onClose}
              className="text-cyan-300 hover:text-cyan-100 transition-colors p-1 hover:bg-cyan-500/20 rounded"
            >
              <X size={16} />
            </button>
          </div>

          <div className="p-4 space-y-3">
            <div className="flex items-center gap-3">
              <div
                className="h-12 w-12 rounded-lg border flex items-center justify-center text-sm font-bold"
                style={{
                  borderColor: `${statusColor}66`,
                  color: statusColor,
                  background: `radial-gradient(circle, ${statusColor}25, transparent)`,
                }}
              >
                {agent.name.slice(0, 2)}
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-white">{agent.name}</div>
                <div className="text-xs text-cyan-200/60">{agent.role}</div>
              </div>
              <span
                className="px-2 py-1 rounded text-[10px] font-bold uppercase"
                style={{
                  background: `${statusColor}25`,
                  color: statusColor,
                  border: `1px solid ${statusColor}55`,
                }}
              >
                {agent.status === 'active' ? 'EXECUTING' : agent.status.toUpperCase()}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div>
                <div className="text-cyan-200/60 uppercase tracking-wider">Current Task</div>
                <div className="text-white/90">{agent.currentTask || 'Awaiting instructions'}</div>
              </div>
              <div>
                <div className="text-cyan-200/60 uppercase tracking-wider">Next Action</div>
                <div className="text-white/80">Optimize workflow</div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-cyan-200/60 uppercase tracking-wider">Inputs</div>
                  <div className="text-white/80">Brief: {agent.department}</div>
                </div>
                <div>
                  <div className="text-cyan-200/60 uppercase tracking-wider">Outputs</div>
                  <div className="text-white/80">Drafts: {agent.name}_v2.md</div>
                </div>
              </div>
              <div>
                <div className="text-cyan-200/60 uppercase tracking-wider">Dependencies</div>
                <div className="text-white/80">Awaiting: {agent.department}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="text-cyan-200/60 uppercase tracking-wider">Confidence</div>
                <span className="text-emerald-300 font-semibold">High</span>
              </div>
            </div>

            <div className="pt-3 border-t border-cyan-500/15">
              <div className="text-cyan-200/60 uppercase tracking-wider text-xs">Command</div>
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendCommand()}
                  placeholder="Adjust tone of the intro..."
                  className="flex-1 px-3 py-2 bg-slate-900/70 border border-cyan-500/20 rounded-lg text-sm text-white placeholder-cyan-500/40 focus:outline-none focus:border-cyan-400/60"
                />
                <button
                  onClick={handleSendCommand}
                  className="px-4 py-2 bg-cyan-500/30 border border-cyan-400/40 text-white text-xs font-semibold rounded-lg hover:bg-cyan-500/40 transition-colors"
                >
                  SEND
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
