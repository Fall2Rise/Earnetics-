/// <reference types="@react-three/fiber" />
import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars, Float } from '@react-three/drei';
import * as THREE from 'three';
import { Agent3D } from './Agent3D';
import { Zone3D } from './Zone3D';

const ZONES = [
    { id: 'executive', name: 'Executive Board', color: '#ff0080', description: 'Strategic vision and leadership' },
    { id: 'finance', name: 'Finance & Revenue', color: '#ffaa00', description: 'Financial optimization and trading' },
    { id: 'creative', name: 'Creative & Product', color: '#0080ff', description: 'Brand storytelling and design' },
    { id: 'tech', name: 'Tech & Infra', color: '#00ff88', description: 'Infrastructure and development' },
    { id: 'legal', name: 'Legal & Sovereignty', color: '#7a7a7a', description: 'Compliance and enforcement' },
    { id: 'health', name: 'Health & Human', color: '#ff88ff', description: 'Operator wellness' },
    { id: 'analytics', name: 'Analytics', color: '#8800ff', description: 'Data center and optimization' },
    { id: 'ops', name: 'Implementation', color: '#ff4400', description: 'Operations and execution' },
    { id: 'email', name: 'Email Marketing', color: '#00ffff', description: 'Communication hub' },
];

// Mock agents for initial visualization
const MOCK_AGENTS = [
    { id: 'akasha', name: 'Akasha', role: 'CEO', zone: 'executive', status: 'active' },
    { id: 'atlas', name: 'Atlas', role: 'COO', zone: 'executive', status: 'active' },
    { id: 'vega', name: 'Vega', role: 'CFO', zone: 'finance', status: 'busy' },
    { id: 'omen', name: 'Omen', role: 'Strategist', zone: 'finance', status: 'active' },
    { id: 'nova', name: 'Nova', role: 'CMO', zone: 'creative', status: 'active' },
    { id: 'lyra', name: 'Lyra', role: 'Storyteller', zone: 'creative', status: 'idle' },
    { id: 'forge', name: 'Forge', role: 'CTO', zone: 'tech', status: 'active' },
    { id: 'titan', name: 'Titan', role: 'Infra', zone: 'tech', status: 'active' },
    { id: 'lex', name: 'Lex', role: 'Policy', zone: 'legal', status: 'active' },
    { id: 'seraph', name: 'Seraph', role: 'Wellness', zone: 'health', status: 'active' },
];

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8001/ws';

