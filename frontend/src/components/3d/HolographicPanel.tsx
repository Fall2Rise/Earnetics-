import React from 'react';
import { motion } from 'framer-motion';
import { Html } from '@react-three/drei';
import { Activity, Pause, Play, RefreshCw, X } from 'lucide-react';
import type { Agent } from '../../stores/agentStore';

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

        <div className="relative bg-black/40 backdrop-blur-md border border-cyan-500/30 rounded-xl shadow-[0_0_30px_rgba(6,182,212,0.2)] overflow-hidden">
          {/* Scanning line effect */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/10 to-transparent h-[200%] w-full animate-scan pointer-events-none" />

          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent" />

          <div className="p-6 relative z-10">
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
                      boxShadow: `0 0 15px ${agent.status === 'active'
                        ? '#10b981'
                        : agent.status === 'idle'
                          ? '#f59e0b'
                          : '#ef4444'
                        }`,
                    }}
                  />
                  <h3 className="text-xl font-bold text-white drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]">
                    {agent.name}
                  </h3>
                </div>
                <p className="text-sm text-cyan-200 font-mono tracking-wider">{agent.role}</p>
              </div>

              <button
                onClick={onClose}
                className="text-cyan-400 hover:text-white transition-colors p-1 hover:bg-cyan-500/20 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-cyan-950/30 border border-cyan-500/20 rounded-lg p-3 hover:bg-cyan-900/40 transition-colors">
                  <div className="text-[10px] uppercase tracking-widest text-cyan-400 mb-1">Department</div>
                  <div className="text-sm text-white font-mono truncate shadow-cyan-500/50">{agent.department}</div>
                </div>

                <div className="bg-cyan-950/30 border border-cyan-500/20 rounded-lg p-3 hover:bg-cyan-900/40 transition-colors">
                  <div className="text-[10px] uppercase tracking-widest text-cyan-400 mb-1">Division</div>
                  <div className="text-sm text-white font-mono truncate">{agent.division}</div>
                </div>
              </div>

              <div className="bg-cyan-950/30 border border-cyan-500/20 rounded-lg p-3">
                <div className="text-[10px] uppercase tracking-widest text-cyan-400 mb-2">Performance Metrics</div>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-cyan-200">Efficiency</span>
                      <span className="text-cyan-400 font-mono font-bold">{agent.performance.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden border border-cyan-500/10">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${agent.performance}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className="h-full bg-cyan-400 rounded-full"
                        style={{
                          boxShadow: '0 0 10px #22d3ee',
                        }}
                      />
                    </div>
                  </div>

                  {agent.memoryEntries !== undefined && (
                    <div className="flex justify-between text-xs">
                      <span className="text-cyan-200">Memory Entries</span>
                      <span className="text-cyan-400 font-mono">{agent.memoryEntries}</span>
                    </div>
                  )}
                </div>
              </div>

              {agent.currentTask && (
                <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <div className="text-[10px] uppercase tracking-widest text-purple-300">Current Task</div>
                  </div>
                  <div className="text-sm text-white/90 font-light italic">"{agent.currentTask}"</div>
                </div>
              )}

              {agent.specialties && agent.specialties.length > 0 && (
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-cyan-400 mb-2">Specialties</div>
                  <div className="flex flex-wrap gap-2">
                    {agent.specialties.map((specialty: string, idx: number) => (
                      <span
                        key={idx}
                        className="text-[10px] px-2 py-1 bg-cyan-500/10 text-cyan-300 rounded border border-cyan-500/30"
                      >
                        {specialty}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {agent.lastActivity && (
                <div className="text-[10px] text-cyan-500/70 text-right font-mono">
                  LAST ACT: {new Date(agent.lastActivity).toLocaleTimeString()}
                </div>
              )}

              <div className="flex gap-2 pt-2 border-t border-cyan-500/20">
                {agent.status === 'active' && onPause && (
                  <button
                    onClick={onPause}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/40 text-orange-300 rounded transition-all text-xs uppercase tracking-wider"
                  >
                    <Pause className="w-3 h-3" />
                    <span>Pause</span>
                  </button>
                )}

                {agent.status !== 'active' && onResume && (
                  <button
                    onClick={onResume}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-500/10 hover:bg-green-500/20 border border-green-500/40 text-green-300 rounded transition-all text-xs uppercase tracking-wider"
                  >
                    <Play className="w-3 h-3" />
                    <span>Resume</span>
                  </button>
                )}

                {onReroute && (
                  <button
                    onClick={onReroute}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 rounded transition-all text-xs uppercase tracking-wider"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Reroute</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </Html>
  );
};
