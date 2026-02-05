import React from 'react';
import { MeshReflectorMaterial } from '@react-three/drei';

export const FactoryFloor: React.FC = () => {
  return (
    <group position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      {/* Main Expansive Floor */}
      <mesh receiveShadow>
        <planeGeometry args={[200, 200]} />
        <MeshReflectorMaterial
          blur={[300, 100]}
          resolution={1024}
          mixBlur={1}
          mixStrength={50} // Strong reflections
          roughness={0.5} // Brushed steel look
          depthScale={1.2}
          minDepthThreshold={0.4}
          maxDepthThreshold={1.4}
          color="#0a0a0a" // Deep Onyx
          metalness={0.85}
          mirror={0.6}
        />
      </mesh>
      
      {/* Subtle Grid Overlay for Scale */}
      <gridHelper 
        args={[200, 40, 0x003333, 0x001111]} 
        position={[0, 0, 0.01]} 
        rotation={[Math.PI / 2, 0, 0]} 
      />
    </group>
  );
};
