import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

interface FloatingMetricProps {
  position: [number, number, number];
  label: string;
  value: string | number;
  color: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const FloatingMetric: React.FC<FloatingMetricProps> = ({ 
  position, 
  label, 
  value, 
  color,
  trend = 'neutral'
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const safeColor = color || '#00d4ff';

  useFrame((state) => {
    if (!groupRef.current) return;
    const time = state.clock.getElapsedTime();
    groupRef.current.position.y = position[1] + Math.sin(time * 0.5) * 0.3;
    groupRef.current.rotation.y = Math.sin(time * 0.3) * 0.1;
  });

  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';

  return (
    <group ref={groupRef} position={position}>
      <Html
        center
        distanceFactor={15}
        style={{
          pointerEvents: 'none',
          userSelect: 'none',
        }}
      >
        <div
          className="backdrop-blur-xl px-4 py-3 rounded-xl border-2 shadow-2xl"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.95)',
            borderColor: safeColor,
            boxShadow: `0 0 30px ${safeColor}60, inset 0 0 15px ${safeColor}20`,
            minWidth: '120px',
          }}
        >
          <div className="text-white text-xs font-semibold mb-1" style={{ color: '#9ca3af' }}>
            {label}
          </div>
          <div className="flex items-center gap-2">
            <div
              className="text-2xl font-bold"
              style={{
                color: safeColor,
                textShadow: `0 0 10px ${safeColor}`,
              }}
            >
              {value}
            </div>
            {trend !== 'neutral' && (
              <div
                className="text-lg"
                style={{
                  color: trend === 'up' ? '#10b981' : '#ef4444',
                }}
              >
                {trendIcon}
              </div>
            )}
          </div>
        </div>
      </Html>
      
      <pointLight
        color={safeColor}
        intensity={0.5}
        distance={5}
        decay={2}
      />
    </group>
  );
};
