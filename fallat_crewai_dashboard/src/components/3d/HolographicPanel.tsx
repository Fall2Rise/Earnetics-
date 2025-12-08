import React, { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Html } from '@react-three/drei';
import { Activity, Pause, Play, RefreshCw, X } from 'lucide-react';
import type { Agent } from '../stores/agentStore';

interface HolographicPanelProps {
  agent: Agent;
  onClose: () => void;
  onPause?: () => void;
  onResume?: () => void;
  onReroute?: () => void;
  position?: [number, number, number];
}

export const HolographicPanel: React.FC<HolographicPanelProps> = ({
  agent,
  onClose,
  onPause,
  onResume,
  onReroute,
  position = [0, 3, 0],
}) => {
  return (
    <Html position={position} center distanceFactor={8}>
      <motion.div
        initial={{ opacity: 0, scale: 0.8, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.8, y: -20 }}
        transition={{ duration: 0.3, type: 'spring' }}
        className="relative"
        style={{ width: '400px' }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl blur-xl" />
        
        <div className="relative bg-black/90 backdrop-blur-xl border-2 border-cyan-500/50 rounded-xl shadow-2xl shadow-cyan-500/30 overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse" />
          
          <div className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div
                    className="w-3 h-3 rounded-full animate-pulse"
                    style={{
                      backgroundColor:
                        agent.status === 'active'
                          ? '#10b981'
                          : agent.status === 'idle'
                          ? '#f59e0b'
                          : '#ef4444',
                      boxShadow: `0 0 10px ${
                        agent.status === 'active'
                          ? '#10b981'
                          : agent.status === 'idle'
                          ? '#f59e0b'
                          : '#ef4444'
                      }`,
                    }}
                  />
                  <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                    {agent.name}
                  </h3>
                </div>
                <p className="text-sm text-cyan-300 font-mono">{agent.role}</p>
              </div>
              
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-white/10 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Department</div>
                  <div className="text-sm text-white font-mono truncate">{agent.department}</div>
                </div>
                
                <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Division</div>
                  <div className="text-sm text-white font-mono truncate">{agent.division}</div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-2">Performance Metrics</div>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-300">Efficiency</span>
                      <span className="text-cyan-400 font-mono">{agent.performance.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${agent.performance}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                        style={{
                          boxShadow: '0 0 10px rgba(6, 182, 212, 0.5)',
                        }}
                      />
                    </div>
                  </div>
                  
                  {agent.memoryEntries !== undefined && (
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-300">Memory Entries</span>
                      <span className="text-cyan-400 font-mono">{agent.memoryEntries}</span>
                    </div>
                  )}
                </div>
              </div>

              {agent.currentTask && (
                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <div className="text-xs text-gray-400">Current Task</div>
                  </div>
                  <div className="text-sm text-white">{agent.currentTask}</div>
                </div>
              )}

              {agent.specialties && agent.specialties.length > 0 && (
                <div>
                  <div className="text-xs text-gray-400 mb-2">Specialties</div>
                  <div className="flex flex-wrap gap-2">
                    {agent.specialties.map((specialty, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 rounded-full border border-cyan-500/30"
                      >
                        {specialty}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {agent.lastActivity && (
                <div className="text-xs text-gray-400">
                  Last Activity: <span className="text-gray-300 font-mono">{new Date(agent.lastActivity).toLocaleString()}</span>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                {agent.status === 'active' && onPause && (
                  <button
                    onClick={onPause}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/50 text-orange-300 rounded-lg transition-all"
                  >
                    <Pause className="w-4 h-4" />
                    <span className="text-sm font-medium">Pause</span>
                  </button>
                )}
                
                {agent.status !== 'active' && onResume && (
                  <button
                    onClick={onResume}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 border border-green-500/50 text-green-300 rounded-lg transition-all"
                  >
                    <Play className="w-4 h-4" />
                    <span className="text-sm font-medium">Resume</span>
                  </button>
                )}
                
                {onReroute && (
                  <button
                    onClick={onReroute}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 text-cyan-300 rounded-lg transition-all"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span className="text-sm font-medium">Reroute</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent" />
        </div>
      </motion.div>
    </Html>
  );
};
