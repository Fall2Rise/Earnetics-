// Agent Inspector - Live Active Window View
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Eye, Terminal, Activity, Zap, Cpu } from 'lucide-react';
import type { Agent } from '../../stores/agentStore';
import { useAgentStore } from '../../stores/agentStore';

interface AgentInspectorProps {
  agent: Agent;
  onClose: () => void;
}

export const AgentInspector: React.FC<AgentInspectorProps> = ({ agent, onClose }) => {
  const [command, setCommand] = useState('');
  const [activeView, setActiveView] = useState<'live' | 'logs' | 'thought'>('live');
  const [logs, setLogs] = useState<string[]>([]);
  const [activeTask, setActiveTask] = useState<string>('Idle - Monitoring System');
  const [currentThought, setCurrentThought] = useState<string>('Agent is awaiting next operational cycle.');
  const [contextTags, setContextTags] = useState<string[]>(['System Monitoring', 'Idle']);

  const { socket } = useAgentStore();

  // Defensive check
  if (!agent) {
    return null;
  }

  // Subscribe to Real-Time WebSocket Events
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        const payload = data.payload || data;

        // Filter events for this specific agent
        // Handle direct matches or loose matches (e.g. "Nova" vs "nova_agent")
        const eventAgent = payload.agent || payload.agent_name;
        if (!eventAgent || !eventAgent.toLowerCase().includes(agent.name.toLowerCase())) {
          return;
        }

        const timestamp = new Date().toLocaleTimeString();
        let logMessage = '';

        // Handle different event types
        if (data.type === 'AUDIT_LOG' || data.type === 'audit_event') {
          if (payload.action === 'agent_thinking') {
             logMessage = `[THOUGHT] ${payload.message}`;
             setCurrentThought(payload.message.replace('Thinking about: ', ''));
             if (payload.details?.data) {
                 setContextTags(Object.keys(payload.details.data));
             }
          } else if (payload.action === 'agent_phase') {
             logMessage = `[PHASE] ${payload.message} (${payload.status})`;
             setActiveTask(payload.message);
          } else if (payload.action === 'agent_tool_use') {
             logMessage = `[TOOL] ${payload.message}`;
          } else {
             logMessage = `[${payload.action.toUpperCase()}] ${payload.message || JSON.stringify(payload.details)}`;
          }
        } else {
          // Fallback for generic events
          logMessage = `[EVENT] ${payload.message || JSON.stringify(payload)}`;
        }

        if (logMessage) {
            setLogs(prev => [...prev.slice(-19), `[${timestamp}] ${logMessage}`]);
        }

      } catch (err) {
        console.error('Failed to parse inspector event:', err);
      }
    };

    socket.addEventListener('message', handleMessage);
    
    // Initial connection message
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Connected to neural link for ${agent.name}...`]);

    return () => {
        socket.removeEventListener('message', handleMessage);
    };
  }, [socket, agent.name]);

  const handleSendCommand = () => {
    if (command.trim()) {
      console.log('[AgentInspector] Sending command to', agent.name, ':', command);
      setLogs(prev => [...prev.slice(-19), `[CMD] User: ${command}`]);
      setCommand('');
      // In a real implementation, we would send this via socket or API
    }
  };

  const statusColor = agent.status === 'active' ? '#FFD700' : 
                     agent.status === 'idle' ? '#00D4FF' : 
                     agent.status === 'error' ? '#FF4444' : '#888888';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          className="w-[900px] h-[650px] bg-slate-950 border border-cyan-500/30 rounded-xl shadow-2xl overflow-hidden flex flex-col"
          style={{ boxShadow: '0 0 50px rgba(0, 214, 255, 0.15)' }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-cyan-500/20 flex items-center justify-between bg-slate-900/50">
            <div className="flex items-center gap-4">
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center text-lg font-bold border"
                style={{
                  borderColor: `${statusColor}66`,
                  color: statusColor,
                  background: `${statusColor}15`,
                }}
              >
                {agent.name.slice(0, 2)}
              </div>
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  {agent.name}
                  <span className="text-xs px-2 py-0.5 rounded border border-cyan-500/30 text-cyan-400 font-mono">
                    {agent.role}
                  </span>
                </h2>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="w-2 h-2 rounded-full" style={{ background: statusColor }}></span>
                  {agent.status.toUpperCase()}
                  <span className="text-slate-600">|</span>
                  <span>ID: {agent.id.slice(0, 8)}</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg"
            >
              <X size={20} />
            </button>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar Navigation */}
            <div className="w-48 border-r border-white/5 bg-slate-900/30 flex flex-col p-2 gap-1">
              <button
                onClick={() => setActiveView('live')}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${activeView === 'live' ? 'bg-cyan-500/10 text-cyan-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
              >
                <Eye size={16} /> Live Feed
              </button>
              <button
                onClick={() => setActiveView('logs')}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${activeView === 'logs' ? 'bg-cyan-500/10 text-cyan-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
              >
                <Terminal size={16} /> Console Logs
              </button>
              <button
                onClick={() => setActiveView('thought')}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${activeView === 'thought' ? 'bg-cyan-500/10 text-cyan-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
              >
                <Cpu size={16} /> Thought Process
              </button>
            </div>

            {/* Viewport */}
            <div className="flex-1 bg-slate-950 p-6 overflow-y-auto relative">
              {/* Background Grid Effect */}
              <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03] pointer-events-none"></div>

              {activeView === 'live' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                      <h4 className="text-xs uppercase text-slate-500 mb-2 flex items-center gap-2">
                        <Activity size={12} /> Current Operation
                      </h4>
                      <p className="text-lg text-white font-medium break-words leading-tight">{activeTask}</p>
                    </div>
                    <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                      <h4 className="text-xs uppercase text-slate-500 mb-2 flex items-center gap-2">
                        <Zap size={12} /> Performance
                      </h4>
                      <div className="flex items-end gap-2">
                        <span className="text-2xl font-bold text-emerald-400">{agent.performance || 95}%</span>
                        <span className="text-xs text-slate-400 mb-1">efficiency</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-black/40 rounded-lg border border-white/10 p-4 font-mono text-sm h-[300px] overflow-y-auto custom-scrollbar">
                    <div className="text-xs text-cyan-500 mb-2 border-b border-cyan-500/20 pb-1 sticky top-0 bg-black/40 backdrop-blur-sm">LIVE_ACTION_FEED</div>
                    {logs.length === 0 ? (
                        <div className="text-slate-600 italic mt-4 text-center">Waiting for neural link data...</div>
                    ) : (
                        logs.map((log, i) => (
                        <div key={i} className="mb-1 text-slate-300 break-words">
                            <span className="text-slate-600 mr-2">{log.split(']')[0]}]</span>
                            {log.split(']')[1]}
                        </div>
                        ))
                    )}
                    <div className="animate-pulse text-cyan-500 mt-2">_</div>
                  </div>
                </div>
              )}

              {activeView === 'logs' && (
                <div className="font-mono text-xs space-y-1 text-slate-300 h-full overflow-y-auto custom-scrollbar">
                  {logs.map((log, i) => (
                    <div key={i} className="border-b border-white/5 pb-1 break-words">
                      {log}
                    </div>
                  ))}
                  {logs.length === 0 && (
                      <div className="text-slate-600 italic">No logs captured in this session yet.</div>
                  )}
                </div>
              )}

              {activeView === 'thought' && (
                <div className="space-y-4">
                  <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                    <h3 className="text-sm font-semibold text-purple-400 mb-2">Cognitive State</h3>
                    <p className="text-slate-300 text-sm leading-relaxed">
                      {currentThought}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                    <h3 className="text-sm font-semibold text-blue-400 mb-2">Context Window</h3>
                    <div className="flex flex-wrap gap-2">
                      {contextTags.length > 0 ? contextTags.map(tag => (
                        <span key={tag} className="px-2 py-1 bg-white/5 rounded text-xs text-slate-300 border border-white/10">
                          {tag}
                        </span>
                      )) : (
                          <span className="text-slate-500 text-xs italic">Empty context</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Command Footer */}
          <div className="p-4 bg-slate-900/80 border-t border-white/10">
            <div className="relative">
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendCommand()}
                placeholder={`Direct command to ${agent.name}...`}
                className="w-full bg-black/50 border border-cyan-500/20 rounded-lg py-3 pl-4 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
              />
              <button
                onClick={handleSendCommand}
                className="absolute right-2 top-2 p-1.5 bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/40 transition-colors"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
