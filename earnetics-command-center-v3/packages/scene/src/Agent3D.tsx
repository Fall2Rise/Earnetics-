/// <reference types="@react-three/fiber" />
import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Html } from '@react-three/drei';
import * as THREE from 'three';

interface Agent3DProps {
    position: [number, number, number];
    name: string;
    status: 'idle' | 'active' | 'error' | 'busy';
    role: string;
    onClick?: () => void;
}

export const Agent3D: React.FC<Agent3DProps> = ({ position, name, status, role, onClick }) => {
    const meshRef = useRef<THREE.Mesh>(null);
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

    return (
        <group position={position}>
            <mesh
                ref={meshRef}
                onClick={onClick}
                onPointerOver={() => setHovered(true)}
                onPointerOut={() => setHovered(false)}
            >
                <sphereGeometry args={[0.3, 32, 32]} />
                <meshStandardMaterial
                    color={getStatusColor()}
                    emissive={getStatusColor()}
                    emissiveIntensity={hovered ? 2 : 0.5}
                    transparent
                    opacity={0.8}
                />

                {/* Outer Ring */}
                <mesh rotation={[Math.PI / 2, 0, 0]}>
                    <torusGeometry args={[0.45, 0.02, 16, 100]} />
                    <meshStandardMaterial color={getStatusColor()} emissive={getStatusColor()} />
                </mesh>
            </mesh>

            {/* Name Tag */}
            <Text
                position={[0, 0.7, 0]}
                fontSize={0.2}
                color="white"
                anchorX="center"
                anchorY="middle"
                font="https://fonts.gstatic.com/s/orbitron/v25/y97pyUadq5YvS_26_C58xO7G.woff"
            >
                {name}
            </Text>

            {/* Hover Info */}
            {hovered && (
                <Html distanceFactor={10}>
                    <div className="bg-black/80 border border-white/20 p-2 rounded text-xs text-white whitespace-nowrap pointer-events-none">
                        <div className="font-bold text-[#00ff88]">{name}</div>
                        <div className="opacity-70">{role}</div>
                        <div className="mt-1 flex items-center gap-1">
                            <div className={`w-2 h-2 rounded-full bg-[${getStatusColor()}]`} />
                            <span className="capitalize">{status}</span>
                        </div>
                    </div>
                </Html>
            )}
        </group>
    );
};
