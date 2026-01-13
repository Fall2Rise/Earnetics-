import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { WorkGraph } from './WorkGraph';
import { Timeline } from './Timeline';
import { ApiKeyGuardian } from './ApiKeyGuardian';
export const DepartmentBay = () => {
    const [agents, setAgents] = React.useState([]);
    React.useEffect(() => {
        // @ts-ignore
        window.api?.getAgents().then(setAgents);
        // Listen for updates
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event) => {
            if (event.type === 'SYSTEM_READY') {
                // @ts-ignore
                window.api?.getAgents().then(setAgents);
            }
        });
        return cleanup;
    }, []);
    return (_jsxs("div", { className: "flex flex-col h-full gap-4", children: [_jsxs("div", { className: "flex-1 grid grid-cols-12 gap-4 min-h-0", children: [_jsxs("div", { className: "col-span-3 bg-gray-900 rounded-lg p-4 border border-gray-800 flex flex-col", children: [_jsx("h2", { className: "text-xl font-bold mb-4 text-green-400", children: "Agent Roster" }), _jsx("div", { className: "space-y-2 overflow-y-auto flex-1 mb-4", children: agents.map(agent => (_jsxs("div", { className: "flex items-center justify-between p-2 bg-gray-800 rounded hover:bg-gray-700 cursor-pointer transition-colors", children: [_jsx("span", { className: "font-medium text-gray-200", children: agent.name }), _jsx("span", { className: `w-2 h-2 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)] ${agent.status === 'online' ? 'bg-green-500' : 'bg-gray-500'}` })] }, agent.id))) }), _jsx(ApiKeyGuardian, {})] }), _jsxs("div", { className: "col-span-6 bg-gray-900 rounded-lg border border-gray-800 flex flex-col overflow-hidden", children: [_jsxs("div", { className: "p-4 border-b border-gray-800 flex justify-between items-center", children: [_jsx("h2", { className: "text-xl font-bold text-blue-400", children: "Active Work Graph" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { 
                                                // @ts-ignore
                                                onClick: () => window.api?.sendCommand('START_REVENUE_CYCLE', {}), className: "px-3 py-1 text-xs bg-green-600 hover:bg-green-500 text-white rounded font-bold uppercase tracking-wider transition-colors", children: "Start Revenue Cycle" }), _jsx("span", { className: "text-xs text-gray-500 uppercase tracking-wider flex items-center", children: "Live View" })] })] }), _jsx("div", { className: "flex-1 relative", children: _jsx(WorkGraph, {}) })] }), _jsxs("div", { className: "col-span-3 bg-gray-900 rounded-lg p-4 border border-gray-800 flex flex-col", children: [_jsx("h2", { className: "text-xl font-bold mb-4 text-purple-400", children: "Evidence" }), _jsx("div", { className: "flex-1 flex items-center justify-center text-sm text-gray-500 italic border-2 border-dashed border-gray-800 rounded", children: "Select a node to view artifacts" })] })] }), _jsx("div", { className: "h-12 shrink-0", children: _jsx(Timeline, {}) })] }));
};
