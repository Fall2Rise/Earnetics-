import React, { useState, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';

export const SovereignHUD: React.FC = () => {
    const { agents } = useAgentStore();
    const [time, setTime] = useState(new Date());

    // Metrics
    const activeAgents = agents.filter(a => a.status === 'active').length;
    const totalAgents = agents.length;
    const systemHealth = activeAgents > 0 ? 'OPTIMAL' : 'STANDBY';

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-6 z-20 overflow-hidden">

            {/* TOP HEADER */}
            <div className="flex justify-between items-start">
                {/* Left: System Identity */}
                <div className="bg-black/80 backdrop-blur-md border border-cyan-500/30 p-4 rounded-tl-xl rounded-br-xl pointer-events-auto">
                    <h1 className="text-2xl font-bold text-cyan-400 tracking-[0.2em] glow-text">
                        EARNETICS NEXUS
                    </h1>
                    <div className="flex gap-4 mt-2 text-xs font-mono text-cyan-700">
                        <span>SECTOR: PRIME</span>
                        <span>AUTH: SOVEREIGN</span>
                        <span>{time.toLocaleTimeString()}</span>
                    </div>
                </div>

                {/* Right: Threat/Status */}
                <div className="flex gap-2">
                    <div className="bg-black/80 backdrop-blur-md border border-cyan-500/30 p-2 px-4 rounded pointer-events-auto">
                        <div className="text-[10px] text-cyan-600 uppercase">System Status</div>
                        <div className={`text-lg font-bold ${systemHealth === 'OPTIMAL' ? 'text-green-400' : 'text-yellow-400'}`}>
                            {systemHealth}
                        </div>
                    </div>
                    <div className="bg-black/80 backdrop-blur-md border border-red-500/30 p-2 px-4 rounded pointer-events-auto">
                        <div className="text-[10px] text-red-600 uppercase">Threat Level</div>
                        <div className="text-lg font-bold text-red-500 animate-pulse">
                            DEFCON 5
                        </div>
                    </div>
                </div>
            </div>

            {/* CENTER: Crosshair (Subtle) */}
            <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
                <div className="w-[500px] h-[500px] border border-cyan-500/20 rounded-full"></div>
                <div className="absolute w-full h-px bg-cyan-500/10"></div>
                <div className="absolute h-full w-px bg-cyan-500/10"></div>
            </div>

            {/* BOTTOM FOOTER */}
            <div className="flex justify-between items-end">
                {/* Left: Agent Roster Summary */}
                <div className="bg-black/80 backdrop-blur-md border border-cyan-500/30 p-4 rounded-tr-xl rounded-bl-xl pointer-events-auto w-64">
                    <div className="text-xs text-cyan-500 font-bold mb-2 border-b border-cyan-900 pb-1">
                        ACTIVE ASSETS [{activeAgents}/{totalAgents}]
                    </div>
                    <div className="space-y-1 max-h-32 overflow-y-auto scrollbar-hide">
                        {agents.filter(a => a.status === 'active').map(agent => (
                            <div key={agent.id} className="flex justify-between text-[10px] font-mono">
                                <span className="text-cyan-300">{agent.name}</span>
                                <span className="text-cyan-700">{agent.department.split(' ')[0]}</span>
                            </div>
                        ))}
                        {activeAgents === 0 && (
                            <div className="text-[10px] text-gray-500 italic">No active operations...</div>
                        )}
                    </div>
                </div>

                {/* Right: Fallat Seal / Cryptosigner */}
                <div className="flex flex-col items-end gap-2 pointer-events-auto">
                    <div className="text-[10px] text-cyan-800 font-mono">
                        ENCRYPTION: ED25519-GCM // VERIFIED
                    </div>
                    <div className="w-16 h-16 border-2 border-cyan-500/50 rounded-full flex items-center justify-center bg-black/50 backdrop-blur-md hover:border-cyan-400 transition-colors cursor-pointer group">
                        <div className="w-10 h-10 border border-cyan-500/30 rotate-45 group-hover:rotate-90 transition-transform duration-500"></div>
                    </div>
                </div>
            </div>
        </div>
    );
};
