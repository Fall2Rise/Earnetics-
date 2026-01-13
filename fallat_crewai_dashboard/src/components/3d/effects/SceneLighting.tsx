import React from 'react';

/**
 * Cinematic 3-light rig with shadows and atmospheric fog
 * - Key light: Main directional light with shadows
 * - Fill light: Soft hemisphere light for ambient fill
 * - Rim light: Subtle back light for depth
 */
export const SceneLighting: React.FC = () => {
  return (
    <>
      {/* Fog for depth and atmosphere */}
      <fog attach="fog" args={['#030714', 30, 120]} />

      {/* Key Light - Main directional light with shadows */}
      <directionalLight
        position={[15, 25, 10]}
        intensity={1.2}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
        shadow-camera-near={0.1}
        shadow-camera-far={200}
        shadow-bias={-0.0001}
        shadow-normalBias={0.005}
      />

      {/* Fill Light - Soft hemisphere for ambient fill (no shadows) */}
      <hemisphereLight
        intensity={0.4}
        color="#1a1a2e"
        groundColor="#0a0a14"
      />

      {/* Rim/Back Light - Subtle directional from behind */}
      <directionalLight
        position={[-10, 15, -15]}
        intensity={0.3}
        color="#4a90e2"
      />

      {/* Ambient light for base illumination */}
      <ambientLight intensity={0.3} color="#1a1a2e" />
    </>
  );
};
