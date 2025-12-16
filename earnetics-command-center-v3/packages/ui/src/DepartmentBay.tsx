import React from 'react';
import { WorkGraph } from './WorkGraph';
import { Timeline } from './Timeline';
import { ApiKeyGuardian } from './ApiKeyGuardian';

export const DepartmentBay = () => {
    const [agents, setAgents] = React.useState<any[]>([]);

    React.useEffect(() => {
        // @ts-ignore
        window.api?.getAgents().then(setAgents);

        // Listen for updates
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event: any) => {
            if (event.type === 'SYSTEM_READY') {
                // @ts-ignore
                window.api?.getAgents().then(setAgents);
            }
        });
        return cleanup;
    }, []);

    return (
        <div className="flex flex-col h-full gap-4">
            <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
                {/* Left: Agent Roster */}
                <div className="col-span-3 bg-gray-900 rounded-lg p-4 border border-gray-800 flex flex-col">
                    <h2 className="text-xl font-bold mb-4 text-green-400">Agent Roster</h2>
                    <div className="space-y-2 overflow-y-auto flex-1 mb-4">
                        {agents.map(agent => (
                            <div key={agent.id} className="flex items-center justify-between p-2 bg-gray-800 rounded hover:bg-gray-700 cursor-pointer transition-colors">
                                <span className="font-medium text-gray-200">{agent.name}</span>
                                <span className={`w-2 h-2 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)] ${agent.status === 'online' ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                            </div>
                        ))}
                    </div>

                    {/* Security Module */}
                    <ApiKeyGuardian />
                </div>

                {/* Center: Work Graph */}
                <div className="col-span-6 bg-gray-900 rounded-lg border border-gray-800 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-gray-800 flex justify-between items-center">
                        <h2 className="text-xl font-bold text-blue-400">Active Work Graph</h2>
                        <div className="flex gap-2">
                            <button
                                // @ts-ignore
                                onClick={() => window.api?.sendCommand('START_REVENUE_CYCLE', {})}
                                className="px-3 py-1 text-xs bg-green-600 hover:bg-green-500 text-white rounded font-bold uppercase tracking-wider transition-colors"
                            >
                                Start Revenue Cycle
                            </button>
                            <span className="text-xs text-gray-500 uppercase tracking-wider flex items-center">Live View</span>
                        </div>
                    </div>
                    <div className="flex-1 relative">
                        <WorkGraph />
                    </div>
                </div>

                {/* Right: Evidence Drawer */}
                <div className="col-span-3 bg-gray-900 rounded-lg p-4 border border-gray-800 flex flex-col">
                    <h2 className="text-xl font-bold mb-4 text-purple-400">Evidence</h2>
                    <div className="flex-1 flex items-center justify-center text-sm text-gray-500 italic border-2 border-dashed border-gray-800 rounded">
                        Select a node to view artifacts
                    </div>
                </div>
            </div>

            {/* Bottom: Timeline */}
            <div className="h-12 shrink-0">
                <Timeline />
            </div>
        </div>
    );
};
