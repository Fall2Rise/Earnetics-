import React, { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';

interface SeatedAgentProps {
  position: [number, number, number];
  color: string;
  rotation?: number;
  label?: string;
  scale?: number;
  onClick?: () => void;
}

/**
 * Seated agent figure at a desk - glowing figure representation
 * Used in department zones to show active agents
 */
export const SeatedAgent: React.FC<SeatedAgentProps> = ({
  position,
  color,
  rotation = 0,
  label,
  scale = 1,
  onClick,
}) => {
  const groupRef = useRef<THREE.Group>(null);

  const agentMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 1.0,
      metalness: 0.7,
      roughness: 0.3,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  const deskMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#1a1a2e',
      emissive: color,
      emissiveIntensity: 0.1,
      metalness: 0.5,
      roughness: 0.5,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  const glowMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 0.6,
      transparent: true,
      opacity: 0.28,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  useFrame((state) => {
    if (groupRef.current) {
      // Subtle breathing animation
      const breathe = Math.sin(state.clock.elapsedTime * 2) * 0.05 + 1;
      groupRef.current.scale.y = breathe;
    }
  });

  return (
    <group
      ref={groupRef}
      position={position}
      rotation={[0, rotation, 0]}
      scale={[scale, scale, scale]}
      onClick={(event) => {
        event.stopPropagation();
        onClick?.();
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        if (onClick) {
          document.body.style.cursor = 'pointer';
        }
      }}
      onPointerOut={(event) => {
        event.stopPropagation();
        document.body.style.cursor = 'default';
      }}
    >
      {/* Desk */}
      <mesh position={[0, 0.18, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <boxGeometry args={[0.85, 0.12, 0.65]} />
        <primitive object={deskMaterial} attach="material" />
      </mesh>

      {/* Seated figure */}
      <group position={[0, 0.4, 0]}>
        {/* Body */}
        <mesh position={[0, 0.2, 0]}>
          <boxGeometry args={[0.3, 0.4, 0.25]} />
          <primitive object={agentMaterial} attach="material" />
        </mesh>

        {/* Head */}
        <mesh position={[0, 0.5, 0]}>
          <sphereGeometry args={[0.15, 12, 12]} />
          <primitive object={agentMaterial} attach="material" />
        </mesh>

        {/* Glow aura */}
        <mesh position={[0, 0.4, 0]}>
          <sphereGeometry args={[0.46, 16, 16]} />
          <primitive object={glowMaterial} attach="material" />
        </mesh>
      </group>

      {/* Halo ring */}
      <mesh position={[0, 0.65, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.35, 0.03, 8, 32]} />
        <primitive object={glowMaterial} attach="material" />
      </mesh>

      {/* Label if provided */}
      {label && (
        <Html position={[0, 1.0, 0]} center>
          <div
            style={{
              background: 'rgba(6, 12, 24, 0.7)',
              border: `1px solid ${color}66`,
              boxShadow: `0 0 10px ${color}55`,
              color: '#e6f6ff',
              padding: '2px 6px',
              borderRadius: '6px',
              fontSize: '9px',
              whiteSpace: 'nowrap',
            }}
          >
            {label}
          </div>
        </Html>
      )}
    </group>
  );
};
