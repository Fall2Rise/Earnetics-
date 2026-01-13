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

  const FLOOR_W = 160;
  const FLOOR_D = 160;

  // Back wall
  const WALL_W = 160;
  const WALL_H = 70;

  // Positions
  const platformY = -PLATFORM_H / 2; // top of platform at y=0
  const floorY = -3.0;
  const wallZ = -70;
  const wallY = 22;

  return (
    <group>
      {/* Floor plane (subtle metal base) */}
      <mesh
        receiveShadow
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, floorY, 0]}
      >
        <planeGeometry args={[FLOOR_W, FLOOR_D]} />
        <primitive object={mats.darkMetal} attach="material" />
      </mesh>

      {/* Optional grid helper overlay for legibility */}
      {showGrid && (
        <gridHelper
          args={[120, 60, "#0a2940", "#08304e"]}
          position={[0, floorY + 0.02, 0]}
        />
      )}

      {/* Main platform (where your zones live) */}
      <RoundedBox
        args={[PLATFORM_W, PLATFORM_H, PLATFORM_D]}
        radius={2.4}
        smoothness={6}
        position={[0, platformY, 0]}
        castShadow
        receiveShadow
      >
        <primitive object={mats.softPanel} attach="material" />
      </RoundedBox>

      {/* Platform edge light strips */}
      <mesh
        castShadow={false}
        receiveShadow={false}
        position={[0, platformY + PLATFORM_H / 2 + 0.03, PLATFORM_D / 2 - 0.25]}
      >
        <boxGeometry args={[PLATFORM_W - 6, 0.08, 0.12]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh
        castShadow={false}
        receiveShadow={false}
        position={[0, platformY + PLATFORM_H / 2 + 0.03, -PLATFORM_D / 2 + 0.25]}
      >
        <boxGeometry args={[PLATFORM_W - 6, 0.08, 0.12]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh
        castShadow={false}
        receiveShadow={false}
        position={[PLATFORM_W / 2 - 0.25, platformY + PLATFORM_H / 2 + 0.03, 0]}
      >
        <boxGeometry args={[0.12, 0.08, PLATFORM_D - 6]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      <mesh
        castShadow={false}
        receiveShadow={false}
        position={[-PLATFORM_W / 2 + 0.25, platformY + PLATFORM_H / 2 + 0.03, 0]}
      >
        <boxGeometry args={[0.12, 0.08, PLATFORM_D - 6]} />
        <primitive object={mats.emissiveLine} attach="material" />
      </mesh>

      {/* Back wall for depth */}
      <mesh receiveShadow position={[0, wallY, wallZ]}>
        <planeGeometry args={[WALL_W, WALL_H]} />
        <primitive object={mats.darkMetal} attach="material" />
      </mesh>

      {/* Side frames */}
      <mesh
        castShadow
        receiveShadow
        position={[FLOOR_W / 2 - 6, wallY, wallZ + 5]}
      >
        <boxGeometry args={[3, WALL_H, 12]} />
        <primitive object={mats.softPanel} attach="material" />
      </mesh>

      <mesh
        castShadow
        receiveShadow
        position={[-FLOOR_W / 2 + 6, wallY, wallZ + 5]}
      >
        <boxGeometry args={[3, WALL_H, 12]} />
        <primitive object={mats.softPanel} attach="material" />
      </mesh>

      {/* Holo panels (subtle translucent "console" feel) */}
      <mesh position={[0, 10, -30]} rotation={[0, 0, 0]}>
        <boxGeometry args={[36, 12, 0.4]} />
        <primitive object={mats.holoGlass} attach="material" />
      </mesh>

      {/* Subtle corner accent lights */}
      <pointLight
        position={[28, 8, 28]}
        intensity={0.45}
        distance={120}
        color={new THREE.Color("#00eaff")}
      />
      <pointLight
        position={[-28, 8, 28]}
        intensity={0.35}
        distance={120}
        color={new THREE.Color("#2b7cff")}
      />
      <pointLight
        position={[28, 8, -28]}
        intensity={0.28}
        distance={120}
        color={new THREE.Color("#00eaff")}
      />
      <pointLight
        position={[-28, 8, -28]}
        intensity={0.22}
        distance={120}
        color={new THREE.Color("#2b7cff")}
      />
    </group>
  );
};
