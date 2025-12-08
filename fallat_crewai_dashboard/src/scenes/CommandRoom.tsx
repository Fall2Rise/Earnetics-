import React, { Suspense, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, PerspectiveCamera } from '@react-three/drei';
import { motion } from 'framer-motion';
import { DivisionalZone } from '../components/3d/DivisionalZone';
import { useAgentStore } from '../stores/agentStore';

const DEPARTMENT_ZONES = [
  {
    department: 'Executive Board',
    position: [0, 2, 0] as [number, number, number],
    scale: [4, 3, 4] as [number, number, number],
    color: '#FFD700',
  },
  {
    department: 'Finance & Revenue',
    position: [8, 0, 0] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#00D4FF',
  },
  {
    department: 'Creative & Product',
    position: [-8, 0, 0] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#FF1493',
  },
  {
    department: 'Tech & Infrastructure',
    position: [0, 0, 8] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#00FFFF',
  },
  {
    department: 'Legal & Sovereignty',
    position: [0, 0, -8] as [number, number, number],
    scale: [4, 2, 4] as [number, number, number],
    color: '#FFA500',
  },
  {
    department: 'Health & Human Factor',
    position: [6, 0, 6] as [number, number, number],
    scale: [3, 2, 3] as [number, number, number],
    color: '#FF6B9D',
  },
  {
    department: 'Corporate Analytics',
    position: [-6, 0, 6] as [number, number, number],
    scale: [3, 2, 3] as [number, number, number],
    color: '#9D4EDD',
  },
  {
    department: 'Corporate Execution',
    position: [6, 0, -6] as [number, number, number],
    scale: [6, 2.5, 6] as [number, number, number],
    color: '#10B981',
  },
  {
    department: 'Email Marketing',
    position: [-6, 0, -6] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#F59E0B',
  },
];

