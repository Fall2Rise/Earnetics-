import React, { useEffect, useState, useMemo } from 'react';
import { EffectComposer, Bloom, SMAA, ChromaticAberration, Noise, Vignette } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import { useThree } from '@react-three/fiber';
import { useDebugStore } from '../../../stores/debugStore';

/**
 * Post-processing effects: Bloom and Anti-aliasing
 * - Bloom: Tasteful glow effect (not overpowering)
 * - SMAA: Enhanced anti-aliasing for cleaner edges
 * 
 * Includes WebGL context loss handling to prevent crashes
 */
export const PostFX: React.FC = () => {
  const { gl } = useThree();
  const [contextValid, setContextValid] = useState(true);
  const debug = useDebugStore();

  useEffect(() => {
    // Check if WebGL context is valid
    if (!gl || !gl.domElement) {
      setContextValid(false);
      return;
    }

    const canvas = gl.domElement;

    const checkContext = () => {
      try {
        if (!gl || !gl.domElement) {
          setContextValid(false);
          return false;
        }
        const context = gl.getContext();
        const isValid = context !== null && !(context as any).isContextLost?.();
        setContextValid(isValid);
        return isValid;
      } catch {
        setContextValid(false);
        return false;
      }
    };

    const handleContextLost = (event: Event) => {
      event.preventDefault();
      console.warn('[PostFX] WebGL context lost, disabling post-processing');
      setContextValid(false);
    };

    const handleContextRestored = () => {
      console.log('[PostFX] WebGL context restored');
      setContextValid(true);
    };

    // Initial check
    checkContext();

    canvas.addEventListener('webglcontextlost', handleContextLost);
    canvas.addEventListener('webglcontextrestored', handleContextRestored);

    // Periodic check in case context is lost without event
    const intervalId = setInterval(() => {
      if (!checkContext()) {
        clearInterval(intervalId);
      }
    }, 1000);

    return () => {
      clearInterval(intervalId);
      canvas.removeEventListener('webglcontextlost', handleContextLost);
      canvas.removeEventListener('webglcontextrestored', handleContextRestored);
    };
  }, [gl]);

  // Don't render if context is invalid or lost
  // Check if renderer and context are valid
  const canRender = useMemo(() => {
    if (!contextValid || !gl || !gl.domElement) return false;
    try {
      const context = gl.getContext();
      if (!context) return false;
      // Check if context is lost (if method exists)
      if (typeof (context as any).isContextLost === 'function') {
        return !(context as any).isContextLost();
      }
      // If method doesn't exist, assume context is valid
      return true;
    } catch {
      return false;
    }
  }, [contextValid, gl]);

  if (!canRender) {
    return null;
  }

  return (
    <EffectComposer multisampling={0} disableNormalPass>
      {/* Bloom effect - "TRON" sci-fi glow */}
      {debug.showBloom ? (
        <Bloom
          intensity={2.0} // Boosted for sci-fi look
          luminanceThreshold={0.4} // Lower threshold to catch more neon
          luminanceSmoothing={0.9}
          height={300}
          mipmapBlur // smoother bloom
        />
      ) : <></>}

      {/* Chromatic Aberration - Cyberpunk fringe */}
      {debug.showChromaticAberration ? (
        <ChromaticAberration
          offset={[0.0015, 0.0015] as any} // Slight boost for holographic feel
          radialModulation={true}
          modulationOffset={0}
        />
      ) : <></>}

      {/* Film Grain - DISABLED */}\n      {/* {debug.showNoise ? (\n        <Noise\n          premultiply\n          blendFunction={BlendFunction.OVERLAY}\n          opacity={0.02}\n        />\n      ) : <></>} */}

      {/* Vignette - Reduced */}
      {debug.showVignette ? (
        <Vignette
          eskil={false}
          offset={0.1}
          darkness={0.4} // Slightly lighter
        />
      ) : <></>}

      {/* SMAA anti-aliasing for cleaner edges */}
      <SMAA />
    </EffectComposer>
  );
};
