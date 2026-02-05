import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface CircularPlatformProps {
  position: [number, number, number];
  radius: number;
  color: string;
  label?: string;
  gridSize?: number;
  glowIntensity?: number;
}

export const CircularPlatform: React.FC<CircularPlatformProps> = ({
  position,
  radius,
  color,
  label,
  gridSize = 5,
  glowIntensity = 1.0,
}) => {
  const platformRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (glowRef.current) {
      const time = state.clock.getElapsedTime();
      glowRef.current.rotation.z = time * 0.1;
      const pulse = Math.sin(time * 2) * 0.1 + 1;
      glowRef.current.scale.set(pulse, pulse, 1);
    }
  });

  const segments = 64;
  const edgeThickness = 0.1;

  return (
    <group position={position}>
      {/* Main platform disc */}
      <mesh ref={platformRef} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[radius, segments]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.2}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Glowing edge ring */}
      <mesh ref={glowRef} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius - edgeThickness, radius, segments]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={glowIntensity}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Grid of small cylindrical elements */}
      {Array.from({ length: gridSize }).map((_, i) => {
        const angle = (i / gridSize) * Math.PI * 2;
        const dist = radius * 0.6;
        const x = Math.cos(angle) * dist;
        const z = Math.sin(angle) * dist;
        return (
          <mesh
            key={`grid-${i}`}
            position={[x, 0.1, z]}
            rotation={[0, angle, 0]}
          >
            <cylinderGeometry args={[0.05, 0.05, 0.2, 8]} />
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={0.5}
            />
          </mesh>
        );
      })}

      {/* Central core */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[radius * 0.2, radius * 0.2, 0.3, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.8}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>
    </group>
  );
};
