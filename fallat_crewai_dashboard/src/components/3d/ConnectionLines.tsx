import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';

interface ConnectionLinesProps {
  agents: Agent[];
  departments: Array<{ department: string; position: [number, number, number] }>;
}

export const ConnectionLines: React.FC<ConnectionLinesProps> = ({ agents, departments }) => {
  const linesRef = useRef<THREE.LineSegments>(null);
  const activeConnectionsRef = useRef<THREE.LineSegments>(null);

  // Create connections between active agents in the same department
  const { connections, activeConnections } = useMemo(() => {
    const connections: Array<{ start: [number, number, number]; end: [number, number, number]; color: string }> = [];
    const activeConnections: Array<{ start: [number, number, number]; end: [number, number, number]; color: string }> = [];

    // Connect agents within same department
    const agentsByDept = agents.reduce((acc, agent) => {
      if (!acc[agent.department]) acc[agent.department] = [];
      acc[agent.department].push(agent);
      return acc;
    }, {} as Record<string, Agent[]>);

    Object.values(agentsByDept).forEach((deptAgents) => {
      for (let i = 0; i < deptAgents.length; i++) {
        for (let j = i + 1; j < deptAgents.length; j++) {
          const agent1 = deptAgents[i];
          const agent2 = deptAgents[j];
          
          // Always show connections, but make them brighter for active agents
          if (agent1.status === 'active' && agent2.status === 'active') {
            activeConnections.push({
              start: agent1.position,
              end: agent2.position,
              color: agent1.color,
            });
          } else {
            // Show dim connections for all agents (even idle ones) to maintain visual structure
            connections.push({
              start: agent1.position,
              end: agent2.position,
              color: agent1.status === 'active' || agent2.status === 'active' 
                ? agent1.color 
                : '#4b5563', // Dim gray only if both are idle
            });
          }
        }
      }
    });

    // Connect departments (executive to all others)
    const executiveDept = departments.find(d => d.department === 'Executive Board');
    if (executiveDept) {
      departments.forEach(dept => {
        if (dept.department !== 'Executive Board') {
          connections.push({
            start: executiveDept.position,
            end: dept.position,
            color: '#FFD700',
          });
        }
      });
    }

    return { connections, activeConnections };
  }, [agents, departments]);

  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const vertices: number[] = [];
    const colors: number[] = [];

    connections.forEach(conn => {
      vertices.push(...conn.start, ...conn.end);
      const color = new THREE.Color(conn.color);
      colors.push(color.r, color.g, color.b, color.r, color.g, color.b);
    });

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [connections]);

  const activeLineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const vertices: number[] = [];
    const colors: number[] = [];

    activeConnections.forEach(conn => {
      vertices.push(...conn.start, ...conn.end);
      const color = new THREE.Color(conn.color);
      colors.push(color.r, color.g, color.b, color.r, color.g, color.b);
    });

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [activeConnections]);

  useFrame((state) => {
    if (linesRef.current) {
      const material = linesRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.2 + Math.sin(state.clock.getElapsedTime() * 0.5) * 0.1;
    }

    if (activeConnectionsRef.current) {
      const material = activeConnectionsRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.6 + Math.sin(state.clock.getElapsedTime() * 2) * 0.3;
      
      // Animate line width/pulse
      const scale = 1 + Math.sin(state.clock.getElapsedTime() * 3) * 0.1;
      activeConnectionsRef.current.scale.setScalar(scale);
    }
  });

  return (
    <>
      {connections.length > 0 && (
        <lineSegments ref={linesRef} geometry={lineGeometry}>
          <lineBasicMaterial
            vertexColors
            transparent
            opacity={0.2}
            linewidth={1}
            blending={THREE.AdditiveBlending}
          />
        </lineSegments>
      )}
      
      {activeConnections.length > 0 && (
        <lineSegments ref={activeConnectionsRef} geometry={activeLineGeometry}>
          <lineBasicMaterial
            vertexColors
            transparent
            opacity={0.6}
            linewidth={2}
            blending={THREE.AdditiveBlending}
          />
        </lineSegments>
      )}
    </>
  );
};
