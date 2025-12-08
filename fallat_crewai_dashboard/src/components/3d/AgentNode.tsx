import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';

interface AgentNodeProps {
  agent: Agent;
  onClick: () => void;
  isSelected: boolean;
}

export const AgentNode: React.FC<AgentNodeProps> = ({ agent, onClick, isSelected }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const pulseRef = useRef<THREE.Mesh>(null);
  const orbitRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (!meshRef.current) return;

    const time = state.clock.getElapsedTime();
    
    if (agent.status === 'active') {
      meshRef.current.rotation.y = time * 1.2;
      meshRef.current.rotation.x = Math.sin(time * 0.5) * 0.3;
      meshRef.current.position.y = agent.position[1] + Math.sin(time * 2 + agent.position[0]) * 0.2;
      
      if (pulseRef.current) {
        const pulseScale = 1 + Math.sin(time * 3) * 0.4;
        pulseRef.current.scale.setScalar(pulseScale);
        const pulseMaterial = pulseRef.current.material as THREE.MeshBasicMaterial;
        pulseMaterial.opacity = 0.4 * (1 - (pulseScale - 1) / 0.4);
      }
    } else if (agent.status === 'idle') {
      meshRef.current.rotation.y = time * 0.3;
      meshRef.current.position.y = agent.position[1] + Math.sin(time * 1) * 0.1;
    } else if (agent.status === 'error') {
      meshRef.current.rotation.y = time * 0.5;
      meshRef.current.rotation.z = Math.sin(time * 4) * 0.1;
      
      if (pulseRef.current) {
        const pulseScale = 1 + Math.sin(time * 5) * 0.3;
        pulseRef.current.scale.setScalar(pulseScale);
        const pulseMaterial = pulseRef.current.material as THREE.MeshBasicMaterial;
        pulseMaterial.opacity = 0.5 * (1 - (pulseScale - 1) / 0.3);
      }
    }

    if (orbitRef.current && agent.status === 'active') {
      orbitRef.current.rotation.y = time * 2;
    }

    if (isSelected && glowRef.current) {
      glowRef.current.scale.setScalar(1.5 + Math.sin(time * 4) * 0.2);
      const glowMaterial = glowRef.current.material as THREE.MeshBasicMaterial;
      glowMaterial.opacity = 0.3 + Math.sin(time * 3) * 0.1;
    }

    if (hovered && meshRef.current) {
      meshRef.current.scale.setScalar(1.3);
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1);
    }
  });

  const getStatusColor = () => {
    switch (agent.status) {
      case 'active': return agent.color;
      case 'idle': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'offline': return '#6b7280';
      default: return '#ffffff';
    }
  };

  const getStatusGlow = () => {
    switch (agent.status) {
      case 'active': return agent.color;
      case 'idle': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'offline': return '#374151';
      default: return '#ffffff';
    }
  };

  return (
    <group position={agent.position}>
      {(agent.status === 'active' || agent.status === 'error') && (
        <mesh ref={pulseRef}>
          <sphereGeometry args={[0.9, 16, 16]} />
          <meshBasicMaterial
            color={getStatusGlow()}
            transparent
            opacity={0.4}
            side={THREE.BackSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      )}

      {agent.status === 'active' && (
        <group ref={orbitRef}>
          {[0, 1, 2].map((i) => (
            <mesh key={i} position={[Math.cos(i * Math.PI * 2 / 3) * 0.8, 0, Math.sin(i * Math.PI * 2 / 3) * 0.8]}>
              <sphereGeometry args={[0.08, 8, 8]} />
              <meshBasicMaterial
                color={agent.color}
                transparent
                opacity={0.8}
              />
            </mesh>
          ))}
        </group>
      )}

      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHovered(false);
          document.body.style.cursor = 'default';
        }}
      >
        <octahedronGeometry args={[0.45, 0]} />
        <meshStandardMaterial
          color={getStatusColor()}
          emissive={getStatusColor()}
          emissiveIntensity={agent.status === 'active' ? 0.9 : agent.status === 'error' ? 0.7 : 0.3}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {isSelected && (
        <mesh ref={glowRef}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshBasicMaterial
            color={agent.color}
            transparent
            opacity={0.3}
            side={THREE.BackSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      )}

      <Html
        position={[0, 1.3, 0]}
        center
        distanceFactor={8}
        style={{
          pointerEvents: 'none',
          userSelect: 'none',
          transition: 'all 0.2s ease',
          transform: hovered ? 'scale(1.15)' : 'scale(1)',
        }}
      >
        <div 
          className="backdrop-blur-xl px-3 py-2 rounded-lg border-2 shadow-lg transition-all duration-200"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            borderColor: getStatusColor(),
            boxShadow: hovered ? `0 0 25px ${getStatusColor()}` : `0 0 10px ${getStatusColor()}40`,
          }}
        >
          <div className="text-white text-xs font-bold">{agent.name}</div>
          <div className="text-[10px] mt-0.5" style={{ color: getStatusColor() }}>
            {agent.role}
          </div>
          <div className="flex items-center gap-1 mt-1.5">
            <div 
              className="w-1.5 h-1.5 rounded-full animate-pulse" 
              style={{ 
                backgroundColor: getStatusGlow(),
                boxShadow: `0 0 6px ${getStatusGlow()}`
              }}
            />
            <span 
              className="text-[9px] font-semibold uppercase"
              style={{ color: getStatusColor() }}
            >
              {agent.status}
            </span>
          </div>
          {hovered && (
            <div className="text-[9px] text-gray-400 mt-1 border-t border-gray-700 pt-1">
              Click for details
            </div>
          )}
        </div>
      </Html>

      <pointLight
        color={getStatusGlow()}
        intensity={agent.status === 'active' ? 2 : agent.status === 'error' ? 1.5 : 0.5}
        distance={5}
        decay={2}
      />

      {agent.status === 'active' && (
        <pointLight
          color={agent.color}
          intensity={0.8}
          distance={8}
          decay={2}
        />
      )}
    </group>
  );
};
