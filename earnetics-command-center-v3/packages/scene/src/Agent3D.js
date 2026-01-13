import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Html } from '@react-three/drei';
export const Agent3D = ({ position, name, status, role, onClick }) => {
    const meshRef = useRef(null);
    const [hovered, setHovered] = useState(false);
    // Color based on status
    const getStatusColor = () => {
        switch (status) {
            case 'active': return '#00ff88'; // Neon Green
            case 'error': return '#ff0000'; // Red
            case 'busy': return '#ffaa00'; // Amber
            default: return '#0080ff'; // Cyber Blue
        }
    };
    useFrame((state) => {
        if (meshRef.current) {
            // Subtle floating animation
            meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * 0.1;
            // Rotation
            meshRef.current.rotation.y += 0.01;
        }
    });
    return (_jsxs("group", { position: position, children: [_jsxs("mesh", { ref: meshRef, onClick: onClick, onPointerOver: () => setHovered(true), onPointerOut: () => setHovered(false), children: [_jsx("sphereGeometry", { args: [0.3, 32, 32] }), _jsx("meshStandardMaterial", { color: getStatusColor(), emissive: getStatusColor(), emissiveIntensity: hovered ? 2 : 0.5, transparent: true, opacity: 0.8 }), _jsxs("mesh", { rotation: [Math.PI / 2, 0, 0], children: [_jsx("torusGeometry", { args: [0.45, 0.02, 16, 100] }), _jsx("meshStandardMaterial", { color: getStatusColor(), emissive: getStatusColor() })] })] }), _jsx(Text, { position: [0, 0.7, 0], fontSize: 0.2, color: "white", anchorX: "center", anchorY: "middle", font: "https://fonts.gstatic.com/s/orbitron/v25/y97pyUadq5YvS_26_C58xO7G.woff", children: name }), hovered && (_jsx(Html, { distanceFactor: 10, children: _jsxs("div", { className: "bg-black/80 border border-white/20 p-2 rounded text-xs text-white whitespace-nowrap pointer-events-none", children: [_jsx("div", { className: "font-bold text-[#00ff88]", children: name }), _jsx("div", { className: "opacity-70", children: role }), _jsxs("div", { className: "mt-1 flex items-center gap-1", children: [_jsx("div", { className: `w-2 h-2 rounded-full bg-[${getStatusColor()}]` }), _jsx("span", { className: "capitalize", children: status })] })] }) }))] }));
};
