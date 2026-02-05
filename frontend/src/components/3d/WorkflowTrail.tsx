import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface WorkflowTrailProps {
  from: [number, number, number];
  to: [number, number, number];
  color: string;
  progress: number; // 0 to 1
}

export const WorkflowTrail: React.FC<WorkflowTrailProps> = ({ from, to, color, progress }) => {
  const trailRef = useRef<THREE.Group>(null);
  const lineRef = useRef<THREE.Line>(null);
  const particleRef = useRef<THREE.Mesh>(null);
  const safeColor = color || '#00d4ff';

  const currentPos = useMemo(() => {
    return new THREE.Vector3(...from).lerp(new THREE.Vector3(...to), progress);
  }, [from, to, progress]);

  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const points = [
      new THREE.Vector3(...from),
      currentPos,
    ];
    geometry.setFromPoints(points);
    return geometry;
  }, [from, currentPos]);

  useFrame((state) => {
    if (particleRef.current) {
      particleRef.current.position.copy(currentPos);
      const time = state.clock.getElapsedTime();
      particleRef.current.rotation.y = time * 2;
      particleRef.current.rotation.x = time * 1.5;
      
      const scale = 1 + Math.sin(time * 5) * 0.2;
      particleRef.current.scale.setScalar(scale);
    }

    if (lineRef.current) {
      const material = lineRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.5 + Math.sin(state.clock.getElapsedTime() * 2) * 0.3;
    }
  });

  return (
    <group ref={trailRef}>
      <line ref={lineRef} geometry={lineGeometry}>
        <lineBasicMaterial
          color={safeColor}
          transparent
          opacity={0.5}
          linewidth={3}
          blending={THREE.AdditiveBlending}
        />
      </line>
      
      <mesh ref={particleRef} position={currentPos}>
        <octahedronGeometry args={[0.2, 0]} />
        <meshBasicMaterial
          color={safeColor}
          transparent
          opacity={0.9}
          // MeshBasicMaterial has no emissive uniforms; keep it simple to avoid uniform errors
        />
      </mesh>
      
      <pointLight
        color={safeColor}
        intensity={2}
        distance={3}
        decay={2}
        position={currentPos}
      />
    </group>
  );
};
