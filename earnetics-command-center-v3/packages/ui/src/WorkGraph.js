import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge, } from 'reactflow';
import 'reactflow/dist/style.css';
const initialNodes = [
    { id: '1', position: { x: 0, y: 0 }, data: { label: 'Objective: Q4 Revenue' }, type: 'input', style: { background: '#22c55e', color: 'black', border: 'none', fontWeight: 'bold' } },
];
const initialEdges = [];
export const WorkGraph = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);
    React.useEffect(() => {
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event) => {
            if (event.type === 'TASK_CREATED') {
                const task = event.payload;
                const newNode = {
                    id: task.id,
                    position: { x: Math.random() * 400, y: Math.random() * 400 },
                    data: { label: `Task: ${task.title}` },
                    style: { background: '#1f2937', color: 'white', border: '1px solid #374151' }
                };
                setNodes((nds) => [...nds, newNode]);
                // Link to Objective if exists (mock logic for now)
                setEdges((eds) => [...eds, { id: `e-${task.id}`, source: '1', target: task.id, animated: true, style: { stroke: '#22c55e' } }]);
            }
        });
        return cleanup;
    }, [setNodes, setEdges]);
    return (_jsx("div", { className: "w-full h-full bg-gray-950 rounded-lg border border-gray-800 overflow-hidden", children: _jsxs(ReactFlow, { nodes: nodes, edges: edges, onNodesChange: onNodesChange, onEdgesChange: onEdgesChange, onConnect: onConnect, fitView: true, className: "bg-gray-950", children: [_jsx(Controls, { className: "bg-gray-800 border-gray-700 fill-white" }), _jsx(MiniMap, { className: "bg-gray-900 border-gray-800", nodeColor: () => '#374151' }), _jsx(Background, { color: "#374151", gap: 16 })] }) }));
};
