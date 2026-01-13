import React, { useState, useEffect } from 'react';
import { useSystemStore } from './stores/systemStore';
import { AgentPanel } from './components/AgentPanel';
import { MailOpsRoom } from './components/MailOpsRoom';
import { TasksRoom } from './components/TasksRoom';
import { OpsRoom } from '@earnetics/scene'; // Keep 3D room if available

function App() {
    const [viewMode, setViewMode] = useState<'3d' | 'agents' | 'mailops' | 'tasks'>('agents');
    const connect = useSystemStore((state) => state.connect);
    const isConnected = useSystemStore((state) => state.isConnected);
    const safeMode = useSystemStore((state) => state.safeMode);
    const toggleSafeMode = useSystemStore((state) => state.toggleSafeMode);

    useEffect(() => {
        connect();
    }, [connect]);

    return (
        <div className="w-screen h-screen bg-black text-white overflow-hidden flex flex-col font-mono">
            {/* Top Bar */}
            <div className="h-14 bg-slate-900 border-b border-slate-800 flex items-center px-4 justify-between z-50">
                <div className="flex items-center gap-4">
                    <h1 className="font-bold text-xl tracking-wider text-cyan-500">EARNETICS <span className="text-white">CMD</span></h1>
                    <div className="flex gap-1">
                        <button onClick={() => setViewMode('agents')} className={`px-3 py-1 rounded text-sm ${viewMode === 'agents' ? 'bg-cyan-900 text-cyan-200' : 'hover:bg-slate-800'}`}>AGENTS</button>
                        <button onClick={() => setViewMode('mailops')} className={`px-3 py-1 rounded text-sm ${viewMode === 'mailops' ? 'bg-cyan-900 text-cyan-200' : 'hover:bg-slate-800'}`}>MAILOPS</button>
                        <button onClick={() => setViewMode('tasks')} className={`px-3 py-1 rounded text-sm ${viewMode === 'tasks' ? 'bg-cyan-900 text-cyan-200' : 'hover:bg-slate-800'}`}>TASKS</button>
                        <button onClick={() => setViewMode('3d')} className={`px-3 py-1 rounded text-sm ${viewMode === '3d' ? 'bg-cyan-900 text-cyan-200' : 'hover:bg-slate-800'}`}>3D VIEW</button>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className={`px-2 py-1 rounded text-xs font-bold ${isConnected ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
                        {isConnected ? 'ONLINE' : 'OFFLINE'}
                    </div>
                    <button
                        onClick={toggleSafeMode}
                        className={`px-3 py-1 rounded text-xs font-bold border ${safeMode ? 'bg-yellow-600 border-yellow-500 text-black' : 'bg-transparent border-slate-600 text-slate-400'}`}
                    >
                        {safeMode ? 'SAFE MODE ACTIVE' : 'SAFE MODE OFF'}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 relative overflow-hidden">
                {viewMode === 'agents' && <AgentPanel />}
                {viewMode === 'mailops' && <MailOpsRoom />}
                {viewMode === 'tasks' && <TasksRoom />}
                {viewMode === '3d' && (
                    <div className="absolute inset-0">
                        <OpsRoom />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;

