import React from 'react';
import { EffectComposer, Bloom, SMAA } from '@react-three/postprocessing';

/**
 * Post-processing effects: Bloom and Anti-aliasing
 * - Bloom: Tasteful glow effect (not overpowering)
 * - SMAA: Enhanced anti-aliasing for cleaner edges
 */
export const PostFX: React.FC = () => {
  return (
    <EffectComposer multisampling={0}>
      {/* Bloom effect - subtle glow */}
      <Bloom
        intensity={0.4}
        luminanceThreshold={0.9}
        luminanceSmoothing={0.9}
        height={300}
      />
      
      {/* SMAA anti-aliasing for cleaner edges */}
      <SMAA />
    </EffectComposer>
  );
};
