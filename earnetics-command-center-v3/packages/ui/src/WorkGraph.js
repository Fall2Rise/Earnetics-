import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge, } from 'reactflow';
import 'reactflow/dist/style.css';
const initialNodes = [
    { id: '1', position: { x: 0, y: 0 }, data: { label: 'Objective: Q4 Revenue' }, type: 'input', style: { background: '#22c55e', color: 'black', border: 'none', fontWeight: 'bold' } },
    { id: '2', position: { x: 0, y: 100 }, data: { label: 'Task: Analyze Trends' }, style: { background: '#1f2937', color: 'white', border: '1px solid #374151' } },
    { id: '3', position: { x: 200, y: 100 }, data: { label: 'Task: Launch Campaign' }, style: { background: '#1f2937', color: 'white', border: '1px solid #374151' } },
    { id: '4', position: { x: 100, y: 200 }, data: { label: 'Artifact: Report.pdf' }, type: 'output', style: { background: '#3b82f6', color: 'white', border: 'none' } },
];
const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#22c55e' } },
    { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#22c55e' } },
    { id: 'e2-4', source: '2', target: '4', style: { stroke: '#3b82f6' } },
];
export const WorkGraph = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);
    return (_jsx("div", { className: "w-full h-full bg-gray-950 rounded-lg border border-gray-800 overflow-hidden", children: _jsxs(ReactFlow, { nodes: nodes, edges: edges, onNodesChange: onNodesChange, onEdgesChange: onEdgesChange, onConnect: onConnect, fitView: true, className: "bg-gray-950", children: [_jsx(Controls, { className: "bg-gray-800 border-gray-700 fill-white" }), _jsx(MiniMap, { className: "bg-gray-900 border-gray-800", nodeColor: () => '#374151' }), _jsx(Background, { color: "#374151", gap: 16 })] }) }));
};
