import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Activity, TrendingUp } from 'lucide-react';
import type { Agent } from '../../stores/agentStore';

interface DepartmentPanelProps {
  department: string;
  agents: Agent[];
  color: string;
  onClose: () => void;
  position?: [number, number, number];
}

export const DepartmentPanel: React.FC<DepartmentPanelProps> = ({
  department,
  agents,
  color,
  onClose,
  position = [0, 5, 0],
}) => {
  const activeAgents = agents.filter(a => a.status === 'active').length;
  const idleAgents = agents.filter(a => a.status === 'idle').length;
  const totalMemory = agents.reduce((sum, a) => sum + (a.memoryEntries || 0), 0);
  const avgPerformance = agents.length > 0
    ? agents.reduce((sum, a) => sum + a.performance, 0) / agents.length
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.9 }}
      transition={{ duration: 0.3, type: 'spring' }}
      className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-2xl"
    >
      <div className="relative">
        {/* Glow effect */}
        <div
          className="absolute inset-0 rounded-2xl blur-2xl opacity-30"
          style={{ backgroundColor: color }}
        />
        
        {/* Main panel */}
        <div
          className="relative bg-black/95 backdrop-blur-xl border-2 rounded-2xl shadow-2xl overflow-hidden"
          style={{ borderColor: color }}
        >
          {/* Header */}
          <div
            className="px-6 py-4 border-b"
            style={{ borderColor: `${color}40` }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full animate-pulse"
                  style={{ backgroundColor: color }}
                />
                <h2 className="text-2xl font-bold text-white" style={{ textShadow: `0 0 10px ${color}` }}>
                  {department}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="px-6 py-4 grid grid-cols-4 gap-4 border-b" style={{ borderColor: `${color}40` }}>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Users size={16} className="text-gray-400" />
                <span className="text-2xl font-bold text-white">{agents.length}</span>
              </div>
              <div className="text-xs text-gray-400">Total Agents</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Activity size={16} className="text-green-400" />
                <span className="text-2xl font-bold text-green-400">{activeAgents}</span>
              </div>
              <div className="text-xs text-gray-400">Active</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <TrendingUp size={16} className="text-blue-400" />
                <span className="text-2xl font-bold text-blue-400">{totalMemory}</span>
              </div>
              <div className="text-xs text-gray-400">Memory Entries</div>
            </div>
            <div className="text-center">
              <div className="mb-1">
                <span className="text-2xl font-bold text-white">{avgPerformance.toFixed(0)}%</span>
              </div>
              <div className="text-xs text-gray-400">Avg Performance</div>
            </div>
          </div>

          {/* Agent List */}
          <div className="px-6 py-4 max-h-96 overflow-y-auto custom-scrollbar">
            <div className="space-y-2">
              {agents.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  No agents in this department
                </div>
              ) : (
                agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border"
                    style={{ borderColor: `${color}20` }}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{
                          backgroundColor:
                            agent.status === 'active'
                              ? '#10b981'
                              : agent.status === 'idle'
                              ? '#f59e0b'
                              : '#ef4444',
                        }}
                      />
                      <div className="flex-1">
                        <div className="text-white font-semibold">{agent.name}</div>
                        <div className="text-xs text-gray-400">{agent.role}</div>
                        {agent.currentTask && (
                          <div className="text-xs text-gray-500 mt-1 italic">
                            {agent.currentTask}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-white font-mono">
                        {agent.performance.toFixed(0)}%
                      </div>
                      <div className="text-xs text-gray-400">
                        {agent.memoryEntries || 0} entries
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

