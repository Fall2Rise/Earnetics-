import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import { GlowingPeg } from './GlowingPeg';
import { SeatedAgent } from './SeatedAgent';
import type { Agent } from '../../stores/agentStore';
import { useAgentStore } from '../../stores/agentStore';

interface DepartmentZoneNewProps {
  department: string;
  position: [number, number, number];
  scale: [number, number, number];
  color: string;
  agents: Agent[];
  onZoneClick?: () => void;
  onAgentClick?: (agent: Agent) => void;
}

/**
 * New Department Zone component matching reference design
 * Hexagonal/trapezoidal shape with glowing pegs and seated agents
 */
export const DepartmentZoneNew: React.FC<DepartmentZoneNewProps> = ({
  department,
  position,
  scale,
  color,
  agents,
  onZoneClick,
  onAgentClick,
}) => {
  const [width, height, depth] = scale;
  const zoneY = position[1] + 0.35;
  const selectAgent = useAgentStore((state) => state.selectAgent);

  const pegIntensity = (index: number) => 0.75 + ((index * 13) % 10) * 0.03;

  // Create glowing pegs in concentric circles
  const pegPositions = useMemo(() => {
    const pegs: Array<{ pos: [number, number, number]; pegColor: string }> = [];
    const layers = 3;
    const pegsPerLayer = [8, 16, 24];
    const colors = [color, adjustBrightness(color, 1.2), adjustBrightness(color, 0.8)];

    for (let layer = 0; layer < layers; layer++) {
      const radius = (layer + 1) * (width / 6);
      const count = pegsPerLayer[layer];
      const layerColor = colors[layer % colors.length];

      for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        pegs.push({
          pos: [x, 0.1, z],
          pegColor: layerColor,
        });
      }
    }

    return pegs;
  }, [width, color]);

  // Zone material
  const zoneMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#0c1626',
      emissive: color,
      emissiveIntensity: 0.55,
      metalness: 0.65,
      roughness: 0.28,
      transparent: true,
      opacity: 0.9,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  // Border material
  const borderMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 1.6,
      metalness: 0.6,
      roughness: 0.2,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  const coreMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: '#071827',
      emissive: color,
      emissiveIntensity: 0.6,
      metalness: 0.6,
      roughness: 0.25,
    });
    mat.needsUpdate = true;
    return mat;
  }, [color]);

  // Position agents around the zone
  const agentPositions = useMemo(() => {
    if (!agents.length) return [];
    const positions: Array<{ pos: [number, number, number]; rotation: number; agent: Agent; scale: number }> = [];
    const baseRadius = width / 3.6;
    const maxRadius = Math.max(baseRadius, width / 2 - 0.6);
    const ringSpacing = Math.max(0.45, width / 8);
    const baseCount = 6;
    const countStep = 6;
    const maxPerTier = 48;
    const agentScale =
      agents.length > 36 ? 0.75 :
      agents.length > 24 ? 0.82 :
      agents.length > 14 ? 0.9 : 1.0;

    let cursor = 0;
    let ringIndex = 0;
    let radius = baseRadius;
    let tierIndex = 0;
    while (cursor < agents.length) {
      if (ringIndex * countStep + baseCount > maxPerTier) {
        ringIndex = 0;
        radius = baseRadius;
        tierIndex += 1;
      }

      const capacity = baseCount + ringIndex * countStep;
      const remaining = agents.length - cursor;
      const count = Math.min(capacity, remaining);
      const yOffset = 0.1 + tierIndex * 0.22;
      for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2;
        positions.push({
          pos: [
            Math.cos(angle) * radius,
            yOffset,
            Math.sin(angle) * radius,
          ] as [number, number, number],
          rotation: angle + Math.PI,
          agent: agents[cursor + i],
          scale: agentScale,
        });
      }

      cursor += count;
      ringIndex += 1;
      radius = Math.min(maxRadius, radius + ringSpacing);
    }

    return positions;
  }, [agents, width]);

  const totalAgents = agents.length;
  const activeAgents = agents.filter(a => a.status === 'active').length;
  const progress = totalAgents > 0 ? Math.round((activeAgents / totalAgents) * 100) : 0;

  return (
    <group position={[position[0], zoneY, position[2]]}>
      {/* Hexagonal zone base */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[width / 2, width / 2, height + 0.4, 6]} />
        <primitive object={zoneMaterial} attach="material" />
      </mesh>
      {/* Always-visible base overlay */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <cylinderGeometry args={[width / 2 - 0.2, width / 2 - 0.2, height + 0.2, 6]} />
        <meshBasicMaterial color="#0c1c2e" transparent opacity={0.6} />
      </mesh>

      {/* Glowing border */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[width / 2 - 0.1, width / 2, 6]} />
        <primitive object={borderMaterial} attach="material" />
      </mesh>

      {/* Outer glow ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 0]}>
        <ringGeometry args={[width / 2, width / 2 + 0.35, 6]} />
        <meshBasicMaterial color={color} transparent opacity={0.45} />
      </mesh>

      {/* Inner rim */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[width / 2 - 0.5, width / 2 - 0.4, 6]} />
        <primitive object={borderMaterial} attach="material" />
      </mesh>

      {/* Central core */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[width / 6, width / 6, 0.3, 24]} />
        <primitive object={coreMaterial} attach="material" />
      </mesh>

      {/* Glowing pegs */}
      {pegPositions.map((peg, idx) => (
        <GlowingPeg
          key={`peg-${idx}`}
          position={peg.pos}
          color={peg.pegColor}
          size={0.12}
          intensity={pegIntensity(idx)}
        />
      ))}

      {/* Seated agents */}
      {agentPositions.map((agentPos, idx) => (
        <SeatedAgent
          key={`agent-${agentPos.agent.id}-${idx}`}
          position={agentPos.pos}
          color={agentPos.agent.color || color}
          rotation={agentPos.rotation}
          label={agentPos.agent.name}
          scale={agentPos.scale}
          onClick={() => {
            if (onAgentClick) {
              onAgentClick(agentPos.agent);
            } else {
              selectAgent(agentPos.agent);
            }
          }}
        />
      ))}

      {/* Department label */}
      <Html position={[0, 0.6, -width / 2 - 0.8]} center>
        <div
          style={{
            background: 'linear-gradient(180deg, rgba(10,24,40,0.92), rgba(6,12,20,0.75))',
            border: `1px solid ${color}55`,
            boxShadow: `0 0 16px ${color}55`,
            color: '#d7f7ff',
            padding: '4px 10px',
            borderRadius: '8px',
            fontSize: '11px',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
          }}
        >
          {department}
        </div>
      </Html>

      {/* Stats panel */}
      <Html position={[0, 1.4, 0]} center>
        <div
          style={{
            background: 'rgba(4, 10, 20, 0.7)',
            border: `1px solid ${color}55`,
            boxShadow: `0 0 12px ${color}40`,
            color: '#e8f7ff',
            padding: '6px 10px',
            borderRadius: '8px',
            fontSize: '10px',
            minWidth: '110px',
            textAlign: 'center',
          }}
        >
          <div style={{ textTransform: 'uppercase', letterSpacing: '0.08em', color: '#a7d9ff' }}>
            Agents
          </div>
          <div style={{ fontSize: '13px', fontWeight: 700 }}>
            {activeAgents}/{totalAgents}
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', marginTop: '4px' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: color, borderRadius: '4px' }} />
          </div>
        </div>
      </Html>

      {/* Clickable area */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        onClick={onZoneClick}
        onPointerOver={(e) => {
          e.stopPropagation();
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          document.body.style.cursor = 'default';
        }}
      >
        <cylinderGeometry args={[width / 2, width / 2, 0.02, 6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
    </group>
  );
};

// Helper function to adjust color brightness
function adjustBrightness(color: string, factor: number): string {
  try {
    const hex = color.replace('#', '');
    if (hex.length !== 6) return color; // Return original if invalid format
    
    const r = Math.min(255, Math.max(0, Math.floor(parseInt(hex.substring(0, 2), 16) * factor)));
    const g = Math.min(255, Math.max(0, Math.floor(parseInt(hex.substring(2, 4), 16) * factor)));
    const b = Math.min(255, Math.max(0, Math.floor(parseInt(hex.substring(4, 6), 16) * factor)));
    return `#${[r, g, b].map(x => x.toString(16).padStart(2, '0')).join('')}`;
  } catch {
    return color; // Return original color if parsing fails
  }
}