const CommandDeck = ({ onAgentSelect }: { onAgentSelect: (id: string | null) => void }) => {
    const [agents, setAgents] = useState(MOCK_AGENTS);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

    useEffect(() => {
        // Fetch initial agents
        const fetchAgents = async () => {
            try {
                // @ts-ignore
                if (window.api?.getAgents) {
                    // @ts-ignore
                    const data = await window.api.getAgents();
                    if (data && data.length > 0) setAgents(data);
                } else {
                    const res = await fetch(`${API_URL}/api/dashboard/agents`);
                    const data = await res.json();
                    if (data.agents) setAgents(data.agents);
                }
            } catch (err) {
                console.error('Failed to fetch agents:', err);
            }
        };

        fetchAgents();

        // WebSocket for real-time updates
        let ws: WebSocket | null = null;

        const connectWS = () => {
            ws = new WebSocket(WS_URL);
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'AGENT_STATUS_CHANGE') {
                        setAgents(prev => prev.map(a => a.id === data.payload.agentId ? { ...a, status: data.payload.status } : a));
                    }
                } catch (err) {
                    console.error('WS parse error:', err);
                }
            };
            ws.onclose = () => setTimeout(connectWS, 5000);
        };

        connectWS();

        // Electron IPC fallback
        // @ts-ignore
        const cleanup = window.api?.onNewEvent?.((event: any) => {
            if (event.type === 'AGENT_STATUS_CHANGE') {
                setAgents(prev => prev.map(a => a.id === event.agentId ? { ...a, status: event.status } : a));
            }
        });

        return () => {
            ws?.close();
            cleanup?.();
        };
    }, []);

    // Camera focus logic
    useFrame((state) => {
        if (selectedAgent) {
            const agent = agents.find(a => a.id === selectedAgent);
            if (agent) {
                const zone = ZONES.find(z => z.id === agent.zone);
                if (zone) {
                    const zoneIdx = ZONES.indexOf(zone);
                    const angle = (zoneIdx / ZONES.length) * Math.PI * 2;
                    const radius = 12;
                    const zx = Math.cos(angle) * radius;
                    const zz = Math.sin(angle) * radius;

                    const filtered = agents.filter(a => a.zone === agent.zone);
                    const agentIdx = filtered.indexOf(agent);
                    const agentAngle = (agentIdx / filtered.length) * Math.PI * 2;
                    const agentRadius = 2;
                    const ax = zx + Math.cos(agentAngle) * agentRadius;
                    const az = zz + Math.sin(agentAngle) * agentRadius;

                    const targetPos = new THREE.Vector3(ax, 1, az) as any;
                    const cameraTargetPos = new THREE.Vector3(ax + 5, 5, az + 5) as any;

                    state.camera.position.lerp(cameraTargetPos, 0.05);
                    // @ts-ignore
                    if (state.controls) {
                        // @ts-ignore
                        state.controls.target.lerp(targetPos, 0.05);
                    } else {
                        state.camera.lookAt(targetPos);
                    }
                }
            }
        }
    });

    const handleAgentClick = (id: string) => {
        setSelectedAgent(id);
        onAgentSelect(id);
    };

    return (
        <group>
            {/* Central Core */}
            <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                <mesh position={[0, 2, 0]} onClick={() => { setSelectedAgent(null); onAgentSelect(null); }}>
                    <octahedronGeometry args={[2, 0]} />
                    <meshStandardMaterial color="#00ff88" wireframe transparent opacity={0.2} />
                </mesh>
                <mesh position={[0, 2, 0]}>
                    <sphereGeometry args={[0.8, 32, 32]} />
                    <meshStandardMaterial color="#00ff88" emissive="#00ff88" emissiveIntensity={1} />
                </mesh>
            </Float>

            {/* Zones */}
            {ZONES.map((zone, i) => {
                const angle = (i / ZONES.length) * Math.PI * 2;
                const radius = 12;
                const x = Math.cos(angle) * radius;
                const z = Math.sin(angle) * radius;

                return (
                    <group key={zone.id}>
                        <Zone3D
                            position={[x, 0, z]}
                            name={zone.name}
                            color={zone.color}
                            description={zone.description}
                        />

                        {/* Agents in this zone */}
                        {agents.filter(a => a.zone === zone.id).map((agent, ai, filtered) => {
                            const agentAngle = (ai / filtered.length) * Math.PI * 2;
                            const agentRadius = 2;
                            const ax = x + Math.cos(agentAngle) * agentRadius;
                            const az = z + Math.sin(agentAngle) * agentRadius;

                            return (
                                <Agent3D
                                    key={agent.id}
                                    position={[ax, 1, az]}
                                    name={agent.name}
                                    role={agent.role}
                                    status={agent.status as any}
                                    onClick={() => handleAgentClick(agent.id)}
                                />
                            );
                        })}
                    </group>
                );
            })}
        </group>
    );
};

