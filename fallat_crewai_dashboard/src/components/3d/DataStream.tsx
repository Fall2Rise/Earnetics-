import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { Agent } from '../../stores/agentStore';

interface DataStreamProps {
  from: [number, number, number];
  to: [number, number, number];
  color: string;
  speed?: number;
}

export const DataStream: React.FC<DataStreamProps> = ({ from, to, color, speed = 2 }) => {
  const streamRef = useRef<THREE.Group>(null);
  const particlesRef = useRef<THREE.Points>(null);

  const direction = useMemo(() => {
    const dir = new THREE.Vector3(...to).sub(new THREE.Vector3(...from)).normalize();
    return dir;
  }, [from, to]);

  const distance = useMemo(() => {
    return new THREE.Vector3(...from).distanceTo(new THREE.Vector3(...to));
  }, [from, to]);

  const particleCount = Math.max(10, Math.floor(distance * 2));
  
  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const colorObj = new THREE.Color(color);

    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const t = i / particleCount;
      
      const pos = new THREE.Vector3(...from).lerp(new THREE.Vector3(...to), t);
      positions[i3] = pos.x;
      positions[i3 + 1] = pos.y;
      positions[i3 + 2] = pos.z;

      colors[i3] = colorObj.r;
      colors[i3 + 1] = colorObj.g;
      colors[i3 + 2] = colorObj.b;
    }

    return { positions, colors };
  }, [from, to, color, particleCount]);

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
      const time = state.clock.getElapsedTime() * speed;
      
      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        const baseT = (i / particleCount + time * 0.1) % 1;
        
        const pos = new THREE.Vector3(...from).lerp(new THREE.Vector3(...to), baseT);
        positions[i3] = pos.x;
        positions[i3 + 1] = pos.y;
        positions[i3 + 2] = pos.z;
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <group ref={streamRef}>
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={positions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={particleCount}
            array={colors}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.2}
          vertexColors
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </group>
  );
};