export const CommandRoom: React.FC = () => {
  const { agents, selectedAgent, selectAgent, fetchAgents, getAgentsByDepartment, loading, error } = useAgentStore();

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, [fetchAgents]);

  const totalActive = agents.filter(a => a.status === 'active').length;

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-black">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        className="absolute inset-0"
      >
        <Canvas>
          <Suspense fallback={null}>
            <PerspectiveCamera makeDefault position={[0, 15, 20]} fov={60} />
            
            <ambientLight intensity={0.3} />
            <directionalLight position={[10, 10, 5]} intensity={0.6} />
            <directionalLight position={[-10, 10, -5]} intensity={0.3} />
            
            <Stars
              radius={150}
              depth={80}
              count={7000}
              factor={5}
              saturation={0}
              fade
              speed={1}
            />

            {DEPARTMENT_ZONES.map((zone) => {
              const zoneAgents = getAgentsByDepartment(zone.department);
              return (
                <DivisionalZone
                  key={zone.department}
                  department={zone.department}
                  agents={zoneAgents}
                  position={zone.position}
                  scale={zone.scale}
                  color={zone.color}
                  onAgentClick={selectAgent}
                  selectedAgent={selectedAgent}
                />
              );
            })}

            <gridHelper args={[40, 40, '#00ff88', '#1a1a1a']} position={[0, -2, 0]} />

            <OrbitControls
              enablePan
              enableZoom
              enableRotate
              minDistance={10}
              maxDistance={50}
              maxPolarAngle={Math.PI / 2.2}
            />
          </Suspense>
        </Canvas>
      </motion.div>

      <div className="absolute top-6 left-6 z-10">
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-xl p-4 min-w-[280px]"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              EARNETICS COMMAND CENTER
            </h2>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Active Agents:</span>
              <span className="text-green-400 font-mono">
                {totalActive}/{agents.length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Divisional Zones:</span>
              <span className="text-cyan-400 font-mono">{DEPARTMENT_ZONES.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">System Status:</span>
              <span className="text-cyan-400 font-mono">OPERATIONAL</span>
            </div>
          </div>

          {loading && (
            <div className="mt-3 text-xs text-yellow-400 animate-pulse">
              Syncing agents...
            </div>
          )}

          {error && (
            <div className="mt-3 text-xs text-red-400">
              Error: {error}
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-4 bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-xl p-4 max-h-[400px] overflow-y-auto"
        >
          <h3 className="text-sm font-bold text-cyan-400 mb-3">DEPARTMENT ZONES</h3>
          <div className="space-y-2">
            {DEPARTMENT_ZONES.map((zone) => {
              const zoneAgents = getAgentsByDepartment(zone.department);
              const activeCount = zoneAgents.filter(a => a.status === 'active').length;
              return (
                <div key={zone.department} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: zone.color }}
                    />
                    <span className="text-gray-300">{zone.department}</span>
                  </div>
                  <span className="text-gray-400 font-mono">
                    {activeCount}/{zoneAgents.length}
                  </span>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>

      {selectedAgent && (
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 100, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="absolute top-6 right-6 z-10 bg-black/70 backdrop-blur-md border border-cyan-500/30 rounded-xl p-5 min-w-[320px] max-h-[80vh] overflow-y-auto"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-white">{selectedAgent.name}</h3>
              <p className="text-sm text-cyan-400">{selectedAgent.role}</p>
            </div>
            <button
              onClick={() => selectAgent(null)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="space-y-3">
            <div>
              <div className="text-xs text-gray-400 mb-1">Department</div>
              <div 
                className="text-sm text-white font-mono px-2 py-1 rounded border"
                style={{ 
                  borderColor: DEPARTMENT_ZONES.find(z => z.department === selectedAgent.department)?.color || '#6366f1',
                  backgroundColor: `${DEPARTMENT_ZONES.find(z => z.department === selectedAgent.department)?.color || '#6366f1'}20`
                }}
              >
                {selectedAgent.department}
              </div>
            </div>

            <div>
              <div className="text-xs text-gray-400 mb-1">Division</div>
              <div className="text-sm text-white font-mono">{selectedAgent.division}</div>
            </div>

            <div>
              <div className="text-xs text-gray-400 mb-1">Status</div>
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: selectedAgent.status === 'active' ? '#10b981' : '#6b7280',
                  }}
                />
                <span className="text-sm text-white uppercase">{selectedAgent.status}</span>
              </div>
            </div>

            <div>
              <div className="text-xs text-gray-400 mb-1">Performance</div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
                  style={{ width: `${selectedAgent.performance}%` }}
                />
              </div>
              <div className="text-xs text-right text-gray-400 mt-1">
                {selectedAgent.performance.toFixed(1)}%
              </div>
            </div>

            {selectedAgent.memoryEntries !== undefined && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Memory Entries</div>
                <div className="text-sm text-white font-mono">{selectedAgent.memoryEntries}</div>
              </div>
            )}

            {selectedAgent.specialties && selectedAgent.specialties.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Specialties</div>
                <div className="flex flex-wrap gap-1">
                  {selectedAgent.specialties.map((specialty, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded-full border border-cyan-500/30"
                    >
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedAgent.currentTask && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Current Task</div>
                <div className="text-sm text-white">{selectedAgent.currentTask}</div>
              </div>
            )}

            {selectedAgent.lastActivity && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Last Activity</div>
                <div className="text-xs text-gray-300 font-mono">
                  {new Date(selectedAgent.lastActivity).toLocaleString()}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-black/50 backdrop-blur-sm border border-cyan-500/20 rounded-full px-6 py-3"
        >
          <p className="text-xs text-gray-400 text-center">
            <span className="text-cyan-400 font-mono">MOUSE</span> to rotate • 
            <span className="text-cyan-400 font-mono"> SCROLL</span> to zoom • 
            <span className="text-cyan-400 font-mono"> CLICK</span> agent for details
          </p>
        </motion.div>
      </div>
    </div>
  );
};

import React, { Suspense, useEffect, useState, useRef, useCallback } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { VRButton, XR, Controllers, Hands } from '@react-three/xr';
import { motion, AnimatePresence } from 'framer-motion';
import { DivisionalZone } from '../components/3d/DivisionalZone';
import { HolographicPanel } from '../components/3d/HolographicPanel';
import { ParticleBackground } from '../components/3d/ParticleBackground';
import { VoiceControl } from '../components/VoiceControl';
import { useAgentStore } from '../stores/agentStore';
import type { Agent } from '../stores/agentStore';

const DEPARTMENT_ZONES = [
  {
    department: 'Executive Board',
    position: [0, 2, 0] as [number, number, number],
    scale: [4, 3, 4] as [number, number, number],
    color: '#FFD700',
  },
  {
    department: 'Finance & Revenue',
    position: [8, 0, 0] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#00D4FF',
  },
  {
    department: 'Creative & Product',
    position: [-8, 0, 0] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#FF1493',
  },
  {
    department: 'Tech & Infrastructure',
    position: [0, 0, 8] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#00FFFF',
  },
  {
    department: 'Legal & Sovereignty',
    position: [0, 0, -8] as [number, number, number],
    scale: [4, 2, 4] as [number, number, number],
    color: '#FFA500',
  },
  {
    department: 'Health & Human Factor',
    position: [6, 0, 6] as [number, number, number],
    scale: [3, 2, 3] as [number, number, number],
    color: '#FF6B9D',
  },
  {
    department: 'Corporate Analytics',
    position: [-6, 0, 6] as [number, number, number],
    scale: [3, 2, 3] as [number, number, number],
    color: '#9D4EDD',
  },
  {
    department: 'Corporate Execution',
    position: [6, 0, -6] as [number, number, number],
    scale: [6, 2.5, 6] as [number, number, number],
    color: '#10B981',
  },
  {
    department: 'Email Marketing',
    position: [-6, 0, -6] as [number, number, number],
    scale: [5, 2.5, 5] as [number, number, number],
    color: '#F59E0B',
  },
];

interface CameraControllerProps {
  targetAgent: Agent | null;
  resetView: boolean;
  zoomIn: boolean;
  zoomOut: boolean;
  onResetComplete: () => void;
}

const CameraController: React.FC<CameraControllerProps> = ({ 
  targetAgent, 
  resetView, 
  zoomIn, 
  zoomOut,
  onResetComplete 
}) => {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  useEffect(() => {
    if (targetAgent && controlsRef.current) {
      const zone = DEPARTMENT_ZONES.find(z => z.department === targetAgent.department);
      if (zone) {
        controlsRef.current.target.set(...zone.position);
        camera.position.set(
          zone.position[0] + 5,
          zone.position[1] + 8,
          zone.position[2] + 5
        );
      }
    }
  }, [targetAgent, camera]);

  useEffect(() => {
    if (resetView && controlsRef.current) {
      controlsRef.current.target.set(0, 0, 0);
      camera.position.set(0, 15, 20);
      onResetComplete();
    }
  }, [resetView, camera, onResetComplete]);

  useEffect(() => {
    if (zoomIn) {
      camera.position.multiplyScalar(0.9);
    }
  }, [zoomIn, camera]);

  useEffect(() => {
    if (zoomOut) {
      camera.position.multiplyScalar(1.1);
    }
  }, [zoomOut, camera]);

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan
      enableZoom
      enableRotate
      minDistance={8}
      maxDistance={60}
      maxPolarAngle={Math.PI / 2.1}
      enableDamping
      dampingFactor={0.05}
    />
  );
};

const Scene: React.FC<{
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentClick: (agent: Agent) => void;
  getAgentsByDepartment: (dept: string) => Agent[];
  targetAgent: Agent | null;
  resetView: boolean;
  zoomIn: boolean;
  zoomOut: boolean;
  onResetComplete: () => void;
}> = ({ 
  agents, 
  selectedAgent, 
  onAgentClick, 
  getAgentsByDepartment,
  targetAgent,
  resetView,
  zoomIn,
  zoomOut,
  onResetComplete
}) => {
  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 15, 20]} fov={60} />
      
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 15, 5]} intensity={0.8} castShadow />
      <directionalLight position={[-10, 10, -5]} intensity={0.4} />
      <pointLight position={[0, 20, 0]} intensity={1} distance={50} decay={2} color="#00ffff" />
      
      <ParticleBackground />

      {DEPARTMENT_ZONES.map((zone) => {
        const zoneAgents = getAgentsByDepartment(zone.department);
        return (
          <DivisionalZone
            key={zone.department}
            department={zone.department}
            agents={zoneAgents}
            position={zone.position}
            scale={zone.scale}
            color={zone.color}
            onAgentClick={onAgentClick}
            selectedAgent={selectedAgent}
          />
        );
      })}

      {selectedAgent && (
        <HolographicPanel
          agent={selectedAgent}
          onClose={() => onAgentClick(null as any)}
          position={[
            selectedAgent.position[0],
            selectedAgent.position[1] + 3,
            selectedAgent.position[2]
          ]}
        />
      )}

      <CameraController 
        targetAgent={targetAgent}
        resetView={resetView}
        zoomIn={zoomIn}
        zoomOut={zoomOut}
        onResetComplete={onResetComplete}
      />
    </>
  );
};

export const CommandRoom: React.FC = () => {
  const { 
    agents, 
    selectedAgent, 
    selectAgent, 
    fetchAgents, 
    getAgentsByDepartment, 
    loading, 
    error,
    updateAgentStatus 
  } = useAgentStore();

  const [vrEnabled, setVrEnabled] = useState(false);
  const [targetAgent, setTargetAgent] = useState<Agent | null>(null);
  const [resetView, setResetView] = useState(false);
  const [zoomIn, setZoomIn] = useState(false);
  const [zoomOut, setZoomOut] = useState(false);
  const [showStatusReport, setShowStatusReport] = useState(false);

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, [fetchAgents]);

  const handleVoiceCommand = useCallback((command: string, params?: any) => {
    switch (command) {
      case 'focus_agent':
        if (params?.agent) {
          selectAgent(params.agent);
          setTargetAgent(params.agent);
        }
        break;
      case 'pause_division':
        if (params?.division) {
          const divisionAgents = getAgentsByDepartment(params.division);
          divisionAgents.forEach(agent => {
            updateAgentStatus(agent.id, 'idle');
          });
        }
        break;
      case 'status_report':
        setShowStatusReport(true);
        setTimeout(() => setShowStatusReport(false), 5000);
        break;
      case 'zoom_in':
        setZoomIn(true);
        setTimeout(() => setZoomIn(false), 100);
        break;
      case 'zoom_out':
        setZoomOut(true);
        setTimeout(() => setZoomOut(false), 100);
        break;
      case 'reset_view':
        setResetView(true);
        setTargetAgent(null);
        selectAgent(null);
        break;
      case 'show_all_agents':
        setResetView(true);
        setTargetAgent(null);
        break;
    }
  }, [selectAgent, getAgentsByDepartment, updateAgentStatus]);

  const handleResetComplete = useCallback(() => {
    setResetView(false);
  }, []);

  const totalActive = agents.filter(a => a.status === 'active').length;
  const totalIdle = agents.filter(a => a.status === 'idle').length;
  const totalError = agents.filter(a => a.status === 'error').length;

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-black overflow-hidden">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.5 }}
        className="absolute inset-0"
      >
        {vrEnabled ? (
          <Canvas>
            <XR>
              <Suspense fallback={null}>
                <Scene
                  agents={agents}
                  selectedAgent={selectedAgent}
                  onAgentClick={selectAgent}
                  getAgentsByDepartment={getAgentsByDepartment}
                  targetAgent={targetAgent}
                  resetView={resetView}
                  zoomIn={zoomIn}
                  zoomOut={zoomOut}
                  onResetComplete={handleResetComplete}
                />
                <Controllers />
                <Hands />
              </Suspense>
            </XR>
          </Canvas>
        ) : (
          <Canvas>
            <Suspense fallback={null}>
              <Scene
                agents={agents}
                selectedAgent={selectedAgent}
                onAgentClick={selectAgent}
                getAgentsByDepartment={getAgentsByDepartment}
                targetAgent={targetAgent}
                resetView={resetView}
                zoomIn={zoomIn}
                zoomOut={zoomOut}
                onResetComplete={handleResetComplete}
              />
            </Suspense>
          </Canvas>
        )}
      </motion.div>

      <div className="absolute top-6 left-6 z-10">
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-black/70 backdrop-blur-xl border-2 border-cyan-500/40 rounded-xl p-5 min-w-[320px] shadow-2xl shadow-cyan-500/20"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="relative">
              <div className="w-4 h-4 rounded-full bg-green-500 animate-pulse" />
              <div className="absolute inset-0 w-4 h-4 rounded-full bg-green-500 animate-ping" />
            </div>
            <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400">
              EARNETICS AI COMMAND CENTER
            </h2>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center p-2 bg-gradient-to-r from-green-500/10 to-transparent rounded">
              <span className="text-gray-300">Active Agents:</span>
              <span className="text-green-400 font-mono font-bold text-lg">
                {totalActive}/{agents.length}
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gradient-to-r from-orange-500/10 to-transparent rounded">
              <span className="text-gray-300">Idle Agents:</span>
              <span className="text-orange-400 font-mono font-bold text-lg">{totalIdle}</span>
            </div>
            {totalError > 0 && (
              <div className="flex justify-between items-center p-2 bg-gradient-to-r from-red-500/10 to-transparent rounded">
                <span className="text-gray-300">Error State:</span>
                <span className="text-red-400 font-mono font-bold text-lg">{totalError}</span>
              </div>
            )}
            <div className="flex justify-between items-center p-2 bg-gradient-to-r from-cyan-500/10 to-transparent rounded">
              <span className="text-gray-300">Divisional Zones:</span>
              <span className="text-cyan-400 font-mono font-bold">{DEPARTMENT_ZONES.length}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gradient-to-r from-blue-500/10 to-transparent rounded">
              <span className="text-gray-300">System Status:</span>
              <span className="text-blue-400 font-mono font-bold">OPERATIONAL</span>
            </div>
          </div>

          {loading && (
            <div className="mt-4 flex items-center gap-2 text-xs text-yellow-400 animate-pulse">
              <div className="w-2 h-2 rounded-full bg-yellow-400 animate-ping" />
              Syncing agents...
            </div>
          )}

          {error && (
            <div className="mt-4 text-xs text-red-400 p-2 bg-red-500/10 rounded border border-red-500/30">
              Error: {error}
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-4 bg-black/70 backdrop-blur-xl border-2 border-cyan-500/40 rounded-xl p-4 max-h-[400px] overflow-y-auto shadow-2xl shadow-cyan-500/20"
        >
          <h3 className="text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-3">
            DEPARTMENT ZONES
          </h3>
          <div className="space-y-2">
            {DEPARTMENT_ZONES.map((zone) => {
              const zoneAgents = getAgentsByDepartment(zone.department);
              const activeCount = zoneAgents.filter(a => a.status === 'active').length;
              return (
                <div 
                  key={zone.department} 
                  className="flex items-center justify-between text-xs p-2 rounded hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full animate-pulse" 
                      style={{ 
                        backgroundColor: zone.color,
                        boxShadow: `0 0 10px ${zone.color}`
                      }}
                    />
                    <span className="text-gray-200 font-medium">{zone.department}</span>
                  </div>
                  <span className="text-gray-400 font-mono">
                    {activeCount}/{zoneAgents.length}
                  </span>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>

      <AnimatePresence>
        {showStatusReport && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 bg-black/90 backdrop-blur-xl border-2 border-cyan-500/50 rounded-2xl p-8 min-w-[500px] shadow-2xl shadow-cyan-500/30"
          >
            <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-6">
              System Status Report
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-green-500/20 to-green-500/5 border border-green-500/30 rounded-lg p-4">
                  <div className="text-green-400 text-3xl font-bold">{totalActive}</div>
                  <div className="text-gray-300 text-sm">Active Agents</div>
                </div>
                <div className="bg-gradient-to-br from-orange-500/20 to-orange-500/5 border border-orange-500/30 rounded-lg p-4">
                  <div className="text-orange-400 text-3xl font-bold">{totalIdle}</div>
                  <div className="text-gray-300 text-sm">Idle Agents</div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/5 border border-cyan-500/30 rounded-lg p-4">
                <div className="text-cyan-400 text-3xl font-bold">{agents.length}</div>
                <div className="text-gray-300 text-sm">Total Agents Deployed</div>
              </div>
              <div className="text-xs text-gray-400 text-center pt-4 border-t border-gray-700">
                All systems operational • Real-time monitoring active
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute top-6 right-6 z-10 flex flex-col gap-3">
        <motion.button
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          onClick={() => setVrEnabled(!vrEnabled)}
          className={`px-6 py-3 rounded-xl backdrop-blur-xl border-2 transition-all font-bold ${
            vrEnabled
              ? 'bg-purple-500/30 border-purple-500 text-purple-300 shadow-lg shadow-purple-500/30'
              : 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30'
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {vrEnabled ? '🥽 VR MODE ACTIVE' : '🥽 ENABLE VR MODE'}
        </motion.button>

        {vrEnabled && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-black/80 backdrop-blur-xl border border-purple-500/30 rounded-lg p-3 text-xs text-purple-300"
          >
            Put on your VR headset to enter immersive mode
          </motion.div>
        )}
      </div>

      <VoiceControl onCommand={handleVoiceCommand} />

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-black/60 backdrop-blur-xl border border-cyan-500/30 rounded-full px-8 py-3 shadow-lg shadow-cyan-500/20"
        >
          <p className="text-xs text-gray-300 text-center">
            <span className="text-cyan-400 font-mono font-bold">MOUSE</span> to rotate • 
            <span className="text-cyan-400 font-mono font-bold"> SCROLL</span> to zoom • 
            <span className="text-cyan-400 font-mono font-bold"> CLICK</span> agent for details •
            <span className="text-purple-400 font-mono font-bold"> MIC</span> for voice commands
          </p>
        </motion.div>
      </div>
    </div>
  );
};
