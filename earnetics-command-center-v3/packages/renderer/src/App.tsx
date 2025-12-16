import React, { useState, useEffect } from 'react';
import { OpsRoom } from '@earnetics/scene';
import { DepartmentBay } from '@earnetics/ui';

function App() {
    const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
    const [events, setEvents] = useState<any[]>([]);

    useEffect(() => {
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event: any) => {
            console.log('New Event:', event);
            setEvents(prev => [...prev, event]);
        });
        return cleanup;
    }, []);

    return (
        <div className="w-screen h-screen bg-black text-white overflow-hidden flex flex-col">
            {/* Top Bar */}
            <div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 justify-between z-50">
                <h1 className="font-bold text-lg tracking-wider text-green-500">EARNETICS <span className="text-white">V3</span></h1>
                <div className="flex gap-2">
                    <button
                        onClick={() => setViewMode('3d')}
                        className={`px-3 py-1 rounded ${viewMode === '3d' ? 'bg-green-600' : 'bg-gray-800'}`}
                    >
                        Ops Room (3D)
                    </button>
                    <button
                        onClick={() => setViewMode('2d')}
                        className={`px-3 py-1 rounded ${viewMode === '2d' ? 'bg-blue-600' : 'bg-gray-800'}`}
                    >
                        Dept Bay (2D)
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 relative">
                {viewMode === '3d' && (
                    <div className="absolute inset-0">
                        <OpsRoom />
                    </div>
                )}

                {viewMode === '2d' && (
                    <div className="absolute inset-0 bg-gray-950 p-4">
                        <DepartmentBay />
                    </div>
                )}
            </div>

            {/* Bottom Rail */}
            <div className="h-8 bg-gray-900 border-t border-gray-800 flex items-center px-4 text-xs text-gray-400">
                <span>Status: ONLINE</span>
                <span className="mx-2">|</span>
                <span>Events: {events.length}</span>
            </div>
        </div>
    );
}

export default App;
