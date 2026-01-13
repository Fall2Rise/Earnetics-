import React, { useRef, useEffect, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ActivityBurstProps {
  position: [number, number, number];
  color: string;
  intensity?: number;
  duration?: number;
}

export const ActivityBurst: React.FC<ActivityBurstProps> = ({ 
  position, 
  color, 
  intensity = 1,
  duration = 1 
}) => {
  const burstRef = useRef<THREE.Group>(null);
  const [active, setActive] = useState(true);
  const startTime = useRef<number>(0);

  useEffect(() => {
    startTime.current = Date.now();
    const timer = setTimeout(() => setActive(false), duration * 1000);
    return () => clearTimeout(timer);
  }, [duration]);

  useFrame((state) => {
    if (!burstRef.current || !active) return;
    
    const elapsed = (Date.now() - startTime.current) / 1000;
    const progress = elapsed / duration;
    
    if (progress >= 1) {
      setActive(false);
      return;
    }

    const scale = 1 + progress * 3;
    const opacity = 1 - progress;
    
    burstRef.current.scale.setScalar(scale);
    burstRef.current.children.forEach((child) => {
      if (child instanceof THREE.Mesh) {
        const material = child.material as THREE.MeshBasicMaterial;
        material.opacity = opacity * 0.6;
      }
    });
  });

  if (!active) return null;

  return (
    <group ref={burstRef} position={position}>
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const angle = (i / 6) * Math.PI * 2;
        return (
          <mesh
            key={i}
            position={[Math.cos(angle) * 0.5, Math.sin(angle) * 0.5, 0]}
            rotation={[0, 0, angle]}
          >
            <boxGeometry args={[0.1, 1, 0.1]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={0.6}
              blending={THREE.AdditiveBlending}
            />
          </mesh>
        );
      })}
      <mesh>
        <sphereGeometry args={[0.3, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.8}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  );
};
