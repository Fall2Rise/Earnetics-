import React, { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

interface GlowingPegProps {
  position: [number, number, number];
  color: string;
  size?: number;
  intensity?: number;
}

/**
 * Individual glowing peg/node that pulses and glows
 * Used to populate department zones
 */
export const GlowingPeg: React.FC<GlowingPegProps> = ({
  position,
  color,
  size = 0.18,
  intensity = 1.2,
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  const baseMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#0b1320',
      metalness: 0.7,
      roughness: 0.35,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  const material = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: intensity,
      metalness: 0.8,
      roughness: 0.25,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color, intensity]);

  const glowMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: intensity * 0.5,
      transparent: true,
      opacity: 0.4,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color, intensity]);

  useFrame((state) => {
    if (meshRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 3 + position[0] + position[2]) * 0.1 + 1;
      meshRef.current.scale.setScalar(pulse);
    }
    if (glowRef.current) {
      const glowPulse = Math.sin(state.clock.elapsedTime * 2 + position[0] + position[2]) * 0.2 + 1;
      glowRef.current.scale.setScalar(glowPulse);
    }
  });

  return (
    <group position={position}>
      {/* Base */}
      <mesh position={[0, -size * 0.6, 0]}>
        <cylinderGeometry args={[size * 0.9, size * 1.05, size * 0.6, 12]} />
        <primitive object={baseMaterial} attach="material" />
      </mesh>

      {/* Main peg */}
      <mesh ref={meshRef}>
        <cylinderGeometry args={[size * 0.75, size * 0.75, size * 2.2, 12]} />
        <primitive object={material} attach="material" />
      </mesh>

      {/* Glow effect */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[size * 1.6, 10, 10]} />
        <primitive object={glowMaterial} attach="material" />
      </mesh>

      {/* Always-visible top cap */}
      <mesh position={[0, size * 0.9, 0]}>
        <sphereGeometry args={[size * 0.5, 10, 10]} />
        <meshBasicMaterial color={color} transparent opacity={0.8} />
      </mesh>

    </group>
  );
};
