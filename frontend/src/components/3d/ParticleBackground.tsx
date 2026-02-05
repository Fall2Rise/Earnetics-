import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export const ParticleBackground: React.FC = () => {
  const particlesRef = useRef<THREE.Points>(null);
  const gridRef = useRef<THREE.LineSegments>(null);

  const particleCount = 5000; // Increased for more impressive effect
  const seeded = (index: number) => {
    const x = Math.sin(index * 12.9898) * 43758.5453;
    return x - Math.floor(x);
  };
  
  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const r1 = seeded(i + 1);
      const r2 = seeded(i + 17);
      const r3 = seeded(i + 31);
      
      positions[i3] = (r1 - 0.5) * 100;
      positions[i3 + 1] = (r2 - 0.5) * 100;
      positions[i3 + 2] = (r3 - 0.5) * 100;

      const color = new THREE.Color();
      const hue = 0.5 + seeded(i + 47) * 0.2;
      const light = 0.5 + seeded(i + 53) * 0.3;
      color.setHSL(hue, 0.7, light);
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;
    }

    return { positions, colors };
  }, []);

  const gridGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const gridSize = 60;
    const divisions = 60;
    const step = gridSize / divisions;
    const halfSize = gridSize / 2;

    const vertices: number[] = [];
    const colors: number[] = [];

    const color1 = new THREE.Color(0x00ff88);
    const color2 = new THREE.Color(0x00ffff);

    for (let i = 0; i <= divisions; i++) {
      const pos = -halfSize + i * step;
      
      vertices.push(-halfSize, -10, pos, halfSize, -10, pos);
      vertices.push(pos, -10, -halfSize, pos, -10, halfSize);

      const t = i / divisions;
      const color = new THREE.Color().lerpColors(color1, color2, t);
      
      for (let j = 0; j < 4; j++) {
        colors.push(color.r, color.g, color.b);
      }
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.getElapsedTime() * 0.02;
      
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
      
      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        const y = positions[i3 + 1];
        
        positions[i3 + 1] = y + Math.sin(state.clock.getElapsedTime() + i) * 0.01;
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }

    if (gridRef.current) {
      const material = gridRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.15 + Math.sin(state.clock.getElapsedTime() * 0.5) * 0.05;
    }
  });

  return (
    <>
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

      <lineSegments ref={gridRef} geometry={gridGeometry}>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.15}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>

      <mesh position={[0, -10.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshBasicMaterial
          color="#000510"
          transparent
          opacity={0.8}
        />
      </mesh>
    </>
  );
};
