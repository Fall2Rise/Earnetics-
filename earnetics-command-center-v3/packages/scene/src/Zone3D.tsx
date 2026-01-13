import React from 'react';
import { Text, Grid } from '@react-three/drei';
import * as THREE from 'three';

interface Zone3DProps {
    position: [number, number, number];
    name: string;
    color: string;
    description: string;
}

export const Zone3D: React.FC<Zone3DProps> = ({ position, name, color, description }) => {
    return (
        <group position={position}>
            {/* Zone Floor/Base */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
                <planeGeometry args={[6, 6]} />
                <meshStandardMaterial
                    color={color}
                    transparent
                    opacity={0.05}
                    side={THREE.DoubleSide}
                />
            </mesh>

            {/* Zone Border */}
            <Grid
                position={[0, -0.05, 0]}
                args={[6, 6]}
                sectionColor={color}
                cellColor="#1a1a1a"
                sectionThickness={1.5}
                fadeDistance={20}
                infiniteGrid={false}
            />

            {/* Zone Label */}
            <Text
                position={[0, 0.1, 3.2]}
                rotation={[-Math.PI / 2, 0, 0]}
                fontSize={0.4}
                color={color}
                anchorX="center"
                anchorY="middle"
                font="https://fonts.gstatic.com/s/orbitron/v25/y97pyUadq5YvS_26_C58xO7G.woff"
            >
                {name.toUpperCase()}
            </Text>

            {/* Corner Pillars/Markers */}
            {[[-3, -3], [3, -3], [3, 3], [-3, 3]].map(([x, z], i) => (
                <mesh key={i} position={[x, 1, z]}>
                    <boxGeometry args={[0.1, 2, 0.1]} />
                    <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} transparent opacity={0.3} />
                </mesh>
            ))}

            {/* Decorative Light Beam */}
            <mesh position={[0, 2, 0]}>
                <cylinderGeometry args={[0.5, 0.5, 4, 32]} />
                <meshStandardMaterial
                    color={color}
                    transparent
                    opacity={0.02}
                />
            </mesh>
        </group>
    );
};
