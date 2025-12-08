import React, { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Text } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';
import { AgentNode } from './AgentNode';

interface DivisionalZoneProps {
  department: string;
  agents: Agent[];
  position: [number, number, number];
  color: string;
  scale: [number, number, number];
  onAgentClick: (agent: Agent) => void;
  selectedAgent: Agent | null;
}

export const DivisionalZone: React.FC<DivisionalZoneProps> = ({
  department,
  agents,
  position,
  color,
  scale,
  onAgentClick,
  selectedAgent,
}) => {
  const zoneRef = useRef<THREE.Mesh>(null);
  const edgesRef = useRef<THREE.LineSegments>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  const edgesGeometry = useMemo(() => {
    const geometry = new THREE.BoxGeometry(scale[0], scale[1], scale[2]);
    return new THREE.EdgesGeometry(geometry);
  }, [scale]);

  useFrame((state) => {
    if (!zoneRef.current) return;
    const time = state.clock.getElapsedTime();
    
    zoneRef.current.position.y = position[1] + Math.sin(time * 0.5 + position[0]) * 0.3;
    
    if (edgesRef.current) {
      const material = edgesRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.4 + Math.sin(time * 2) * 0.2;
      
      edgesRef.current.rotation.y = time * 0.1;
    }

    if (glowRef.current) {
      const glowMaterial = glowRef.current.material as THREE.MeshBasicMaterial;
      glowMaterial.opacity = 0.1 + Math.sin(time * 1.5) * 0.05;
      glowRef.current.scale.setScalar(1 + Math.sin(time * 2) * 0.05);
    }
    
    if (hovered) {
      zoneRef.current.scale.setScalar(1.02 + Math.sin(time * 3) * 0.01);
    } else {
      zoneRef.current.scale.set(1, 1, 1);
    }
  });

  const activeAgents = agents.filter(a => a.status === 'active').length;
  const totalAgents = agents.length;

  return (
    <group position={position}>
      <mesh
        ref={zoneRef}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'default';
        }}
      >
        <boxGeometry args={scale} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.12}
          emissive={color}
          emissiveIntensity={hovered ? 0.4 : 0.15}
          wireframe={false}
        />
      </mesh>

      <mesh ref={glowRef} position={[0, 0, 0]}>
        <boxGeometry args={[scale[0] * 1.05, scale[1] * 1.05, scale[2] * 1.05]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.1}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      <lineSegments ref={edgesRef} geometry={edgesGeometry}>
        <lineBasicMaterial
          color={color}
          transparent
          opacity={0.5}
          linewidth={2}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>

      <Html
        position={[0, scale[1] / 2 + 0.8, 0]}
        center
        distanceFactor={10}
        style={{
          pointerEvents: 'none',
          userSelect: 'none',
        }}
      >
        <div 
          className="bg-black/95 backdrop-blur-xl px-5 py-3 rounded-xl border-2 shadow-lg" 
          style={{ 
            borderColor: color,
            boxShadow: `0 0 20px ${color}40, inset 0 0 10px ${color}20`
          }}
        >
          <div 
            className="text-white text-base font-bold text-center mb-1"
            style={{
              textShadow: `0 0 10px ${color}`,
            }}
          >
            {department}
          </div>
          <div className="flex items-center justify-center gap-2">
            <div 
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ 
                backgroundColor: activeAgents > 0 ? '#10b981' : '#6b7280',
                boxShadow: activeAgents > 0 ? '0 0 8px #10b981' : 'none'
              }}
            />
            <div className="text-xs text-gray-300 font-mono">
              {activeAgents}/{totalAgents} Active
            </div>
          </div>
        </div>
      </Html>

      {agents.map((agent, index) => {
        const angle = (index / agents.length) * Math.PI * 2;
        const radius = Math.min(scale[0], scale[2]) * 0.35;
        const localX = Math.cos(angle) * radius;
        const localZ = Math.sin(angle) * radius;
        const localY = (Math.sin(index * 0.5) * 0.5);

        const agentWithLocalPosition = {
          ...agent,
          position: [localX, localY, localZ] as [number, number, number],
        };

        return (
          <AgentNode
            key={agent.id}
            agent={agentWithLocalPosition}
            onClick={() => onAgentClick(agent)}
            isSelected={selectedAgent?.id === agent.id}
          />
        );
      })}

      <pointLight
        color={color}
        intensity={activeAgents > 0 ? 3 : 0.8}
        distance={scale[0] * 2.5}
        decay={2}
      />

      <spotLight
        color={color}
        intensity={activeAgents > 0 ? 1.5 : 0.3}
        angle={Math.PI / 4}
        penumbra={0.5}
        position={[0, scale[1] / 2 + 2, 0]}
        target-position={[0, 0, 0]}
        distance={scale[0] * 3}
        decay={2}
      />
    </group>
  );
};
