import React, { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';
import { AgentNode } from './AgentNode';
import { CircularPlatform } from './CircularPlatform';

interface DivisionalZoneProps {
  department: string;
  agents: Agent[];
  position: [number, number, number];
  color: string;
  scale: [number, number, number];
  onAgentClick: (agent: Agent) => void;
  selectedAgent: Agent | null;
  onZoneClick?: (department: string) => void;
}

const ThemedElement: React.FC<{ department: string; color: string; scale: [number, number, number] }> = ({ department, color, scale }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    const time = state.clock.getElapsedTime();
    meshRef.current.rotation.y = time * 0.2;
    meshRef.current.position.y = Math.sin(time * 0.5) * 0.2;
  });

  switch (department) {
    case 'Finance & Revenue':
      return (
        <group position={[0, -scale[1] / 2 + 0.5, 0]}>
          {/* Hexagonal stack for Finance */}
          {[0, 1, 2].map((i) => (
            <mesh key={i} position={[Math.cos(i * 2.1) * 1.8, i * 0.6, Math.sin(i * 2.1) * 1.8]}>
              <cylinderGeometry args={[0.6, 0.6, 0.2, 6]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} metalness={0.8} roughness={0.2} />
            </mesh>
          ))}
          <mesh position={[0, 2, 0]}>
            <octahedronGeometry args={[0.8, 0]} />
            <meshStandardMaterial color={color} wireframe emissive={color} emissiveIntensity={1} />
          </mesh>
        </group>
      );
    case 'Tech & Infrastructure':
      return (
        <group>
          <mesh ref={meshRef} position={[0, 0, 0]}>
            <torusKnotGeometry args={[scale[0] * 0.25, 0.08, 128, 16]} />
            <meshStandardMaterial color={color} wireframe emissive={color} emissiveIntensity={1.2} />
          </mesh>
          {/* Tech rings */}
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[2.5, 2.6, 64]} />
            <meshBasicMaterial color={color} transparent opacity={0.4} side={THREE.DoubleSide} />
          </mesh>
        </group>
      );
    case 'Creative & Product':
      return (
        <group>
          <mesh ref={meshRef} position={[0, 0, 0]}>
            <icosahedronGeometry args={[scale[0] * 0.35, 1]} />
            <meshPhysicalMaterial
              color={color}
              metalness={0.1}
              roughness={0.1}
              transmission={0.6}
              thickness={2}
              emissive={color}
              emissiveIntensity={0.5}
            />
          </mesh>
          <mesh scale={[1.2, 1.2, 1.2]}>
            <icosahedronGeometry args={[scale[0] * 0.35, 0]} />
            <meshBasicMaterial color={color} wireframe transparent opacity={0.3} />
          </mesh>
        </group>
      );
    case 'Executive Board':
      return (
        <group position={[0, -0.5, 0]}>
          <mesh>
            <cylinderGeometry args={[scale[0] * 0.4, scale[0] * 0.45, 0.2, 6]} />
            <meshStandardMaterial color={color} metalness={0.9} roughness={0.1} emissive={color} emissiveIntensity={0.5} />
          </mesh>
          {/* Floating crown */}
          <mesh position={[0, 1.5, 0]} rotation={[0, 0.5, 0]}>
            <torusGeometry args={[1.5, 0.05, 16, 100]} />
            <meshStandardMaterial color="#ffd700" emissive="#ffd700" emissiveIntensity={1} />
          </mesh>
        </group>
      );
    default:
      return (
        <mesh ref={meshRef} position={[0, -scale[1] / 2 + 0.2, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[scale[0] * 0.3, scale[0] * 0.35, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.3} side={THREE.DoubleSide} />
        </mesh>
      );
  }
};

export const DivisionalZone: React.FC<DivisionalZoneProps> = ({
  department,
  agents,
  position,
  color,
  scale,
  onAgentClick,
  selectedAgent,
  onZoneClick,
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

  // Calculate platform radius from scale
  const platformRadius = Math.max(scale[0], scale[2]) * 0.5;
  const gridSize = Math.max(3, Math.min(7, Math.floor(platformRadius))); // Adaptive grid size

  return (
    <group position={position}>
      {/* Use CircularPlatform for futuristic look */}
      <CircularPlatform
        position={[0, position[1], 0]}
        radius={platformRadius}
        color={color}
        label={department}
        gridSize={gridSize}
        glowIntensity={activeAgents > 0 ? 1.5 : 0.8}
      />

      <mesh
        ref={zoneRef}
        raycast={() => null}  // Prevent raycasting issues
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
          (e.target as any).setPointerCapture(e.pointerId);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHovered(false);
          document.body.style.cursor = 'default';
          (e.target as any).releasePointerCapture(e.pointerId);
        }}
        onPointerDown={(e) => {
          e.stopPropagation();
          (e.target as any).setPointerCapture(e.pointerId);
        }}
        onPointerUp={(e) => {
          e.stopPropagation();
          if (onZoneClick) {
            console.log('[DivisionalZone] Zone clicked (onPointerUp):', department);
            onZoneClick(department);
          }
          (e.target as any).releasePointerCapture(e.pointerId);
        }}
        onClick={(e) => {
          e.stopPropagation();
          if (onZoneClick) {
            console.log('[DivisionalZone] Zone clicked (onClick):', department);
            onZoneClick(department);
          }
        }}
      >
        <boxGeometry args={scale} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.15}
          emissive={color}
          emissiveIntensity={hovered ? 0.6 : 0.2}
          wireframe={false}
          side={2}  // DoubleSide to ensure clicks work from both sides
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

      {/* Department Label - positioned above circular platform */}
      <Html
        position={[0, platformRadius + 1.2, 0]}
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
            className="text-white text-base font-bold text-center mb-1 uppercase font-mono"
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

      {/* Animated energy field around active departments */}
      {activeAgents > 0 && (
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[scale[0] * 0.6, 32, 32]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.05}
            wireframe
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      )}

      {/* Floating particles around department */}
      {activeAgents > 0 && Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        const radius = scale[0] * 0.5;
        return (
          <mesh
            key={`particle-${i}`}
            position={[
              Math.cos(angle) * radius,
              Math.sin(i * 0.5) * 0.5,
              Math.sin(angle) * radius
            ]}
          >
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={0.6}
              blending={THREE.AdditiveBlending}
            />
          </mesh>
        );
      })}
    </group>
  );
};
