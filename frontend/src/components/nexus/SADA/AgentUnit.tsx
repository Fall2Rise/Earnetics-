import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Html } from '@react-three/drei';
import * as THREE from 'three';

interface AgentUnitProps {
    position: [number, number, number];
    name: string;
    role: string;
    status: 'active' | 'idle' | 'alert';
    onClick?: () => void;
}

export const AgentUnit: React.FC<AgentUnitProps> = ({ position, name, role, status, onClick }) => {
    const meshRef = useRef<THREE.Group>(null);
    const [hovered, setHovered] = useState(false);

    // Status colors
    const colors = {
        active: '#00ffaa', // Cyan/Green
        idle: '#445566',   // Blue/Grey
        alert: '#ff3333'   // Red
    };

    const color = colors[status];

    useFrame((state) => {
        if (meshRef.current) {
            // Gentle floating animation
            meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * 0.1;
            // Slow rotation
            meshRef.current.rotation.y += 0.01;
        }
    });

    return (
        <group
            ref={meshRef}
            position={position}
            onClick={onClick}
            onPointerOver={() => setHovered(true)}
            onPointerOut={() => setHovered(false)}
        >
            {/* The "Soul" Core */}
            <mesh>
                <capsuleGeometry args={[0.3, 1, 4, 8]} />
                <meshStandardMaterial
                    color={color}
                    emissive={color}
                    emissiveIntensity={hovered ? 2 : 1}
                    roughness={0.2}
                    metalness={0.8}
                />
            </mesh>

            {/* Status Ring */}
            <mesh position={[0, -0.6, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <ringGeometry args={[0.4, 0.45, 32]} />
                <meshBasicMaterial color={color} transparent opacity={0.5} />
            </mesh>

            {/* Floating Label (HTML) */}
            <Html position={[0, 1.2, 0]} center distanceFactor={10} zIndexRange={[100, 0]}>
                <div className="flex flex-col items-center pointer-events-none whitespace-nowrap">
                    <span className="text-xs font-bold text-white tracking-widest drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)]">
                        {name.toUpperCase()}
                    </span>
                    <span className="text-[8px] font-mono mt-0.5 px-1 rounded bg-black/50 backdrop-blur-sm" style={{ color: color }}>
                        {role.toUpperCase()}
                    </span>
                </div>
            </Html>

            {/* Hover Info Card (HTML Overlay) */}
            {hovered && (
                <Html position={[1, 1, 0]} distanceFactor={10}>
                    <div className="bg-black/90 border border-cyan-500 p-2 rounded w-32 backdrop-blur-md">
                        <div className="text-[8px] text-cyan-500 uppercase tracking-wider">Status</div>
                        <div className="text-xs font-bold text-white mb-1">{status.toUpperCase()}</div>
                        <div className="h-px bg-cyan-900 my-1" />
                        <div className="text-[8px] text-gray-400">Click for details</div>
                    </div>
                </Html>
            )}
        </group>
    );
};
