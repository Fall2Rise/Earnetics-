import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

export const LegalZone: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  const scrollRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (scrollRef.current) {
      scrollRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
    }
  });

  return (
    <group position={position}>
      {/* Zone Marker */}
      <mesh position={[0, 0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[4, 4.2, 32]} />
        <meshBasicMaterial color="#FFA500" transparent opacity={0.3} />
      </mesh>

      {/* Floating Scrolls/Blueprints */}
      <group ref={scrollRef} position={[0, 2, 0]}>
        <mesh position={[0, 0, 0]} rotation={[0, 0, Math.PI / 6]}>
          <planeGeometry args={[1.5, 2]} />
          <meshStandardMaterial color="#FFA500" transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      </group>

      {/* Label (HTML to avoid crash) */}
      <Html position={[0, 4, 0]} center distanceFactor={15}>
        <div className="text-orange-400 font-bold text-sm tracking-widest whitespace-nowrap bg-black/50 backdrop-blur-sm px-2 py-1 border border-orange-500/30 rounded">
          LEGAL & SOVEREIGNTY
        </div>
      </Html>
    </group>
  );
};
