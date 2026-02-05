import React, { useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

interface ExecutiveBridgeProps {
  position?: [number, number, number];
}

/**
 * Central Executive Bridge - the glowing blue core with seated executive figures
 * Matches the reference design with circular structure and glowing energy core
 */
export const ExecutiveBridge: React.FC<ExecutiveBridgeProps> = ({ 
  position = [0, 0, 0] 
}) => {
  const coreRef = React.useRef<THREE.Mesh>(null);
  const glowRef = React.useRef<THREE.Mesh>(null);

  // Animate the core glow
  useFrame((state) => {
    if (coreRef.current) {
      coreRef.current.rotation.y += 0.002;
    }
    if (glowRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.1 + 1;
      glowRef.current.scale.setScalar(pulse);
    }
  });

  // Glowing blue material for core
  const coreMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#00D4FF',
      emissive: '#00D4FF',
      emissiveIntensity: 1.5,
      metalness: 0.8,
      roughness: 0.2,
    });
    // Ensure uniforms are initialized
    mat.needsUpdate = true;
    return mat;
  }, []);

  // Outer glow material
  const glowMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#00D4FF',
      emissive: '#00D4FF',
      emissiveIntensity: 1.0,
      transparent: true,
      opacity: 0.45,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  // Desk material for executive seats
  const deskMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#0b1a2a',
      emissive: '#00D4FF',
      emissiveIntensity: 0.25,
      metalness: 0.6,
      roughness: 0.4,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  const baseMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#0b1422',
      metalness: 0.8,
      roughness: 0.35,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  const rimMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#ffb84a',
      emissive: '#ffb84a',
      emissiveIntensity: 0.7,
      metalness: 0.4,
      roughness: 0.2,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  // Executive figure material (glowing blue)
  const executiveMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#00D4FF',
      emissive: '#00D4FF',
      emissiveIntensity: 1.2,
      metalness: 0.7,
      roughness: 0.3,
    });
    mat.needsUpdate = true;
    return mat;
  }, []);

  // Create 10 executive seats around the core
  const seatPositions = useMemo(() => {
    const radius = 4.2;
    const seats = 10;
    return Array.from({ length: seats }, (_, i) => {
      const angle = (i / seats) * Math.PI * 2;
      return {
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        angle: angle + Math.PI / 2, // Face inward
      };
    });
  }, []);

  return (
    <group position={position}>
      {/* Warm rim light */}
      <pointLight position={[0, 4, 0]} intensity={0.9} distance={30} color="#31d4ff" />
      <pointLight position={[3, 3, 3]} intensity={0.55} distance={18} color="#ffb84a" />

      {/* Central glowing core pillar */}
      <mesh ref={coreRef} position={[0, 2, 0]}>
        <cylinderGeometry args={[0.8, 0.8, 4, 32]} />
        <primitive object={coreMaterial} attach="material" />
      </mesh>

      {/* Outer glow ring */}
      <mesh ref={glowRef} position={[0, 2, 0]}>
        <torusGeometry args={[1.2, 0.15, 16, 32]} />
        <primitive object={glowMaterial} attach="material" />
      </mesh>

      {/* Inner ring */}
      <mesh position={[0, 0.8, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.2, 0.08, 16, 64]} />
        <primitive object={rimMaterial} attach="material" />
      </mesh>
      {/* Mid ring */}
      <mesh position={[0, 0.82, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3.2, 0.05, 16, 64]} />
        <primitive object={coreMaterial} attach="material" />
      </mesh>

      {/* Base platform */}
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[6.4, 6.4, 0.35, 48]} />
        <primitive object={baseMaterial} attach="material" />
      </mesh>

      {/* Rim ring */}
      <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[6.0, 6.4, 64]} />
        <primitive object={rimMaterial} attach="material" />
      </mesh>
      {/* Outer accent ring */}
      <mesh position={[0, 0.04, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[6.6, 6.9, 64]} />
        <primitive object={glowMaterial} attach="material" />
      </mesh>

      {/* Executive seats with figures */}
      {seatPositions.map((seat, idx) => (
        <group key={`exec-seat-${idx}`} position={[seat.x, 0.1, seat.z]}>
          {/* Desk */}
          <mesh rotation={[-Math.PI / 2, seat.angle, 0]} position={[0, 0.3, 0]}>
            <boxGeometry args={[1.2, 0.1, 0.8]} />
            <primitive object={deskMaterial} attach="material" />
          </mesh>

          {/* Seated executive figure (simplified glowing form) */}
          <group position={[0, 0.5, 0]} rotation={[0, seat.angle, 0]}>
            {/* Body */}
            <mesh position={[0, 0.3, 0]}>
              <boxGeometry args={[0.4, 0.6, 0.3]} />
              <primitive object={executiveMaterial} attach="material" />
            </mesh>
            {/* Head */}
            <mesh position={[0, 0.7, 0]}>
              <sphereGeometry args={[0.2, 16, 16]} />
              <primitive object={executiveMaterial} attach="material" />
            </mesh>
            {/* Glow effect */}
            <mesh position={[0, 0.5, 0]}>
              <sphereGeometry args={[0.5, 16, 16]} />
              <primitive object={glowMaterial} attach="material" />
            </mesh>
          </group>
        </group>
      ))}

      {/* Label - removed to prevent material issues */}
    </group>
  );
};
