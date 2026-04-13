// fallat_crewai_dashboard/src/components/3d/environment/CommandDeckShell.tsx
import React, { useMemo } from "react";
import * as THREE from "three";
import { RoundedBox } from "@react-three/drei";
import { createDeckMaterials } from "./DeckMaterials";

type Props = {
  /** Toggle star backdrop; actual stars component mounted separately */
  showGrid?: boolean;
};

export const CommandDeckShell: React.FC<Props> = ({ showGrid = true }) => {
  const mats = useMemo(() => createDeckMaterials(), []);

  // Dimensions tuned to your zone layout (~ +/- 20 units)
  const PLATFORM_W = 80;
  const PLATFORM_D = 80;
  const PLATFORM_H = 1.2;
  const PLATFORM_R = 34;

  const FLOOR_W = 200;
  const FLOOR_D = 200;

  // Back wall
  const WALL_W = 200;
  const WALL_H = 80;

  // Positions
  const platformY = -PLATFORM_H / 2; // top of platform at y=0
  const floorY = -4.0;
  const wallZ = -80;
  const wallY = 20;

  return (
    <group>
      {/* --- FLOOR --- */}
      {/* Base Floor (Reflective Dark Glass) */}
      <mesh
        receiveShadow
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, floorY, 0]}
      >
        <planeGeometry args={[FLOOR_W, FLOOR_D]} />
        <meshStandardMaterial 
            color="#050505" // Slightly lighter black
            roughness={0.2} // Increased roughness to blur reflections
            metalness={0.8} // Reduced metalness
            emissive="#000000"
            emissiveIntensity={0}
        />
      </mesh>

      {/* Cyber Grid Overlay (Cyan/Magenta) */}
      {showGrid && (
        <group position={[0, floorY + 0.05, 0]}>
            {/* Primary Grid */}
            <gridHelper
            args={[300, 60, "#00ffff", "#002233"]}
            position={[0, 0, 0]}
            />
            {/* Secondary Grid (finer) */}
            <gridHelper
            args={[300, 150, "#ff00ff", "#000000"]}
            position={[0, 0.01, 0]}
            />
        </group>
      )}

      {/* --- COMMAND DECK --- */}
      {/* Circular command deck base */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.1, 0]} receiveShadow>
        <circleGeometry args={[PLATFORM_R, 64]} />
        <meshStandardMaterial 
            color="#050510"
            roughness={0.1}
            metalness={0.9}
            emissive="#004488"
            emissiveIntensity={0.5}
        />
      </mesh>

      {/* Volumetric Light Pillars (Simulated with transparent cones) */}
      {[0, 90, 180, 270].map((deg) => {
          const rad = (deg * Math.PI) / 180;
          return (
            <mesh key={`light-${deg}`} position={[Math.cos(rad) * 25, 10, Math.sin(rad) * 25]} rotation={[0, 0, 0]}>
                <coneGeometry args={[2, 40, 32, 1, true]} />
                <meshBasicMaterial 
                    color="#00ffff" 
                    transparent 
                    opacity={0.08} 
                    side={THREE.DoubleSide} 
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                />
            </mesh>
          );
      })}

      {/* Rotating Tech Ring (Animation would be handled by a ref and useFrame, keeping it static for now but visually complex) */}
      <group position={[0, 5, 0]} rotation={[0.2, 0, 0]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[15, 0.2, 16, 100]} />
            <meshBasicMaterial color="#00ffff" toneMapped={false} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, Math.PI / 4]}>
            <torusGeometry args={[18, 0.1, 16, 100]} />
            <meshBasicMaterial color="#ff00ff" toneMapped={false} />
        </mesh>
      </group>

      {/* Primary halo glow */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.105, 0]}>
        <ringGeometry args={[PLATFORM_R - 6, PLATFORM_R - 3.4, 128]} />
        <meshBasicMaterial color="#0fe7ff" transparent opacity={0.3} blending={THREE.AdditiveBlending} />
      </mesh>

      {/* Inner ring lanes */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.14, 0]}>
        <ringGeometry args={[18, 18.2, 128]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.14, 0]}>
        <ringGeometry args={[12.5, 12.7, 128]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Central Hub Glow */}
      <pointLight position={[0, 2, 0]} intensity={2} color="#00f2ff" distance={15} decay={2} />

      {/* Executive dais */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.35, 0]}>
        <cylinderGeometry args={[9, 9, 0.7, 64]} />
        <primitive object={mats.darkMetal} attach="material" />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 0.36, 0]}>
        <ringGeometry args={[8.8, 9.0, 128]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Main platform (where your zones live) - UPGRADED SURFACE */}
      <RoundedBox
        args={[PLATFORM_W, PLATFORM_H, PLATFORM_D]}
        radius={2.4}
        smoothness={6}
        position={[0, platformY, 0]}
        castShadow
        receiveShadow
      >
        <meshStandardMaterial 
            color="#050a10"
            roughness={0.15}
            metalness={0.8}
            emissive="#001133"
            emissiveIntensity={0.15}
        />
      </RoundedBox>

      {/* Platform Surface Grid - VISIBLE ON TOP - Lifted higher to prevent z-fighting */}
      {showGrid && (
        <group position={[0, 0.05, 0]}>
            <gridHelper
                args={[80, 40, "#00ffff", "#001133"]}
                position={[0, 0, 0]}
            />
            <gridHelper
                args={[80, 80, "#ff00ff", "#000000"]}
                position={[0, 0.01, 0]}
            />
        </group>
      )}

      {/* NEW: Holographic Perimeter Fence - Undeniable visual update */}
      <mesh position={[0, platformY + 1.5, 0]}>
        <cylinderGeometry args={[PLATFORM_R - 0.5, PLATFORM_R - 0.5, 2, 64, 1, true]} />
        <meshBasicMaterial 
            color="#00ffff" 
            transparent 
            opacity={0.1} 
            side={THREE.DoubleSide} 
            blending={THREE.AdditiveBlending}
            depthWrite={false}
        />
      </mesh>
      <mesh position={[0, platformY + 2.5, 0]} rotation={[-Math.PI/2, 0, 0]}>
        <ringGeometry args={[PLATFORM_R - 0.6, PLATFORM_R - 0.4, 64]} />
        <meshBasicMaterial color="#00ffff" />
      </mesh>

      {/* Perimeter wall ring */}
      <mesh position={[0, platformY + 1.2, 0]}>
        <cylinderGeometry args={[PLATFORM_R + 4, PLATFORM_R + 4, 3.5, 128, 1, true]} />
        <primitive object={mats.darkMetal} attach="material" />
      </mesh>

      {/* Glowing rim */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, platformY + 2.9, 0]}>
        <ringGeometry args={[PLATFORM_R + 3.8, PLATFORM_R + 4.0, 128]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Perimeter accent fins */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
        const rad = (deg * Math.PI) / 180;
        const x = Math.cos(rad) * (PLATFORM_R + 3.8);
        const z = Math.sin(rad) * (PLATFORM_R + 3.8);
        return (
          <group key={`fin-${deg}`} position={[x, platformY + 2.1, z]} rotation={[0, rad, 0]}>
            <mesh>
              <boxGeometry args={[0.6, 2.6, 3.2]} />
              <primitive object={mats.darkMetal} attach="material" />
            </mesh>
            <mesh position={[0, 0, 1.65]}>
              <boxGeometry args={[0.2, 2.0, 0.1]} />
              <primitive object={mats.emissiveLine} attach="material" />
            </mesh>
          </group>
        );
      })}

      {/* Platform edge light strips */}
      <mesh position={[0, platformY + PLATFORM_H / 2 + 0.03, PLATFORM_D / 2 - 0.25]}>
        <boxGeometry args={[PLATFORM_W - 6, 0.05, 0.1]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh position={[0, platformY + PLATFORM_H / 2 + 0.03, -PLATFORM_D / 2 + 0.25]}>
        <boxGeometry args={[PLATFORM_W - 6, 0.05, 0.1]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh position={[PLATFORM_W / 2 - 0.25, platformY + PLATFORM_H / 2 + 0.03, 0]}>
        <boxGeometry args={[0.1, 0.05, PLATFORM_D - 6]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh position={[-PLATFORM_W / 2 + 0.25, platformY + PLATFORM_H / 2 + 0.03, 0]}>
        <boxGeometry args={[0.1, 0.05, PLATFORM_D - 6]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Back wall for depth */}
      <mesh receiveShadow position={[0, wallY, wallZ]}>
        <planeGeometry args={[WALL_W, WALL_H]} />
        <primitive object={mats.darkMetal} attach="material" />
      </mesh>

      {/* Back wall glow stripes */}
      <mesh position={[0, wallY + 6, wallZ + 0.2]}>
        <boxGeometry args={[120, 0.2, 0.4]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>
      <mesh position={[0, wallY - 8, wallZ + 0.2]}>
        <boxGeometry args={[100, 0.2, 0.4]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Holo panels (subtle translucent "console" feel) */}
      <mesh position={[0, 10, -30]} rotation={[0, 0, 0]}>
        <boxGeometry args={[36, 12, 0.4]} />
        <primitive object={mats.holoGlass} attach="material" />
      </mesh>

      {/* Floating particles for atmosphere */}
      {/* (Particles are handled by separate component, but we can add some static detail here) */}
    </group>
  );
};
