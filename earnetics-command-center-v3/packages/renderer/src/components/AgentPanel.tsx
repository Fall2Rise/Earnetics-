import React, { useEffect, useState } from 'react';
import { useSystemStore } from '../stores/systemStore';

export const AgentPanel: React.FC = () => {
    const [roster, setRoster] = useState<any[]>([]);
    const logs = useSystemStore((state) => state.logs);
    const agentPaused = useSystemStore((state) => state.agentPaused);
    const toggleAgentPaused = useSystemStore((state) => state.toggleAgentPaused);

    useEffect(() => {
        const fetchRoster = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/agents/roster`);
                const data = await res.json();
                setRoster(data.agents || []);
            } catch (e) {
                console.error('Failed to fetch roster', e);
            }
        };
        fetchRoster();
        const interval = setInterval(fetchRoster, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-4 bg-slate-900 text-white h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Agent Command</h2>
                <button
                    onClick={toggleAgentPaused}
                    className={`px-4 py-2 rounded ${agentPaused ? 'bg-red-600' : 'bg-green-600'}`}
                >
                    {agentPaused ? 'RESUME ALL' : 'PAUSE ALL'}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {roster.map((agent) => (
                    <div key={agent.name} className="bg-slate-800 p-4 rounded border border-slate-700">
                        <h3 className="font-bold text-lg">{agent.name}</h3>
                        <p className="text-sm text-slate-400">{agent.role}</p>
                        <div className="mt-2 text-xs">
                            <span className={`px-2 py-1 rounded ${agent.health === 'operational' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                                {agent.health}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <h3 className="text-lg font-bold mb-2">Live Neural Logs</h3>
            <div className="bg-black p-2 rounded h-64 overflow-y-auto font-mono text-xs">
                {logs.map((log, i) => (
                    <div key={i} className="mb-1 border-b border-slate-800 pb-1">
                        <span className="text-slate-500">[{log.timestamp}]</span>{' '}
                        <span className="text-cyan-400">{log.agent || 'SYSTEM'}</span>:{' '}
                        <span className="text-slate-300">{log.message}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};