export const OpsRoom = () => {
    const [stripeStatus, setStripeStatus] = useState<{ ok: boolean, message: string }>({ ok: false, message: 'Checking...' });
    const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const res = await fetch(`${API_URL}/health`);
                const data = await res.json();
                setStripeStatus({
                    ok: data.checks?.stripe?.ok || false,
                    message: data.checks?.stripe?.message || 'Not configured'
                });
            } catch (err) {
                setStripeStatus({ ok: false, message: 'Backend unreachable' });
            }
        };
        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full h-full bg-[#050505] relative">
            <Canvas shadows>
                <PerspectiveCamera makeDefault position={[20, 20, 20]} fov={50} />
                <OrbitControls
                    enableDamping
                    dampingFactor={0.05}
                    maxPolarAngle={Math.PI / 2.1}
                    minDistance={5}
                    maxDistance={50}
                />

                <ambientLight intensity={0.4} />
                <pointLight position={[10, 10, 10]} intensity={1.5} castShadow />
                <spotLight
                    position={[0, 20, 0]}
                    angle={0.3}
                    penumbra={1}
                    intensity={2}
                    castShadow
                    color="#00ff88"
                />

                <Stars radius={100} depth={50} count={7000} factor={4} saturation={0} fade speed={1} />

                <CommandDeck onAgentSelect={setSelectedAgentId} />
            </Canvas>

            {/* Overlay UI */}
            <div className="absolute top-6 left-6 pointer-events-none">
                <h1 className="text-4xl font-bold text-[#00ff88] tracking-tighter" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                    EARNETICS COMMAND CENTER
                </h1>
                <p className="text-white/40 text-sm font-mono mt-1">
                    SYSTEM STATUS: OPTIMAL // AUTONOMY ACTIVE
                </p>
            </div>

            {/* Revenue Readiness Panel */}
            <div className="absolute top-6 right-6 w-64 bg-black/60 backdrop-blur-md border border-white/10 p-4 rounded-lg">
                <div className="text-xs text-white/50 mb-2 uppercase tracking-widest flex justify-between items-center">
                    <span>Revenue Subsystem</span>
                    <div className={`w-2 h-2 rounded-full ${stripeStatus.ok ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                </div>
                <div className="flex flex-col gap-1">
                    <div className="text-sm font-bold text-white">Stripe: <span className={stripeStatus.ok ? 'text-green-400' : 'text-red-400'}>{stripeStatus.ok ? 'READY' : 'OFFLINE'}</span></div>
                    <div className="text-[10px] text-white/60 font-mono truncate">{stripeStatus.message}</div>
                </div>
                <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="text-[10px] text-white/40 uppercase mb-1">Active Mode</div>
                    <div className="text-xs text-blue-400 font-bold">REVENUE GENERATION ACTIVE</div>
                </div>
            </div>

            <div className="absolute bottom-6 right-6 flex flex-col gap-2 items-end">
                <div className="bg-black/60 backdrop-blur-md border border-white/10 p-4 rounded-lg">
                    <div className="text-xs text-white/50 mb-2 uppercase tracking-widest">Active Divisions</div>
                    <div className="grid grid-cols-3 gap-4">
                        {ZONES.map(z => (
                            <div key={z.id} className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: z.color }} />
                                <span className="text-[10px] text-white/80 whitespace-nowrap">{z.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Agent Detail Panel (Conditional) */}
            {selectedAgentId && (
                <div className="absolute bottom-6 left-6 w-80 bg-black/80 backdrop-blur-xl border border-[#00ff88]/30 p-6 rounded-xl shadow-[0_0_30px_rgba(0,255,136,0.1)]">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <div className="text-[10px] text-[#00ff88] uppercase tracking-[0.2em] mb-1">Agent Profile</div>
                            <h2 className="text-2xl font-bold text-white tracking-tight">{selectedAgentId.toUpperCase()}</h2>
                        </div>
                        <button
                            onClick={() => setSelectedAgentId(null)}
                            className="text-white/40 hover:text-white transition-colors"
                        >
                            ✕
                        </button>
                    </div>
                    <div className="space-y-4">
                        <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                            <div className="text-[10px] text-white/40 uppercase mb-1">Current Task</div>
                            <div className="text-sm text-white/90">Optimizing revenue streams for Q4...</div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                                <div className="text-[10px] text-white/40 uppercase mb-1">Efficiency</div>
                                <div className="text-lg font-bold text-[#00ff88]">98.4%</div>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                                <div className="text-[10px] text-white/40 uppercase mb-1">Uptime</div>
                                <div className="text-lg font-bold text-blue-400">142h</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
