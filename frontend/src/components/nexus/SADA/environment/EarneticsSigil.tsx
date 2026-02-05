import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export const EarneticsSigil: React.FC = () => {
  const outerRingRef = useRef<THREE.Group>(null);
  const innerRingRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (outerRingRef.current) {
      outerRingRef.current.rotation.z = t * 0.02; // Slow rotation
    }
    if (innerRingRef.current) {
      innerRingRef.current.rotation.z = -t * 0.05; // Counter-rotation
    }
    if (coreRef.current) {
      // Heartbeat pulse
      const scale = 1 + Math.sin(t * 1.5) * 0.02;
      coreRef.current.scale.set(scale, scale, scale);
      
      // Color pulse
      const intensity = 2 + Math.sin(t * 2) * 0.5;
      (coreRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = intensity;
    }
  });

  return (
    <group position={[0, -0.08, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      {/* Dais Base - Dark Metallic Rim */}
      <mesh position={[0, 0, -0.1]}>
        <cylinderGeometry args={[14, 15, 0.5, 64]} />
        <meshStandardMaterial color="#1a1a1a" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* Outer Golden Ring (Complex) */}
      <group ref={outerRingRef}>
        <mesh>
          <torusGeometry args={[12, 0.15, 16, 100]} />
          <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={0.5} />
        </mesh>
        {/* Decorative ticks */}
        {Array.from({ length: 12 }).map((_, i) => (
          <mesh key={i} rotation={[0, 0, (i / 12) * Math.PI * 2]} position={[12, 0, 0]}>
            <boxGeometry args={[0.5, 0.2, 0.2]} />
            <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={0.5} />
          </mesh>
        ))}
      </group>

      {/* Inner Geometric Pattern (Metatron-ish) */}
      <group ref={innerRingRef}>
        <mesh>
          <torusGeometry args={[8, 0.1, 16, 6]} /> {/* Hexagon shape */}
          <meshStandardMaterial color="#00FFFF" emissive="#00FFFF" emissiveIntensity={0.8} />
        </mesh>
        <mesh rotation={[0, 0, Math.PI / 6]}>
          <torusGeometry args={[8, 0.05, 16, 6]} />
          <meshStandardMaterial color="#00FFFF" emissive="#00FFFF" emissiveIntensity={0.4} />
        </mesh>
      </group>

      {/* Central Core - The "E" / Sigil */}
      <mesh ref={coreRef} position={[0, 0, 0.1]}>
        <octahedronGeometry args={[2.5, 0]} />
        <meshStandardMaterial 
          color="#FFD700" 
          emissive="#FFD700" 
          emissiveIntensity={2}
          wireframe
        />
      </mesh>
      
      {/* Glass Cover (The "Embedded" look) */}
      <mesh position={[0, 0, 0.2]}>
        <circleGeometry args={[13.5, 64]} />
        <meshPhysicalMaterial 
          color="#000000" 
          transmission={0.6} 
          opacity={0.3} 
          transparent 
          roughness={0} 
          metalness={0.5} 
          clearcoat={1}
        />
      </mesh>

      {/* Sub-floor Glow */}
      <pointLight position={[0, 0, 2]} distance={25} intensity={3} color="#0088ff" />
    </group>
  );
};
