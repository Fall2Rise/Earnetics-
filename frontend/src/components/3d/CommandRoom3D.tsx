import React, { Suspense, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Html, Grid, Environment } from '@react-three/drei';
import * as THREE from 'three';
// XR imports removed - causing WebGL context creation issues
// import { XR, createXRStore } from '@react-three/xr';
import { ExecutiveBridge } from './ExecutiveBridge';
import { DepartmentZoneNew } from './DepartmentZoneNew';
import { HolographicPanel } from './HolographicPanel';
// // import { ParticleBackground } from './ParticleBackground';
import { ConnectionLines } from './ConnectionLines';
import { DataStream } from './DataStream';
import { ActivityBurst } from './ActivityBurst';
import { FloatingMetric } from './FloatingMetrics';
import { WorkflowTrail } from './WorkflowTrail';
import { SceneLighting } from './effects/SceneLighting';
import { PostFX } from './effects/PostFX';
import { CameraRig, CameraRigRef } from './effects/CameraRig';
import { Grid, Environment } from '@react-three/drei';
import { TopDashboard } from './TopDashboard';
import { AgentInspector } from './AgentInspector';
import { EventLog } from './EventLog';
import { ObsidianVault } from './ObsidianVault';
import { KnowledgeVaultModal } from '../dashboard/KnowledgeVaultModal';
import { fetchPendingWorkflows, WorkflowTask } from '../../api/workflowsApi';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';

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

// XR Store - only create if VR is actually needed to avoid WebGL context issues
// const xrStore = createXRStore();

// CameraController removed - replaced by CameraRig component

type DebugFlags = {
    environment: boolean;
    starBackdrop: boolean;
    lighting: boolean;
    particles: boolean;
    connectionLines: boolean;
    dataStreams: boolean;
    workflows: boolean;
    activityBursts: boolean;
    metrics: boolean;
    zones: boolean;
    holograms: boolean;
    executiveBridge: boolean;
    postFX: boolean;
};

const DEFAULT_DEBUG_FLAGS: DebugFlags = {
    environment: true,
    starBackdrop: true,
    lighting: true,
    particles: false,
    connectionLines: true,
    dataStreams: true,
    workflows: true,
    activityBursts: true,
    metrics: true,
    zones: true,
    holograms: true,
    executiveBridge: true,
    postFX: true, // ENSURE THIS IS TRUE
};

