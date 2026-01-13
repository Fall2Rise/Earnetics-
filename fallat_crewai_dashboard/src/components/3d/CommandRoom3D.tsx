import React, { Suspense, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { XR, createXRStore } from '@react-three/xr';
import { DivisionalZone } from './DivisionalZone';
import { HolographicPanel } from './HolographicPanel';
import { ParticleBackground } from './ParticleBackground';
import { ConnectionLines } from './ConnectionLines';
import { DataStream } from './DataStream';
import { ActivityBurst } from './ActivityBurst';
import { FloatingMetric } from './FloatingMetrics';
import { WorkflowTrail } from './WorkflowTrail';
import { SceneLighting } from './effects/SceneLighting';
import { PostFX } from './effects/PostFX';
import { CameraRig, CameraRigRef } from './effects/CameraRig';
import { CommandDeckShell } from './environment/CommandDeckShell';
import { StarBackdrop } from './environment/StarBackdrop';
import { useAgentStore, Agent } from '../../stores/agentStore';

const DEPARTMENT_ZONES = [
    {
        department: 'Executive Board',
        position: [0, 2, 0] as [number, number, number],
        scale: [4, 3, 4] as [number, number, number],
        color: '#FFD700',
    },
    // Main cardinal directions - spaced at 18 units (much larger separation)
    {
        department: 'Finance & Revenue',
        position: [18, 0, 0] as [number, number, number],
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#00D4FF',
    },
    {
        department: 'Creative & Product',
        position: [-18, 0, 0] as [number, number, number],
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#FF1493',
    },
    {
        department: 'Tech & Infrastructure',
        position: [0, 0, 18] as [number, number, number],
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#00FFFF',
    },
    {
        department: 'Legal & Sovereignty',
        position: [0, 0, -18] as [number, number, number],
        scale: [4, 2, 4] as [number, number, number],
        color: '#FFA500',
    },
    // Diagonal positions - spaced at 14 units with 45-degree angles for better separation
    {
        department: 'Health & Human Factor',
        position: [12.7, 0, 12.7] as [number, number, number], // 18 * cos(45°) ≈ 12.7
        scale: [3, 2, 3] as [number, number, number],
        color: '#FF6B9D',
    },
    {
        department: 'Corporate Analytics',
        position: [-12.7, 0, 12.7] as [number, number, number],
        scale: [3, 2, 3] as [number, number, number],
        color: '#9D4EDD',
    },
    {
        department: 'Corporate Execution',
        position: [12.7, 0, -12.7] as [number, number, number],
        scale: [6, 2.5, 6] as [number, number, number],
        color: '#10B981',
    },
    {
        department: 'Email Marketing',
        position: [-12.7, 0, -12.7] as [number, number, number],
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#F59E0B',
    },
    // Revenue departments - positioned at intermediate angles (22.5° offsets) at 20 units
    {
        department: 'Revenue Strategy Cell',
        position: [-18.5, 0, 7.7] as [number, number, number], // 20 units at 157.5° angle
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#9333EA',
    },
    {
        department: 'Revenue Execution',
        position: [18.5, 0, -7.7] as [number, number, number], // 20 units at 22.5° angle
        scale: [6, 2.5, 6] as [number, number, number],
        color: '#EF4444',
    },
    {
        department: 'Lead Generation & Acquisition',
        position: [-7.7, 0, 18.5] as [number, number, number], // 20 units at 112.5° angle
        scale: [5, 2.5, 5] as [number, number, number],
        color: '#06B6D4',
    },
    {
        department: 'Website Growth & Digital Presence',
        position: [7.7, 0, -18.5] as [number, number, number], // 20 units at -67.5° angle
        scale: [6, 2.5, 6] as [number, number, number],
        color: '#8B5CF6',
    },
];

// Debug: Log department count on module load
console.log(`[CommandRoom3D] DEPARTMENT_ZONES initialized with ${DEPARTMENT_ZONES.length} departments:`, DEPARTMENT_ZONES.map(z => z.department));

const xrStore = createXRStore();

// CameraController removed - replaced by CameraRig component

const Scene: React.FC<{ cameraRigRef?: React.RefObject<CameraRigRef>; vrEnabled?: boolean }> = ({ cameraRigRef, vrEnabled = false }) => {
    const { selectedAgent, selectAgent, selectedDepartment, selectDepartment, getAgentsByDepartment, agents } = useAgentStore();
    const [recentActivity, setRecentActivity] = React.useState<Array<{ agent: string; position: [number, number, number]; color: string; time: number }>>([]);
    const [workflows, setWorkflows] = React.useState<Array<{ from: [number, number, number]; to: [number, number, number]; progress: number; color: string }>>([]);

    // Listen for agent activity to create bursts
    React.useEffect(() => {
        const socket = useAgentStore.getState().socket;
        if (!socket) return;

        const handleActivity = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'agent_thinking' || data.type === 'agent_action') {
                    const agentName = data.agent?.toLowerCase();
                    const agent = agents.find(a => a.name.toLowerCase() === agentName);
                    if (agent) {
                        setRecentActivity(prev => [
                            { agent: agent.name, position: agent.position, color: agent.color, time: Date.now() },
                            ...prev.slice(0, 9) // Keep last 10
                        ]);
                    }
                }
            } catch (e) {
                // Ignore parse errors
            }
        };

        if (socket.readyState === WebSocket.OPEN) {
            socket.addEventListener('message', handleActivity);
        } else {
            socket.addEventListener('open', () => {
                socket.addEventListener('message', handleActivity);
            }, { once: true });
        }

        return () => {
            if (socket) {
                socket.removeEventListener('message', handleActivity);
            }
        };
    }, [agents]);

    // Create workflow trails between departments
    React.useEffect(() => {
        const activeAgents = agents.filter(a => a.status === 'active');
        if (activeAgents.length < 2) {
            setWorkflows([]);
            return;
        }

        const newWorkflows: Array<{ from: [number, number, number]; to: [number, number, number]; progress: number; color: string }> = [];
        
        // Create workflows between departments
        const departments = Array.from(new Set(activeAgents.map(a => a.department)));
        for (let i = 0; i < departments.length - 1; i++) {
            const dept1 = departments[i];
            const dept2 = departments[i + 1];
            const agent1 = activeAgents.find(a => a.department === dept1);
            const agent2 = activeAgents.find(a => a.department === dept2);
            
            if (agent1 && agent2) {
                newWorkflows.push({
                    from: agent1.position,
                    to: agent2.position,
                    progress: Math.random(),
                    color: agent1.color,
                });
            }
        }
        
        setWorkflows(newWorkflows);
        
        // Animate workflow progress
        const interval = setInterval(() => {
            setWorkflows(prev => prev.map(w => ({
                ...w,
                progress: (w.progress + 0.01) % 1
            })));
        }, 100);
        
        return () => clearInterval(interval);
    }, [agents]);

    // Clean up old activity bursts
    React.useEffect(() => {
        const interval = setInterval(() => {
            setRecentActivity(prev => prev.filter(a => Date.now() - a.time < 2000));
        }, 500);
        return () => clearInterval(interval);
    }, []);

    // Calculate metrics for floating displays
    const activeCount = agents.filter(a => a.status === 'active').length;
    const totalPerformance = agents.reduce((sum, a) => sum + (a.performance || 0), 0);
    const avgPerformance = agents.length > 0 ? Math.round(totalPerformance / agents.length) : 0;

    return (
        <>
            {/* Environment shell (does not affect agent positions) */}
            <CommandDeckShell showGrid={true} />
            <StarBackdrop enabled={true} />

            {/* Cinematic lighting setup */}
            <SceneLighting />

            <ParticleBackground />

            {/* Connection lines between agents and departments */}
            <ConnectionLines agents={agents} departments={DEPARTMENT_ZONES} />

            {/* Data streams between active agents */}
            {agents.filter(a => a.status === 'active').slice(0, 5).map((agent, idx) => {
                const nextAgent = agents.find(a => a.status === 'active' && a.id !== agent.id && a.department !== agent.department);
                if (!nextAgent) return null;
                return (
                    <DataStream
                        key={`stream-${agent.id}-${idx}`}
                        from={agent.position}
                        to={nextAgent.position}
                        color={agent.color}
                        speed={1.5 + Math.random() * 0.5}
                    />
                );
            })}

            {/* Workflow trails */}
            {workflows.map((workflow, idx) => (
                <WorkflowTrail
                    key={`workflow-${idx}`}
                    from={workflow.from}
                    to={workflow.to}
                    color={workflow.color}
                    progress={workflow.progress}
                />
            ))}

            {/* Activity bursts */}
            {recentActivity.map((activity, idx) => (
                <ActivityBurst
                    key={`burst-${activity.agent}-${activity.time}-${idx}`}
                    position={activity.position}
                    color={activity.color}
                    intensity={1.5}
                    duration={1}
                />
            ))}

            {/* Floating metrics */}
            <FloatingMetric
                position={[0, 15, 0]}
                label="Active Agents"
                value={activeCount}
                color="#00ff88"
                trend={activeCount > agents.length / 2 ? 'up' : 'neutral'}
            />
            <FloatingMetric
                position={[-10, 12, 0]}
                label="Total Agents"
                value={agents.length}
                color="#00d4ff"
            />
            <FloatingMetric
                position={[10, 12, 0]}
                label="Performance"
                value={`${avgPerformance}%`}
                color="#ff1493"
                trend="up"
            />

            {DEPARTMENT_ZONES.map((zone) => (
                <DivisionalZone
                    key={zone.department}
                    department={zone.department}
                    agents={getAgentsByDepartment(zone.department)}
                    position={zone.position}
                    scale={zone.scale}
                    color={zone.color}
                    onAgentClick={selectAgent}
                    selectedAgent={selectedAgent}
                    onZoneClick={selectDepartment}
                />
            ))}

            {selectedAgent && (
                <HolographicPanel
                    agent={selectedAgent}
                    onClose={() => selectAgent(null)}
                    position={[
                        selectedAgent.position[0],
                        selectedAgent.position[1] + 3,
                        selectedAgent.position[2]
                    ]}
                />
            )}

            {/* Camera rig and post-processing only in non-VR mode */}
            {!vrEnabled && (
                <>
                    <CameraRig ref={cameraRigRef} targetAgent={selectedAgent} enableFocus={true} />
                    <PostFX />
                </>
            )}
        </>
    );
};

