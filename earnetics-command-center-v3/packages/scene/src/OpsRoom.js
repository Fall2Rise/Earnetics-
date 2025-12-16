import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars, Grid } from '@react-three/drei';
const HoloTable = () => {
    const meshRef = useRef(null);
    useFrame((state, delta) => {
        if (meshRef.current) {
            meshRef.current.rotation.y += delta * 0.1;
        }
    });
    return (_jsxs("group", { position: [0, 0, 0], children: [_jsxs("mesh", { position: [0, -0.5, 0], children: [_jsx("cylinderGeometry", { args: [4, 4, 0.5, 32] }), _jsx("meshStandardMaterial", { color: "#1a1a1a", metalness: 0.8, roughness: 0.2 })] }), _jsxs("mesh", { ref: meshRef, position: [0, 1, 0], children: [_jsx("sphereGeometry", { args: [1.5, 32, 32] }), _jsx("meshStandardMaterial", { color: "#00ff88", wireframe: true, transparent: true, opacity: 0.3 })] }), [0, 1, 2, 3, 4].map((i) => {
                const angle = (i / 5) * Math.PI * 2;
                const x = Math.cos(angle) * 3;
                const z = Math.sin(angle) * 3;
                return (_jsxs("mesh", { position: [x, 0.5, z], children: [_jsx("sphereGeometry", { args: [0.3, 16, 16] }), _jsx("meshStandardMaterial", { color: "#0080ff", emissive: "#0080ff", emissiveIntensity: 0.5 })] }, i));
            })] }));
};
export const OpsRoom = () => {
    return (_jsx("div", { className: "w-full h-full bg-black", children: _jsxs(Canvas, { children: [_jsx(PerspectiveCamera, { makeDefault: true, position: [0, 5, 10] }), _jsx(OrbitControls, { enablePan: false, maxPolarAngle: Math.PI / 2 }), _jsx("ambientLight", { intensity: 0.2 }), _jsx("pointLight", { position: [10, 10, 10], intensity: 1 }), _jsx("spotLight", { position: [0, 10, 0], angle: 0.5, penumbra: 1, intensity: 2, castShadow: true }), _jsx(Stars, { radius: 100, depth: 50, count: 5000, factor: 4, saturation: 0, fade: true, speed: 1 }), _jsx(Grid, { infiniteGrid: true, fadeDistance: 30, sectionColor: "#00ff88", cellColor: "#1a1a1a" }), _jsx(HoloTable, {})] }) }));
};
