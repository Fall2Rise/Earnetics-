import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { OpsRoom } from '@earnetics/scene';
import { DepartmentBay } from '@earnetics/ui';
function App() {
    const [viewMode, setViewMode] = useState('3d');
    const [events, setEvents] = useState([]);
    useEffect(() => {
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event) => {
            console.log('New Event:', event);
            setEvents(prev => [...prev, event]);
        });
        return cleanup;
    }, []);
    return (_jsxs("div", { className: "w-screen h-screen bg-black text-white overflow-hidden flex flex-col", children: [_jsxs("div", { className: "h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 justify-between z-50", children: [_jsxs("h1", { className: "font-bold text-lg tracking-wider text-green-500", children: ["EARNETICS ", _jsx("span", { className: "text-white", children: "V3" })] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => setViewMode('3d'), className: `px-3 py-1 rounded ${viewMode === '3d' ? 'bg-green-600' : 'bg-gray-800'}`, children: "Ops Room (3D)" }), _jsx("button", { onClick: () => setViewMode('2d'), className: `px-3 py-1 rounded ${viewMode === '2d' ? 'bg-blue-600' : 'bg-gray-800'}`, children: "Dept Bay (2D)" })] })] }), _jsxs("div", { className: "flex-1 relative", children: [viewMode === '3d' && (_jsx("div", { className: "absolute inset-0", children: _jsx(OpsRoom, {}) })), viewMode === '2d' && (_jsx("div", { className: "absolute inset-0 bg-gray-950 p-4", children: _jsx(DepartmentBay, {}) }))] }), _jsxs("div", { className: "h-8 bg-gray-900 border-t border-gray-800 flex items-center px-4 text-xs text-gray-400", children: [_jsx("span", { children: "Status: ONLINE" }), _jsx("span", { className: "mx-2", children: "|" }), _jsxs("span", { children: ["Events: ", events.length] })] })] }));
}
export default App;
