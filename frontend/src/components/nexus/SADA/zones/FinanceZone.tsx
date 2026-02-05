import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

export const FinanceZone: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  const streamRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (streamRef.current) {
      streamRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.2;
    }
  });

  return (
    <group position={position}>
      {/* Zone Marker */}
      <mesh position={[0, 0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[4, 4.2, 32]} />
        <meshBasicMaterial color="#00D4FF" transparent opacity={0.3} />
      </mesh>

      {/* Floating Data Streams (Pipelines) */}
      <group ref={streamRef} position={[0, 2, 0]}>
        {Array.from({ length: 5 }).map((_, i) => (
          <mesh key={i} position={[Math.sin(i) * 2, i * 0.5, Math.cos(i) * 2]}>
            <boxGeometry args={[0.2, 0.2, 0.2]} />
            <meshStandardMaterial color="#00D4FF" emissive="#00D4FF" emissiveIntensity={2} />
          </mesh>
        ))}
      </group>

      {/* Label (HTML to avoid crash) */}
      <Html position={[0, 4, 0]} center distanceFactor={15}>
        <div className="text-cyan-400 font-bold text-sm tracking-widest whitespace-nowrap bg-black/50 backdrop-blur-sm px-2 py-1 border border-cyan-500/30 rounded">
          FINANCE & REVENUE
        </div>
      </Html>
    </group>
  );
};