const Scene: React.FC<{ cameraRigRef?: React.RefObject<CameraRigRef>; vrEnabled?: boolean; debugFlags?: DebugFlags; quality?: 'low' | 'high' }> = ({ cameraRigRef, vrEnabled = false, debugFlags, quality = 'low' }) => {
    const { selectedAgent, selectAgent, selectedDepartment, selectDepartment, getAgentsByDepartment, agents } = useAgentStore();
    const [showVault, setShowVault] = React.useState(false);
    const [recentActivity, setRecentActivity] = React.useState<Array<{ agent: string; position: [number, number, number]; color: string; time: number }>>([]);
    const [workflowTasks, setWorkflowTasks] = React.useState<WorkflowTask[]>([]);
    const [systemStatus, setSystemStatus] = React.useState<SystemStatusResponse | null>(null);
    const getSafeColor = (color?: string) => color || '#00d4ff';
    const flags = debugFlags ?? DEFAULT_DEBUG_FLAGS;

    const hashString = React.useCallback((value: string) => {
        let hash = 0;
        for (let i = 0; i < value.length; i += 1) {
            hash = (hash << 5) - hash + value.charCodeAt(i);
            hash |= 0;
        }
        return Math.abs(hash);
    }, []);

    const zoneByDepartment = React.useMemo(() => {
        const map = new Map<string, typeof DEPARTMENT_ZONES[number]>();
        DEPARTMENT_ZONES.forEach((zone) => {
            map.set(zone.department.toLowerCase(), zone);
        });
        return map;
    }, []);

    const renderAgents = React.useMemo(() => {
        const grouped = new Map<string, Agent[]>();
        agents.forEach((agent) => {
            const key = agent.department?.toLowerCase() || 'unknown';
            const list = grouped.get(key) ?? [];
            list.push(agent);
            grouped.set(key, list);
        });

        const positioned: Agent[] = [];
        grouped.forEach((list, deptKey) => {
            const zone = zoneByDepartment.get(deptKey);
            const sorted = [...list].sort((a, b) => a.id.localeCompare(b.id));
            sorted.forEach((agent, index) => {
                if (!zone) {
                    positioned.push(agent);
                    return;
                }
                const base = zone.position;
                const hash = hashString(agent.id);
                const angle = (hash % 360) * (Math.PI / 180);
                const ring = 1.2 + (index % 3) * 0.7;
                const position: [number, number, number] = [
                    base[0] + Math.cos(angle) * ring,
                    base[1] + 0.6,
                    base[2] + Math.sin(angle) * ring,
                ];
                positioned.push({ ...agent, position });
            });
        });
        return positioned;
    }, [agents, hashString, zoneByDepartment]);

    const selectedAgentRender = React.useMemo(() => {
        if (!selectedAgent) return null;
        return renderAgents.find((agent) => agent.id === selectedAgent.id) ?? selectedAgent;
    }, [renderAgents, selectedAgent]);

    const getAgentsForDepartment = React.useCallback(
        (department: string) => renderAgents.filter((agent) => agent.department === department),
        [renderAgents]
    );

    // Listen for agent activity to create bursts
    React.useEffect(() => {
        const socket = useAgentStore.getState().socket;
        if (!socket) return;

        const handleActivity = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'agent_thinking' || data.type === 'agent_action') {
                    const agentName = data.agent?.toLowerCase();
                    const agent = renderAgents.find(a => a.name.toLowerCase() === agentName);
                    if (agent) {
                        setRecentActivity(prev => [
                            { agent: agent.name, position: agent.position, color: getSafeColor(agent.color), time: Date.now() },
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
    }, [renderAgents]);

    React.useEffect(() => {
        let isMounted = true;
        const controller = new AbortController();

        const loadWorkflows = async () => {
            try {
                const response = await fetchPendingWorkflows(controller.signal);
                if (!isMounted) return;
                setWorkflowTasks(response.workflows || []);
            } catch {
                if (!isMounted) return;
                setWorkflowTasks([]);
            }
        };

        void loadWorkflows();
        const intervalId = setInterval(loadWorkflows, 15000);

        return () => {
            isMounted = false;
            controller.abort();
            clearInterval(intervalId);
        };
    }, []);

    React.useEffect(() => {
        let isMounted = true;
        const controller = new AbortController();

        const loadStatus = async () => {
            try {
                const response = await fetchSystemStatus();
                if (!isMounted) return;
                setSystemStatus(response);
            } catch {
                if (!isMounted) return;
                setSystemStatus(null);
            }
        };

        void loadStatus();
        const intervalId = setInterval(loadStatus, 20000);

        return () => {
            isMounted = false;
            controller.abort();
            clearInterval(intervalId);
        };
    }, []);

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
    const uptimeHours = systemStatus?.metrics?.uptime_hours ?? 0;
    const totalRequests = systemStatus?.metrics?.total_requests ?? 0;
    const totalRevenue = systemStatus?.metrics?.total_revenue ?? 0;

    const workflowTrails = React.useMemo(() => {
        if (!workflowTasks.length) return [];
        const center: [number, number, number] = [0, 0.6, 0];
        return workflowTasks
            .map((task) => {
                const zone = zoneByDepartment.get(task.department.toLowerCase());
                if (!zone) return null;
                return {
                    from: center,
                    to: zone.position,
                    color: zone.color,
                    progress: 1,
                };
            })
            .filter(Boolean) as Array<{ from: [number, number, number]; to: [number, number, number]; progress: number; color: string }>;
    }, [workflowTasks, zoneByDepartment]);

    const workflowStreams = React.useMemo(() => {
        if (!workflowTasks.length || renderAgents.length === 0) return [];
        return workflowTasks
            .map((task) => {
                if (!task.assigned_agent) return null;
                const agent = renderAgents.find((a) => a.id.toLowerCase() === task.assigned_agent?.toLowerCase());
                const zone = zoneByDepartment.get(task.department.toLowerCase());
                if (!agent || !zone) return null;
                return {
                    from: agent.position,
                    to: zone.position,
                    color: getSafeColor(agent.color),
                };
            })
            .filter(Boolean) as Array<{ from: [number, number, number]; to: [number, number, number]; color: string }>;
    }, [workflowTasks, renderAgents, zoneByDepartment]);

    return (
        <>
            {/* Environment shell (does not affect agent positions) */}
            {flags.environment && (
                <>
                    <CommandDeckShell showGrid={false} />
                    {/* Add Industrial Grid Floor */}
                    <Grid 
                        position={[0, -0.1, 0]} 
                        args={[150, 150]} 
                        cellSize={2} 
                        cellThickness={0.5} 
                        cellColor="#1a1a1a" 
                        sectionSize={10} 
                        sectionThickness={1} 
                        sectionColor="#333333" 
                        fadeDistance={60} 
                        fadeStrength={1}
                        infiniteGrid
                    />
                    <Environment preset="city" />
                    <fog attach="fog" args={['#050505', 20, 90]} />
                    <color attach="background" args={['#050505']} />
                </>
            )}
            
            {/* StarBackdrop REMOVED - User requested "Factory" not "Space" */}
            {/* {flags.starBackdrop && <StarBackdrop enabled={true} />} */}

            {/* Cinematic lighting setup */}
            {flags.lighting && <SceneLighting quality={quality} />}

            {/* {flags.particles && <ParticleBackground />} */}

            {/* Connection lines between agents and departments */}
            {flags.connectionLines && <ConnectionLines agents={renderAgents} departments={DEPARTMENT_ZONES} />}

            {/* Data streams between active agents */}
            {flags.dataStreams && workflowStreams.map((stream, idx) => (
                <DataStream
                    key={`stream-${idx}`}
                    from={stream.from}
                    to={stream.to}
                    color={stream.color}
                    speed={1.2}
                />
            ))}

            {/* Workflow trails */}
            {flags.workflows && workflowTrails.map((workflow, idx) => (
                <WorkflowTrail
                    key={`workflow-${idx}`}
                    from={workflow.from}
                    to={workflow.to}
                    color={workflow.color}
                    progress={workflow.progress}
                />
            ))}

            {/* Activity bursts */}
            {flags.activityBursts && recentActivity.map((activity, idx) => (
                <ActivityBurst
                    key={`burst-${activity.agent}-${activity.time}-${idx}`}
                    position={activity.position}
                    color={activity.color}
                    intensity={1.5}
                    duration={1}
                />
            ))}

            {/* Floating metrics */}
            {flags.metrics && (
                <>
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
                    <FloatingMetric
                        position={[0, 12, -10]}
                        label="Uptime"
                        value={`${uptimeHours}h`}
                        color="#9ae6ff"
                    />
                    <FloatingMetric
                        position={[-12, 10, -8]}
                        label="Requests"
                        value={totalRequests}
                        color="#38bdf8"
                    />
                    <FloatingMetric
                        position={[12, 10, -8]}
                        label="Revenue"
                        value={`$${totalRevenue.toFixed(0)}`}
                        color="#f59e0b"
                        trend={totalRevenue > 0 ? 'up' : 'neutral'}
                    />
                </>
            )}

            {/* Central Executive Bridge */}
            {flags.executiveBridge && <ExecutiveBridge position={[0, 0, 0]} />}

            {/* Department Zones - updated hex zones with pegs and seated agents */}
            {flags.zones && DEPARTMENT_ZONES.map((zone) => (
                <DepartmentZoneNew
                    key={zone.department}
                    department={zone.department}
                    agents={getAgentsForDepartment(zone.department)}
                    position={zone.position}
                    scale={zone.scale}
                    color={zone.color}
                    onZoneClick={() => selectDepartment(zone.department)}
                    onAgentClick={(agent) => selectAgent(agent)}
                />
            ))}

            {flags.holograms && selectedAgentRender && (
                <HolographicPanel
                    agent={selectedAgentRender}
                    onClose={() => selectAgent(null)}
                    position={[
                        selectedAgentRender.position[0],
                        selectedAgentRender.position[1] + 3,
                        selectedAgentRender.position[2]
                    ]}
                />
            )}

            {/* Floating Obsidian Knowledge Vault */}
            <ObsidianVault 
                position={[0, 16, 0]} 
                onClick={() => setShowVault(true)}
            />

            {/* Knowledge Vault Modal Overlay */}
            {showVault && (
                <Html position={[0, 0, 0]} fullscreen style={{ pointerEvents: 'none', zIndex: 100 }}>
                    <div style={{ pointerEvents: 'auto', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <KnowledgeVaultModal onClose={() => setShowVault(false)} />
                    </div>
                </Html>
            )}

            {/* Camera rig and post-processing only in non-VR mode */}
            {!vrEnabled && (
                <>
                    <CameraRig ref={cameraRigRef} targetAgent={selectedAgentRender} enableFocus={true} />
                    {flags.postFX && (
                        <Suspense fallback={null}>
                            <PostFX />
                        </Suspense>
                    )}
                </>
            )}
        </>
    );
};

export const CommandRoom3D: React.FC<{ vrEnabled?: boolean }> = ({ vrEnabled = false }) => {
    const cameraRigRef = useRef<CameraRigRef>(null);
    const { selectedAgent, selectAgent } = useAgentStore();
    const [webglError, setWebglError] = React.useState<string | null>(null);
    const [retryKey, setRetryKey] = React.useState(0); // Force re-render on retry
    const [debugOpen, setDebugOpen] = React.useState(false);
    const [debugFlags, setDebugFlags] = React.useState<DebugFlags>(DEFAULT_DEBUG_FLAGS);
    const [quality, setQuality] = React.useState<'low' | 'high'>('low');
    const [webglSupported] = React.useState(() => {
        try {
            if (typeof document === 'undefined') return false;
            const canvas = document.createElement('canvas');
            const gl =
                canvas.getContext('webgl2') ||
                canvas.getContext('webgl') ||
                canvas.getContext('experimental-webgl');
            return !!gl;
        } catch {
            return false;
        }
    });

    // Check WebGL support with better detection and diagnostics
    React.useEffect(() => {
        const checkWebGL = () => {
            try {
                const canvas = document.createElement('canvas');
                // Try WebGL2 first, then WebGL1
                let gl: WebGLRenderingContext | WebGL2RenderingContext | null = null;
                let errorInfo: string[] = [];
                
                // Try WebGL2
                try {
                    gl = canvas.getContext('webgl2', {
                        failIfMajorPerformanceCaveat: false,
                        powerPreference: 'default',
                    } as any) as WebGL2RenderingContext | null;
                    if (gl) {
                        console.log('[CommandRoom3D] WebGL2 available');
                    }
                } catch (e) {
                    errorInfo.push(`WebGL2: ${e instanceof Error ? e.message : String(e)}`);
                }
                
                // Try WebGL1
                if (!gl) {
                    try {
                        gl = canvas.getContext('webgl', {
                            failIfMajorPerformanceCaveat: false,
                            powerPreference: 'default',
                        } as any) as WebGLRenderingContext | null;
                        if (gl) {
                            console.log('[CommandRoom3D] WebGL1 available');
                        }
                    } catch (e) {
                        errorInfo.push(`WebGL1: ${e instanceof Error ? e.message : String(e)}`);
                    }
                }
                
                // Try experimental-webgl
                if (!gl) {
                    try {
                        gl = canvas.getContext('experimental-webgl') as WebGLRenderingContext | null;
                        if (gl) {
                            console.log('[CommandRoom3D] Experimental WebGL available');
                        }
                    } catch (e) {
                        errorInfo.push(`Experimental WebGL: ${e instanceof Error ? e.message : String(e)}`);
                    }
                }
                
                if (!gl) {
                    // Get more diagnostic info
                    const diagnostics = [
                        `User Agent: ${navigator.userAgent}`,
                        `Platform: ${navigator.platform}`,
                        `Hardware Concurrency: ${navigator.hardwareConcurrency || 'unknown'}`,
                        `Errors: ${errorInfo.join(', ')}`,
                    ];
                    console.error('[CommandRoom3D] WebGL not available:', diagnostics);
                    
                    setWebglError(`WebGL is not available.\n\nDiagnostics:\n${diagnostics.join('\n')}\n\nPossible fixes:\n1. Open chrome://flags (or edge://flags)\n2. Search for "WebGL"\n3. Enable:\n   • WebGL Draft Extensions\n   • WebGL 2.0 Compute\n   • Hardware-accelerated video decode\n4. Restart browser\n5. Check if any extensions are blocking WebGL`);
                } else {
                    // WebGL is available, log info and clear errors
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        console.log('[CommandRoom3D] WebGL Info:', {
                            vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                            renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL),
                        });
                    }
                    setWebglError(null);
                }
            } catch (e) {
                console.error('[CommandRoom3D] WebGL check error:', e);
                setWebglError('Error checking WebGL support: ' + (e instanceof Error ? e.message : String(e)));
            }
        };
        
        // Delay check slightly to ensure DOM is ready
        const timeoutId = setTimeout(checkWebGL, 100);
        return () => clearTimeout(timeoutId);
    }, []);

    const handleSendCommand = (command: string) => {
        console.log('[CommandRoom3D] Sending command to agent:', selectedAgent?.name, command);
        // TODO: Implement command sending to backend
    };

    // Show fallback UI if WebGL is not available
    if (!webglSupported || webglError) {
        const message =
            webglError ||
            'WebGL is not available in this browser/device. Enable hardware acceleration and ensure your GPU driver is active.';
        return (
            <div className="w-full h-full bg-black rounded-xl overflow-hidden relative flex items-center justify-center">
                <div className="text-center p-8 bg-slate-900/50 rounded-xl border border-red-500/30 max-w-3xl max-h-[90vh] overflow-y-auto">
                    <h2 className="text-2xl font-bold text-red-400 mb-4">⚠️ WebGL Not Available</h2>
                    <div className="text-left text-sm text-white/80 mb-6 whitespace-pre-wrap font-mono bg-black/30 p-4 rounded border border-red-500/20">
                        {message}
                    </div>
                    <div className="text-left text-sm text-white/60 space-y-3">
                        <div>
                            <p className="font-bold text-white mb-2">Quick Fixes:</p>
                            <ol className="list-decimal list-inside space-y-1 ml-2">
                                <li>Open <code className="bg-black/50 px-2 py-1 rounded">chrome://flags</code> (or <code className="bg-black/50 px-2 py-1 rounded">edge://flags</code>)</li>
                                <li>Search for "WebGL"</li>
                                <li>Enable these flags:
                                    <ul className="list-disc list-inside ml-6 mt-1">
                                        <li>WebGL Draft Extensions</li>
                                        <li>WebGL 2.0 Compute</li>
                                        <li>Hardware-accelerated video decode</li>
                                    </ul>
                                </li>
                                <li>Restart your browser completely</li>
                                <li>Check browser console (F12) for more details</li>
                            </ol>
                        </div>
                        <div className="mt-4 pt-4 border-t border-white/10">
                            <p className="font-bold text-white mb-2">Test WebGL directly:</p>
                            <p className="text-xs text-white/50 mb-2">Open browser console (F12) and run:</p>
                            <code className="block bg-black/50 px-2 py-1 rounded mt-1 text-xs mb-3">
                                const c = document.createElement('canvas'); const gl = c.getContext('webgl'); console.log(gl ? 'WebGL OK' : 'WebGL FAILED');
                            </code>
                            <button
                                onClick={() => {
                                    setWebglError(null);
                                    setRetryKey(prev => prev + 1);
                                    // Re-check WebGL after a short delay
                                    setTimeout(() => {
                                        const canvas = document.createElement('canvas');
                                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                                        if (!gl) {
                                            setWebglError('WebGL still not available. Please check browser flags and restart browser.');
                                        }
                                    }, 500);
                                }}
                                className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold transition-colors"
                            >
                                🔄 Retry WebGL Initialization
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-black rounded-xl overflow-hidden relative">
            {/* Top Dashboard Bar */}
            <TopDashboard />
            <button
                type="button"
                onClick={() => setDebugOpen(prev => !prev)}
                className="absolute top-20 right-4 z-30 px-3 py-1 text-xs rounded border border-cyan-500/50 bg-black/70 text-cyan-200 hover:bg-cyan-950/60"
            >
                Debug Toggles
            </button>
            {debugOpen && (
                <div className="absolute top-28 right-4 z-30 bg-black/85 border border-cyan-500/30 rounded p-3 text-xs text-white/80 space-y-2 w-56">
                    <div className="font-semibold text-cyan-300">Scene Layers</div>
                    {Object.entries(debugFlags).map(([key, value]) => (
                        <label key={key} className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) => {
                                    setDebugFlags(prev => ({ ...prev, [key]: e.target.checked }));
                                }}
                            />
                            <span className="capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                        </label>
                    ))}
                    <div className="pt-2 border-t border-white/10 flex gap-2">
                        <button
                            type="button"
                            className="px-2 py-1 text-xs rounded border border-white/20 hover:bg-white/10"
                            onClick={() => setDebugFlags(DEFAULT_DEBUG_FLAGS)}
                        >
                            Reset
                        </button>
                        <button
                            type="button"
                            className="px-2 py-1 text-xs rounded border border-white/20 hover:bg-white/10"
                            onClick={() => {
                                const offFlags = Object.keys(debugFlags).reduce((acc, k) => {
                                    acc[k as keyof DebugFlags] = false;
                                    return acc;
                                }, {} as DebugFlags);
                                setDebugFlags(offFlags);
                            }}
                        >
                            All Off
                        </button>
                    </div>
                    <div className="pt-2 border-t border-white/10 flex items-center justify-between">
                        <span className="text-cyan-200/70">Quality</span>
                        <button
                            type="button"
                            className="px-2 py-1 text-xs rounded border border-cyan-500/40 bg-cyan-500/10 hover:bg-cyan-500/20"
                            onClick={() => setQuality(prev => (prev === 'low' ? 'high' : 'low'))}
                        >
                            {quality.toUpperCase()}
                        </button>
                    </div>
                </div>
            )}

            {/* 3D Canvas */}
            <div className="absolute top-16 bottom-24 left-0 right-0 bg-gradient-to-b from-black via-slate-950 to-black" key={retryKey}>
                <Canvas 
                    shadows={quality === 'high'}
                    dpr={quality === 'high' ? [1, 1.5] : [1, 1]}
                    camera={{ position: [0, 18, 26], fov: 45 }}
                    gl={{ 
                        preserveDrawingBuffer: false,
                        antialias: quality === 'high',
                        powerPreference: quality === 'high' ? "high-performance" : "low-power",
                        failIfMajorPerformanceCaveat: false,
                        stencil: false, // Disable stencil buffer
                        depth: true,
                        alpha: false, // Disable alpha for better compatibility
                        // Try to work around sandboxing issues
                        xrCompatible: false, // Disable XR compatibility
                        desynchronized: false,
                    } as any}
                    onError={(error) => {
                        console.error('[CommandRoom3D] Canvas error:', error);
                        const errorMsg = error?.message || String(error);
                        setWebglError(`Failed to initialize 3D canvas: ${errorMsg}\n\nThis might be due to:\n• Browser security settings blocking WebGL\n• Graphics driver issues\n• Browser extensions blocking WebGL\n• WebGL disabled in browser flags\n\nTry: chrome://flags → Search "WebGL" → Enable all WebGL options`);
                    }}
                    onCreated={({ gl, scene }) => {
                        console.log('[CommandRoom3D] Canvas created successfully');
                        try {
                            const webglContext = gl.getContext();
                            if (webglContext) {
                                const debugInfo = webglContext.getExtension('WEBGL_debug_renderer_info');
                                if (debugInfo) {
                                    console.log('[CommandRoom3D] WebGL Info:', {
                                        vendor: webglContext.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                                        renderer: webglContext.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL),
                                        version: webglContext.getParameter(webglContext.VERSION),
                                    });
                                }
                            }
                        } catch (e) {
                            console.warn('[CommandRoom3D] Could not get WebGL debug info:', e);
                        }
                        gl.setClearColor('#000000', 1);
                        gl.toneMapping = THREE.ACESFilmicToneMapping;
                        gl.toneMappingExposure = 1.4;
                        gl.outputColorSpace = THREE.SRGBColorSpace;
                        setWebglError(null); // Clear any previous errors
                        
                        // Handle WebGL context loss
                        const canvas = gl.domElement;
                        canvas.addEventListener('webglcontextlost', (event) => {
                            event.preventDefault();
                            console.warn('[CommandRoom3D] WebGL context lost, attempting to restore...');
                            setWebglError('WebGL context was lost. Please refresh the page.');
                        });
                        canvas.addEventListener('webglcontextrestored', () => {
                            console.log('[CommandRoom3D] WebGL context restored');
                            setWebglError(null);
                        });
                    }}
                >
                    {/* VR disabled temporarily due to WebGL context issues */}
                    <Suspense fallback={null}>
                        <Scene cameraRigRef={cameraRigRef} vrEnabled={false} debugFlags={debugFlags} />
                    </Suspense>
                </Canvas>
            </div>
            
            {/* Agent Inspector Overlay */}
            {selectedAgent && (
                <AgentInspector 
                    agent={selectedAgent}
                    onClose={() => selectAgent(null)}
                />
            )}

            {/* Event Log at Bottom */}
            <EventLog />

            {/* Reset View Button - only in non-VR mode */}
            {!vrEnabled && (
                <button
                    onClick={() => cameraRigRef.current?.resetView()}
                    className="absolute top-20 right-4 z-10 bg-black/80 backdrop-blur-xl px-4 py-2 rounded-lg border border-cyan-500/50 text-cyan-300 text-xs font-bold hover:bg-black/90 hover:border-cyan-500 transition-all pointer-events-auto"
                    title="Reset camera to default view"
                >
                    Reset View
                </button>
            )}
        </div>
    );
};
