import React from 'react';
import { Environment } from '@react-three/drei';
import { useDebugStore } from '../../../stores/debugStore';

/**
 * Cinematic 3-light rig with shadows and atmospheric fog
 * - Key light: Main directional light with shadows
 * - Fill light: Soft hemisphere light for ambient fill
 * - Rim light: Subtle back light for depth
 */
export const SceneLighting: React.FC<{ quality?: 'low' | 'high' }> = ({ quality = 'low' }) => {
  const high = quality === 'high';
  const debug = useDebugStore();

  return (
    <>
      {/* Environment Map for realistic reflections */}
      {debug.showEnvironment && <Environment preset="city" blur={0.8} background={false} />}

      {/* Volumetric Fog - Lighter and further back */}
      {debug.showFog && <fog attach="fog" args={['#040b16', high ? 40 : 50, high ? 180 : 150]} />}

      {/* Key Light - Main directional light with shadows */}
      {debug.showKeyLight && (
        <directionalLight
          position={[18, 30, 12]}
          intensity={high ? 4.0 : 2.5}
          castShadow={high}
          shadow-mapSize-width={high ? 2048 : 1024}
          shadow-mapSize-height={high ? 2048 : 1024}
          shadow-camera-left={-50}
          shadow-camera-right={50}
          shadow-camera-top={50}
          shadow-camera-bottom={-50}
          shadow-camera-near={0.1}
          shadow-camera-far={200}
          shadow-bias={-0.0001}
          shadow-normalBias={high ? 0.005 : 0.01}
        />
      )}

      {/* Fill Light - Soft hemisphere for ambient fill (no shadows) */}
      {debug.showFillLight && (
        <hemisphereLight
          intensity={high ? 1.5 : 1.2}
          color="#223653"
          groundColor="#0b111f"
        />
      )}

      {/* Rim/Back Light - Subtle directional from behind */}
      {debug.showRimLight && (
        <directionalLight
          position={[-14, 18, -18]}
          intensity={high ? 2.0 : 1.5}
          color="#5aa0ff"
        />
      )}

      {/* Warm amber accents to match reference */}
      {debug.showPointLights && (
        <>
          <pointLight position={[10, 6, 10]} intensity={high ? 2.0 : 1.5} distance={44} color="#ffb84a" />
          <pointLight position={[-10, 6, -10]} intensity={high ? 1.8 : 1.2} distance={44} color="#ff9f2d" />
          {/* Cool cyan core fill */}
          <pointLight position={[0, 7, 0]} intensity={high ? 2.5 : 2.0} distance={36} color="#31d4ff" />
        </>
      )}

      {/* Focused spotlight on command deck */}
      {debug.showSpotLight && (
        <spotLight
          position={[0, 26, 10]}
          intensity={high ? 3.0 : 2.2}
          angle={0.6}
          penumbra={0.5}
          color="#7dd3fc"
          castShadow={high}
        />
      )}

      {/* Ambient light for base illumination - SIGNIFICANTLY BOOSTED */}
      {debug.showAmbientLight && <ambientLight intensity={high ? 0.8 : 0.6} color="#20304a" />}
    </>
  );
};
