import React, { useRef, useEffect, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';
import { AgentNode } from './AgentNode';
import { useAgentStore } from '../../stores/agentStore';

interface DepartmentRoomProps {
  department: string;
  color: string;
  agents: Agent[];
  onExit: () => void;
}

const RoomEnvironment: React.FC<{ department: string; color: string }> = ({ department, color }) => {
  const floorRef = useRef<THREE.Mesh>(null);
  const wallsRef = useRef<THREE.Group>(null);
  const ceilingRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    if (floorRef.current) {
      // Subtle floor animation
      floorRef.current.rotation.z = Math.sin(time * 0.1) * 0.01;
    }
  });

  const roomSize = 20;
  const wallHeight = 10;

  return (
    <group>
      {/* Floor */}
      <mesh ref={floorRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[roomSize, roomSize]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.1}
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>

      {/* Grid floor overlay */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <planeGeometry args={[roomSize, roomSize, 20, 20]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.05}
          wireframe
        />
      </mesh>

      {/* Walls */}
      <group ref={wallsRef}>
        {/* Back wall */}
        <mesh position={[0, wallHeight / 2, -roomSize / 2]}>
          <boxGeometry args={[roomSize, wallHeight, 0.2]} />
          <meshStandardMaterial
            color={color}
            transparent
            opacity={0.15}
            emissive={color}
            emissiveIntensity={0.1}
          />
        </mesh>

        {/* Left wall */}
        <mesh position={[-roomSize / 2, wallHeight / 2, 0]} rotation={[0, Math.PI / 2, 0]}>
          <boxGeometry args={[roomSize, wallHeight, 0.2]} />
          <meshStandardMaterial
            color={color}
            transparent
            opacity={0.15}
            emissive={color}
            emissiveIntensity={0.1}
          />
        </mesh>

        {/* Right wall */}
        <mesh position={[roomSize / 2, wallHeight / 2, 0]} rotation={[0, Math.PI / 2, 0]}>
          <boxGeometry args={[roomSize, wallHeight, 0.2]} />
          <meshStandardMaterial
            color={color}
            transparent
            opacity={0.15}
            emissive={color}
            emissiveIntensity={0.1}
          />
        </mesh>
      </group>

      {/* Ceiling */}
      <mesh ref={ceilingRef} rotation={[Math.PI / 2, 0, 0]} position={[0, wallHeight, 0]}>
        <planeGeometry args={[roomSize, roomSize]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.05}
          emissive={color}
          emissiveIntensity={0.1}
        />
      </mesh>

      {/* Ambient glow */}
      <pointLight
        color={color}
        intensity={2}
        distance={30}
        position={[0, wallHeight / 2, 0]}
        decay={2}
      />
    </group>
  );
};

const Door: React.FC<{ isOpen: boolean; color: string; onClose: () => void }> = ({ isOpen, color, onClose }) => {
  const doorRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (doorRef.current) {
      const targetRotation = isOpen ? -Math.PI / 2 : 0;
      doorRef.current.rotation.y = THREE.MathUtils.lerp(
        doorRef.current.rotation.y,
        targetRotation,
        0.1
      );
    }
  });

  return (
    <group ref={doorRef} position={[0, 5, 9.8]}>
      {/* Door frame */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[4, 10, 0.3]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* Door panels */}
      <group position={[-1.5, 0, 0.1]}>
        <mesh
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          onClick={onClose}
        >
          <boxGeometry args={[1.5, 9, 0.2]} />
          <meshStandardMaterial
            color={hovered ? color : '#1a1a1a'}
            emissive={color}
            emissiveIntensity={hovered ? 0.5 : 0.2}
          />
        </mesh>
      </group>
      <group position={[1.5, 0, 0.1]} rotation={[0, 0, 0]}>
        <mesh>
          <boxGeometry args={[1.5, 9, 0.2]} />
          <meshStandardMaterial
            color={'#1a1a1a'}
            emissive={color}
            emissiveIntensity={0.2}
          />
        </mesh>
      </group>
    </group>
  );
};

export const DepartmentRoom: React.FC<DepartmentRoomProps> = ({
  department,
  color,
  agents,
  onExit,
}) => {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);
  const [doorOpen, setDoorOpen] = useState(false);
  const { selectAgent, selectedAgent } = useAgentStore();

  // Animate camera entry
  useEffect(() => {
    // Start camera outside the room
    camera.position.set(0, 8, 15);
    camera.lookAt(0, 5, 0);

    // Open door after a brief delay
    const doorTimer = setTimeout(() => setDoorOpen(true), 300);

    // Animate camera into room
    const animateCamera = () => {
      const targetPosition = new THREE.Vector3(0, 6, 8);
      const targetLookAt = new THREE.Vector3(0, 4, 0);

      const animate = () => {
        camera.position.lerp(targetPosition, 0.05);
        
        const direction = new THREE.Vector3()
          .subVectors(targetLookAt, camera.position)
          .normalize();
        const targetQuaternion = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 0, -1),
          direction
        );
        camera.quaternion.slerp(targetQuaternion, 0.05);

        if (camera.position.distanceTo(targetPosition) > 0.1) {
          requestAnimationFrame(animate);
        }
      };
      animate();
    };

    const cameraTimer = setTimeout(animateCamera, 500);

    return () => {
      clearTimeout(doorTimer);
      clearTimeout(cameraTimer);
    };
  }, [camera]);

  // Distribute agents in the room
  const agentPositions = agents.map((agent, index) => {
    const angle = (index / agents.length) * Math.PI * 2;
    const radius = 6;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius - 4; // Move them forward in the room
    const y = 1.5;
    return { agent, position: [x, y, z] as [number, number, number] };
  });

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 8, 15]} fov={60} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 10, 5]} intensity={0.8} castShadow />

      {/* Room environment */}
      <RoomEnvironment department={department} color={color} />

      {/* Door */}
      <Door isOpen={doorOpen} color={color} onClose={onExit} />

      {/* Department name display */}
      <mesh position={[0, 8, -9.5]}>
        <planeGeometry args={[8, 2]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.3}
          emissive={color}
          emissiveIntensity={0.5}
        />
      </mesh>

      {/* Floating department label */}
      <Html position={[0, 9, -9.5]} center>
        <div
          className="px-6 py-3 rounded-xl border-2 text-white font-bold text-xl backdrop-blur-xl"
          style={{
            borderColor: color,
            backgroundColor: `${color}20`,
            boxShadow: `0 0 20px ${color}40`,
            textShadow: `0 0 10px ${color}`,
          }}
        >
          {department}
        </div>
      </Html>

      {/* Agents in the room */}
      {agentPositions.map(({ agent, position }) => (
        <AgentNode
          key={agent.id}
          agent={{ ...agent, position }}
          onClick={() => selectAgent(agent)}
          isSelected={selectedAgent?.id === agent.id}
        />
      ))}

      {/* Exit button indicator */}
      {doorOpen && (
        <pointLight
          color={color}
          intensity={3}
          distance={5}
          position={[0, 5, 9.5]}
        />
      )}

      <OrbitControls
        ref={controlsRef}
        enablePan={false}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={20}
        target={[0, 4, -2]}
        maxPolarAngle={Math.PI / 2}
        enableDamping
        dampingFactor={0.05}
      />
    </>
  );
};