export const CommandRoom3D: React.FC<{ vrEnabled?: boolean }> = ({ vrEnabled = false }) => {
    const cameraRigRef = useRef<CameraRigRef>(null);

    return (
        <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-cyan-500/20 relative">
            <Canvas 
                shadows
                dpr={[1, 1.5]}
                camera={{ position: [0, 24, 42], fov: 55 }}
                gl={{ 
                    preserveDrawingBuffer: false,
                    antialias: true,
                    powerPreference: "high-performance",
                    failIfMajorPerformanceCaveat: false,
                }}
                onCreated={({ gl }) => {
                    // Handle WebGL context loss
                    const canvas = gl.domElement;
                    canvas.addEventListener('webglcontextlost', (event) => {
                        event.preventDefault();
                        console.warn('[CommandRoom3D] WebGL context lost, attempting to restore...');
                    });
                    canvas.addEventListener('webglcontextrestored', () => {
                        console.log('[CommandRoom3D] WebGL context restored');
                    });
                }}
            >
                {vrEnabled ? (
                    <XR store={xrStore}>
                        <Suspense fallback={null}>
                            <Scene cameraRigRef={cameraRigRef} vrEnabled={true} />
                        </Suspense>
                    </XR>
                ) : (
                    <Suspense fallback={null}>
                        <Scene cameraRigRef={cameraRigRef} vrEnabled={false} />
                    </Suspense>
                )}
            </Canvas>
            
            {/* Reset View Button - only in non-VR mode */}
            {!vrEnabled && (
                <button
                    onClick={() => cameraRigRef.current?.resetView()}
                    className="absolute top-4 right-4 z-10 bg-black/80 backdrop-blur-xl px-4 py-2 rounded-lg border border-cyan-500/50 text-cyan-300 text-xs font-bold hover:bg-black/90 hover:border-cyan-500 transition-all pointer-events-auto"
                    title="Reset camera to default view"
                >
                    Reset View
                </button>
            )}
        </div>
    );
};
