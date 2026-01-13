import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars, Float } from '@react-three/drei';
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
const CommandDeck = () => {
    const [agents, setAgents] = useState(MOCK_AGENTS);
    const [selectedAgent, setSelectedAgent] = useState(null);
    useEffect(() => {
        // @ts-ignore
        if (window.api?.getAgents) {
            // @ts-ignore
            window.api.getAgents().then((data) => {
                if (data && data.length > 0)
                    setAgents(data);
            });
        }
        // @ts-ignore
        const cleanup = window.api?.onNewEvent?.((event) => {
            if (event.type === 'AGENT_STATUS_CHANGE') {
                setAgents(prev => prev.map(a => a.id === event.agentId ? { ...a, status: event.status } : a));
            }
        });
        return cleanup;
    }, []);
    return (_jsxs("group", { children: [_jsxs(Float, { speed: 2, rotationIntensity: 0.5, floatIntensity: 0.5, children: [_jsxs("mesh", { position: [0, 2, 0], children: [_jsx("octahedronGeometry", { args: [2, 0] }), _jsx("meshStandardMaterial", { color: "#00ff88", wireframe: true, transparent: true, opacity: 0.2 })] }), _jsxs("mesh", { position: [0, 2, 0], children: [_jsx("sphereGeometry", { args: [0.8, 32, 32] }), _jsx("meshStandardMaterial", { color: "#00ff88", emissive: "#00ff88", emissiveIntensity: 1 })] })] }), ZONES.map((zone, i) => {
                const angle = (i / ZONES.length) * Math.PI * 2;
                const radius = 12;
                const x = Math.cos(angle) * radius;
                const z = Math.sin(angle) * radius;
                return (_jsxs("group", { children: [_jsx(Zone3D, { position: [x, 0, z], name: zone.name, color: zone.color, description: zone.description }), agents.filter(a => a.zone === zone.id).map((agent, ai, filtered) => {
                            const agentAngle = (ai / filtered.length) * Math.PI * 2;
                            const agentRadius = 2;
                            const ax = x + Math.cos(agentAngle) * agentRadius;
                            const az = z + Math.sin(agentAngle) * agentRadius;
                            return (_jsx(Agent3D, { position: [ax, 1, az], name: agent.name, role: agent.role, status: agent.status, onClick: () => setSelectedAgent(agent.id) }, agent.id));
                        })] }, zone.id));
            })] }));
};
export const OpsRoom = () => {
    return (_jsxs("div", { className: "w-full h-full bg-[#050505] relative", children: [_jsxs(Canvas, { shadows: true, children: [_jsx(PerspectiveCamera, { makeDefault: true, position: [20, 20, 20], fov: 50 }), _jsx(OrbitControls, { enableDamping: true, dampingFactor: 0.05, maxPolarAngle: Math.PI / 2.1, minDistance: 5, maxDistance: 50 }), _jsx("ambientLight", { intensity: 0.4 }), _jsx("pointLight", { position: [10, 10, 10], intensity: 1.5, castShadow: true }), _jsx("spotLight", { position: [0, 20, 0], angle: 0.3, penumbra: 1, intensity: 2, castShadow: true, color: "#00ff88" }), _jsx(Stars, { radius: 100, depth: 50, count: 7000, factor: 4, saturation: 0, fade: true, speed: 1 }), _jsx(CommandDeck, {})] }), _jsxs("div", { className: "absolute top-6 left-6 pointer-events-none", children: [_jsx("h1", { className: "text-4xl font-bold text-[#00ff88] tracking-tighter", style: { fontFamily: 'Orbitron, sans-serif' }, children: "EARNETICS COMMAND CENTER" }), _jsx("p", { className: "text-white/40 text-sm font-mono mt-1", children: "SYSTEM STATUS: OPTIMAL // AUTONOMY ACTIVE" })] }), _jsx("div", { className: "absolute bottom-6 right-6 flex flex-col gap-2 items-end", children: _jsxs("div", { className: "bg-black/60 backdrop-blur-md border border-white/10 p-4 rounded-lg", children: [_jsx("div", { className: "text-xs text-white/50 mb-2 uppercase tracking-widest", children: "Active Divisions" }), _jsx("div", { className: "grid grid-cols-3 gap-4", children: ZONES.map(z => (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-2 h-2 rounded-full", style: { backgroundColor: z.color } }), _jsx("span", { className: "text-[10px] text-white/80 whitespace-nowrap", children: z.name })] }, z.id))) })] }) })] }));
};
