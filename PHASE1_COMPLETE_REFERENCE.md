# PHASE 1 — COMPLETE REFERENCE DOCUMENT

## 1. NEW FILES — FULL CONTENTS

---

### File 1: `fallat_crewai_dashboard/src/components/3d/effects/SceneLighting.tsx`

```tsx
import React from 'react';
import * as THREE from 'three';

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
        shadow-normalBias={0.02}
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
```

---

### File 2: `fallat_crewai_dashboard/src/components/3d/effects/PostFX.tsx`

```tsx
import React from 'react';
import { EffectComposer, Bloom, SMAA } from '@react-three/postprocessing';

/**
 * Post-processing effects: Bloom and Anti-aliasing
 * - Bloom: Tasteful glow effect (not overpowering)
 * - SMAA: Enhanced anti-aliasing for cleaner edges
 */
export const PostFX: React.FC = () => {
  return (
    <EffectComposer>
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
```

---

### File 3: `fallat_crewai_dashboard/src/components/3d/effects/CameraRig.tsx`

```tsx
import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../../stores/agentStore';
import { useAgentStore } from '../../../stores/agentStore';

// Default camera position
const DEFAULT_CAMERA_POSITION = new THREE.Vector3(0, 30, 50);
const DEFAULT_CAMERA_TARGET = new THREE.Vector3(0, 0, 0);
const DEFAULT_FOV = 50;

export interface CameraRigRef {
  resetView: () => void;
  focusOnPosition: (position: [number, number, number], target?: [number, number, number]) => void;
}

interface CameraRigProps {
  targetAgent?: Agent | null;
  enableFocus?: boolean;
}

export const CameraRig = forwardRef<CameraRigRef, CameraRigProps>(
  ({ targetAgent, enableFocus = true }, ref) => {
    const { camera } = useThree();
    const controlsRef = useRef<any>(null);
    const isAnimatingRef = useRef(false);
    const { selectedDepartment } = useAgentStore();

    // Default camera setup
    useEffect(() => {
      if (!camera) return;
      
      // Set initial camera position
      camera.position.copy(DEFAULT_CAMERA_POSITION);
      camera.fov = DEFAULT_FOV;
      camera.updateProjectionMatrix();
    }, [camera]);

    // Reset camera to default view
    const resetView = () => {
      if (!controlsRef.current || !camera) return;
      
      isAnimatingRef.current = true;
      
      // Smoothly animate to default position
      const startPos = camera.position.clone();
      const startTarget = controlsRef.current.target.clone();
      
      let progress = 0;
      const duration = 1000; // 1 second
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        // Ease in-out
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        // Lerp camera position
        camera.position.lerpVectors(startPos, DEFAULT_CAMERA_POSITION, eased);
        
        // Lerp target
        controlsRef.current.target.lerpVectors(startTarget, DEFAULT_CAMERA_TARGET, eased);
        controlsRef.current.update();
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          isAnimatingRef.current = false;
        }
      };
      
      animate();
    };

    // Focus on a specific position
    const focusOnPosition = (
      position: [number, number, number],
      target?: [number, number, number]
    ) => {
      if (!controlsRef.current || !camera) return;
      
      isAnimatingRef.current = true;
      
      const targetPos = new THREE.Vector3(...position);
      const lookAtPos = target ? new THREE.Vector3(...target) : new THREE.Vector3(...position);
      
      // Calculate camera position offset (behind and above)
      const direction = new THREE.Vector3()
        .subVectors(lookAtPos, camera.position)
        .normalize();
      const offset = direction.multiplyScalar(-15); // Distance from target
      offset.y += 8; // Height offset
      
      const finalCameraPos = new THREE.Vector3()
        .addVectors(lookAtPos, offset);
      
      const startPos = camera.position.clone();
      const startTarget = controlsRef.current.target.clone();
      
      let progress = 0;
      const duration = 1500; // 1.5 seconds
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        // Ease in-out
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        // Lerp camera position
        camera.position.lerpVectors(startPos, finalCameraPos, eased);
        
        // Lerp target
        controlsRef.current.target.lerpVectors(startTarget, lookAtPos, eased);
        controlsRef.current.update();
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          isAnimatingRef.current = false;
        }
      };
      
      animate();
    };

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      resetView,
      focusOnPosition,
    }));

    // Smooth focus on selected agent/department
    useEffect(() => {
      if (!enableFocus || isAnimatingRef.current) return;
      
      if (targetAgent) {
        // Focus on selected agent
        const agentPos: [number, number, number] = [
          targetAgent.position[0],
          targetAgent.position[1] + 2,
          targetAgent.position[2],
        ];
        focusOnPosition(agentPos, agentPos);
      } else if (selectedDepartment) {
        // Focus on selected department (find zone position)
        const departmentZones = [
          { department: 'Executive Board', position: [0, 2, 0] as [number, number, number] },
          { department: 'Finance & Revenue', position: [18, 0, 0] as [number, number, number] },
          { department: 'Creative & Product', position: [-18, 0, 0] as [number, number, number] },
          { department: 'Tech & Infrastructure', position: [0, 0, 18] as [number, number, number] },
          { department: 'Legal & Sovereignty', position: [0, 0, -18] as [number, number, number] },
          { department: 'Health & Human Factor', position: [12.7, 0, 12.7] as [number, number, number] },
          { department: 'Corporate Analytics', position: [-12.7, 0, 12.7] as [number, number, number] },
          { department: 'Corporate Execution', position: [12.7, 0, -12.7] as [number, number, number] },
          { department: 'Email Marketing', position: [-12.7, 0, -12.7] as [number, number, number] },
          { department: 'Revenue Strategy Cell', position: [-18.5, 0, 7.7] as [number, number, number] },
          { department: 'Revenue Execution', position: [18.5, 0, -7.7] as [number, number, number] },
          { department: 'Lead Generation & Acquisition', position: [-7.7, 0, 18.5] as [number, number, number] },
          { department: 'Website Growth & Digital Presence', position: [7.7, 0, -18.5] as [number, number, number] },
        ];
        
        const zone = departmentZones.find(z => z.department === selectedDepartment);
        if (zone) {
          focusOnPosition(zone.position, zone.position);
        }
      }
    }, [targetAgent, selectedDepartment, enableFocus]);

    // Smooth camera updates
    useFrame(() => {
      if (controlsRef.current) {
        controlsRef.current.update();
      }
    });

    return (
      <OrbitControls
        ref={controlsRef}
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={8}
        maxDistance={150}
        minPolarAngle={0.1} // Prevent going below ground
        maxPolarAngle={Math.PI / 2.1} // Prevent flipping upside down
        enableDamping={true}
        dampingFactor={0.05}
        target={DEFAULT_CAMERA_TARGET}
      />
    );
  }
);

CameraRig.displayName = 'CameraRig';
```

---

## 2. EXACT DIFFS FOR MODIFIED FILES

---

### File: `fallat_crewai_dashboard/src/components/dashboard/Office3DView.tsx`

#### ADDED (Line 116-125):
```tsx
          <Canvas
            shadows
            dpr={[1, 1.5]}                    // ← NEW: Device pixel ratio
            gl={{
              preserveDrawingBuffer: true,
              antialias: true,
              powerPreference: "high-performance",
              failIfMajorPerformanceCaveat: false,
            }}
            camera={{ position: [0, 8, 15], fov: 60 }}  // ← NEW: Default camera for DepartmentRoom
          >
```

**Summary**: Added `dpr={[1, 1.5]}` and `camera` prop to DepartmentRoom Canvas.

---

### File: `fallat_crewai_dashboard/src/components/3d/CommandRoom3D.tsx`

#### ADDED (Lines 13-15):
```tsx
import { SceneLighting } from './effects/SceneLighting';
import { PostFX } from './effects/PostFX';
import { CameraRig, CameraRigRef } from './effects/CameraRig';
```

#### REMOVED (Line 107):
```tsx
// CameraController removed - replaced by CameraRig component
```

#### REMOVED (Lines 104-135 - old CameraController):
```tsx
const CameraController: React.FC<{ targetAgent: Agent | null }> = ({ targetAgent }) => {
    const { camera } = useThree();
    const controlsRef = useRef<any>(null);

    useEffect(() => {
        if (targetAgent && controlsRef.current) {
            const zone = DEPARTMENT_ZONES.find(z => z.department === targetAgent.department);
            if (zone) {
                controlsRef.current.target.set(...zone.position);
                camera.position.set(
                    zone.position[0] + 5,
                    zone.position[1] + 8,
                    zone.position[2] + 5
                );
            }
        }
    }, [targetAgent, camera]);

    return (
        <OrbitControls
            ref={controlsRef}
            enablePan
            enableZoom
            enableRotate
            minDistance={5}
            maxDistance={150}
            maxPolarAngle={Math.PI / 2.1}
            enableDamping
            dampingFactor={0.05}
        />
    );
};
```

#### CHANGED (Line 109):
```tsx
// BEFORE:
const Scene: React.FC = () => {

// AFTER:
const Scene: React.FC<{ cameraRigRef?: React.RefObject<CameraRigRef> }> = ({ cameraRigRef }) => {
```

#### REPLACED (Lines 208-241):
```tsx
// BEFORE:
            <PerspectiveCamera makeDefault position={[0, 30, 50]} fov={50} />
            <ambientLight intensity={0.6} />
            <directionalLight position={[10, 15, 5]} intensity={1.2} castShadow />
            <pointLight position={[0, 20, 0]} intensity={2} distance={50} color="#00ffff" />
            <pointLight position={[-20, 10, -20]} intensity={1} distance={40} color="#ff1493" />
            <pointLight position={[20, 10, 20]} intensity={1} distance={40} color="#00d4ff" />

// AFTER:
            <PerspectiveCamera makeDefault position={[0, 30, 50]} fov={50} />
            
            {/* Cinematic lighting setup */}
            <SceneLighting />
```

#### REPLACED (Line 333):
```tsx
// BEFORE:
            <CameraController targetAgent={selectedAgent} />

// AFTER:
            {/* Camera rig with orbit limits and focus capabilities */}
            <CameraRig ref={cameraRigRef} targetAgent={selectedAgent} enableFocus={true} />

            {/* Post-processing effects */}
            <PostFX />
```

#### ADDED (Line 313):
```tsx
export const CommandRoom3D: React.FC<{ vrEnabled?: boolean }> = ({ vrEnabled = false }) => {
    const cameraRigRef = useRef<CameraRigRef>(null);  // ← NEW: Camera rig ref
```

#### CHANGED (Line 316):
```tsx
// BEFORE:
        <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-cyan-500/20">

// AFTER:
        <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-cyan-500/20 relative">
```

#### ADDED (Line 319):
```tsx
            <Canvas 
                shadows
                dpr={[1, 1.5]}                    // ← NEW: Device pixel ratio
                gl={{ 
```

#### ADDED (Line 325):
```tsx
                }}
                camera={{ position: [0, 30, 50], fov: 50 }}  // ← NEW: Default camera
                onCreated={({ gl }) => {
```

#### CHANGED (Lines 338-348):
```tsx
// BEFORE:
                {vrEnabled ? (
                    <XR store={xrStore}>
                        <Suspense fallback={null}>
                            <Scene />
                        </Suspense>
                    </XR>
                ) : (
                    <Suspense fallback={null}>
                        <Scene />
                    </Suspense>
                )}

// AFTER:
                {vrEnabled ? (
                    <XR store={xrStore}>
                        <Suspense fallback={null}>
                            <Scene cameraRigRef={cameraRigRef} />
                        </Suspense>
                    </XR>
                ) : (
                    <Suspense fallback={null}>
                        <Scene cameraRigRef={cameraRigRef} />
                    </Suspense>
                )}
```

#### ADDED (Lines 351-358):
```tsx
            </Canvas>
            
            {/* Reset View Button */}
            <button
                onClick={() => cameraRigRef.current?.resetView()}
                className="absolute top-4 right-4 z-10 bg-black/80 backdrop-blur-xl px-4 py-2 rounded-lg border border-cyan-500/50 text-cyan-300 text-xs font-bold hover:bg-black/90 hover:border-cyan-500 transition-all pointer-events-auto"
                title="Reset camera to default view"
            >
                Reset View
            </button>
```

---

## 3. TUNING CONSTANTS — WHERE TO ADJUST

---

### 🌫️ FOG SETTINGS
**File**: `fallat_crewai_dashboard/src/components/3d/effects/SceneLighting.tsx`  
**Line**: 14

```tsx
<fog attach="fog" args={['#030714', 30, 120]} />
//                      ^^^^^^^^  ^^  ^^^
//                      color     near far
```

**Parameters**:
- **Color**: `'#030714'` - Dark bluish fog color (matches UI theme)
  - To change: Replace with any hex color (e.g., `'#000000'` for black, `'#1a1a2e'` for lighter blue)
- **Near**: `30` - Distance where fog starts (in world units)
  - Lower = fog starts closer (more visible)
  - Higher = fog starts farther (less visible)
- **Far**: `120` - Distance where fog is fully opaque
  - Lower = fog becomes opaque sooner (more dramatic)
  - Higher = fog becomes opaque later (more subtle)

**Example Adjustments**:
```tsx
// More dramatic fog (starts closer, becomes opaque sooner)
<fog attach="fog" args={['#030714', 20, 80]} />

// Subtle fog (starts farther, becomes opaque later)
<fog attach="fog" args={['#030714', 50, 200]} />

// Different color (warmer tone)
<fog attach="fog" args={['#1a0a2e', 30, 120]} />
```

---

### 💡 LIGHTING SETTINGS
**File**: `fallat_crewai_dashboard/src/components/3d/effects/SceneLighting.tsx`

#### Key Light (Main Directional Light)
**Lines**: 17-31

```tsx
<directionalLight
  position={[15, 25, 10]}        // ← Position: [x, y, z]
  intensity={1.2}                // ← Brightness (0-2+)
  castShadow
  shadow-mapSize-width={2048}   // ← Shadow quality (1024, 2048, 4096)
  shadow-mapSize-height={2048}
  shadow-camera-left={-50}       // ← Shadow camera bounds
  shadow-camera-right={50}
  shadow-camera-top={50}
  shadow-camera-bottom={-50}
  shadow-camera-near={0.1}       // ← Shadow camera near/far
  shadow-camera-far={200}
  shadow-bias={-0.0001}          // ← Shadow artifacts fix
  shadow-normalBias={0.02}
/>
```

**Key Tuning Parameters**:
- **Position**: `[15, 25, 10]` - Light direction
  - X: Horizontal angle (positive = right, negative = left)
  - Y: Vertical height (higher = more top-down)
  - Z: Depth (positive = forward, negative = backward)
- **Intensity**: `1.2` - Light brightness
  - `0.5-0.8` = Subtle/dramatic
  - `1.0-1.5` = Normal/bright
  - `2.0+` = Very bright
- **Shadow Map Size**: `2048` - Shadow quality vs performance
  - `1024` = Lower quality, better performance
  - `2048` = Balanced (current)
  - `4096` = Higher quality, lower performance

#### Fill Light (Hemisphere Light)
**Lines**: 34-38

```tsx
<hemisphereLight
  intensity={0.4}                // ← Ambient fill brightness
  color="#1a1a2e"                // ← Sky color (top)
  groundColor="#0a0a14"          // ← Ground color (bottom)
/>
```

**Tuning**:
- **Intensity**: `0.4` - Ambient fill amount
  - `0.2-0.3` = Darker scene
  - `0.4-0.6` = Balanced
  - `0.7-1.0` = Brighter scene
- **Colors**: Sky and ground colors for ambient tint

#### Rim Light (Back Light)
**Lines**: 41-45

```tsx
<directionalLight
  position={[-10, 15, -15]}      // ← Position (behind scene)
  intensity={0.3}                 // ← Rim light brightness
  color="#4a90e2"                 // ← Rim light color (blue tint)
/>
```

**Tuning**:
- **Position**: `[-10, 15, -15]` - Behind and to the side
- **Intensity**: `0.3` - Rim highlight strength
  - `0.1-0.2` = Subtle rim
  - `0.3-0.5` = Visible rim
  - `0.6+` = Strong rim
- **Color**: `"#4a90e2"` - Rim tint (blue for cool, `#ffaa44` for warm)

#### Ambient Light
**Lines**: 48

```tsx
<ambientLight intensity={0.3} color="#1a1a2e" />
```

**Tuning**:
- **Intensity**: `0.3` - Base scene illumination
- **Color**: `"#1a1a2e"` - Overall scene tint

---

### ✨ BLOOM SETTINGS
**File**: `fallat_crewai_dashboard/src/components/3d/effects/PostFX.tsx`  
**Lines**: 12-17

```tsx
<Bloom
  intensity={0.4}                 // ← Glow strength (0-2+)
  luminanceThreshold={0.9}       // ← Brightness threshold (0-1)
  luminanceSmoothing={0.9}       // ← Glow smoothness (0-1)
  height={300}                   // ← Performance: render height
/>
```

**Key Tuning Parameters**:
- **Intensity**: `0.4` - How strong the glow is
  - `0.1-0.3` = Subtle glow
  - `0.4-0.6` = Balanced (current)
  - `0.7-1.0` = Strong glow
  - `1.5+` = Very strong (may wash out UI)
- **Luminance Threshold**: `0.9` - Only objects brighter than this glow
  - `0.7-0.8` = More objects glow (lower threshold)
  - `0.9-0.95` = Only very bright objects glow (current)
  - `0.98+` = Only extremely bright objects glow
- **Luminance Smoothing**: `0.9` - How smooth the glow transition is
  - `0.7-0.8` = Sharper transition
  - `0.9-0.95` = Smooth transition (current)
- **Height**: `300` - Performance optimization (lower = faster)
  - `200` = Faster, lower quality
  - `300` = Balanced (current)
  - `600+` = Higher quality, slower

**Example Adjustments**:
```tsx
// More dramatic bloom (stronger, affects more objects)
<Bloom
  intensity={0.7}
  luminanceThreshold={0.8}
  luminanceSmoothing={0.9}
  height={300}
/>

// Subtle bloom (weaker, only very bright objects)
<Bloom
  intensity={0.2}
  luminanceThreshold={0.95}
  luminanceSmoothing={0.9}
  height={300}
/>
```

---

### 📹 CAMERA SETTINGS
**File**: `fallat_crewai_dashboard/src/components/3d/effects/CameraRig.tsx`

#### Default Camera Position
**Lines**: 9-11

```tsx
const DEFAULT_CAMERA_POSITION = new THREE.Vector3(0, 30, 50);
const DEFAULT_CAMERA_TARGET = new THREE.Vector3(0, 0, 0);
const DEFAULT_FOV = 50;
```

**Tuning**:
- **Position**: `[0, 30, 50]` - Default camera location
  - X: Horizontal offset
  - Y: Height (30 = above scene)
  - Z: Distance from center (50 = far back)
- **Target**: `[0, 0, 0]` - What camera looks at (scene center)
- **FOV**: `50` - Field of view (degrees)
  - `30-40` = Narrow (zoomed in)
  - `50-60` = Normal (current)
  - `70-90` = Wide (fisheye effect)

#### Orbit Controls Limits
**Lines**: 191-194

```tsx
minDistance={8}                  // ← Minimum zoom (closest)
maxDistance={150}                // ← Maximum zoom (farthest)
minPolarAngle={0.1}              // ← Prevent going below ground
maxPolarAngle={Math.PI / 2.1}    // ← Prevent flipping upside down
```

**Tuning**:
- **Min Distance**: `8` - Closest zoom
  - `5` = Can get very close
  - `8-10` = Comfortable close (current)
  - `15+` = Can't get very close
- **Max Distance**: `150` - Farthest zoom
  - `100` = Limited zoom out
  - `150-200` = Good range (current)
  - `300+` = Can zoom very far
- **Min Polar Angle**: `0.1` - Prevents going below ground
  - `0` = Can go below ground
  - `0.1-0.2` = Slight limit (current)
- **Max Polar Angle**: `Math.PI / 2.1` - Prevents flipping
  - `Math.PI / 2` = Exactly 90° (can flip)
  - `Math.PI / 2.1` = Slightly less (current, prevents flip)
  - `Math.PI / 2.5` = More restrictive

#### Damping
**Line**: 196

```tsx
dampingFactor={0.05}
```

**Tuning**:
- `0.01-0.03` = More responsive (less damping)
- `0.05-0.08` = Smooth (current)
- `0.1+` = Very smooth (sluggish)

#### Animation Durations
**Lines**: 51, 106

```tsx
const duration = 1000;  // Reset view: 1 second
const duration = 1500;  // Focus animation: 1.5 seconds
```

**Tuning**:
- `500-800` = Fast animation
- `1000-1500` = Smooth (current)
- `2000+` = Slow animation

#### Focus Offset
**Lines**: 96-97

```tsx
const offset = direction.multiplyScalar(-15); // Distance from target
offset.y += 8; // Height offset
```

**Tuning**:
- **Distance**: `-15` - How far camera sits from focus point
  - `-10` = Closer to target
  - `-15` = Comfortable distance (current)
  - `-20` = Farther from target
- **Height Offset**: `8` - How high camera sits above target
  - `5` = Lower angle
  - `8-10` = Comfortable height (current)
  - `15+` = Higher angle

---

### 🎨 CANVAS SETTINGS
**File**: `fallat_crewai_dashboard/src/components/3d/CommandRoom3D.tsx`  
**Line**: 319

```tsx
dpr={[1, 1.5]}  // Device Pixel Ratio
```

**Tuning**:
- `[1, 1]` = Standard resolution (faster)
- `[1, 1.5]` = Balanced (current)
- `[1, 2]` = High resolution (slower, sharper)
- `[0.5, 1]` = Lower resolution (faster, less sharp)

---

## 📍 QUICK REFERENCE — ALL CONSTANTS

| Setting | File | Line | Current Value | Tuning Range |
|---------|------|------|---------------|--------------|
| **Fog Color** | SceneLighting.tsx | 14 | `'#030714'` | Any hex color |
| **Fog Near** | SceneLighting.tsx | 14 | `30` | 10-50 |
| **Fog Far** | SceneLighting.tsx | 14 | `120` | 80-200 |
| **Key Light Position** | SceneLighting.tsx | 18 | `[15, 25, 10]` | Any [x,y,z] |
| **Key Light Intensity** | SceneLighting.tsx | 19 | `1.2` | 0.5-2.0 |
| **Shadow Map Size** | SceneLighting.tsx | 21-22 | `2048` | 1024-4096 |
| **Fill Light Intensity** | SceneLighting.tsx | 35 | `0.4` | 0.2-1.0 |
| **Rim Light Intensity** | SceneLighting.tsx | 43 | `0.3` | 0.1-0.6 |
| **Ambient Light Intensity** | SceneLighting.tsx | 48 | `0.3` | 0.1-0.5 |
| **Bloom Intensity** | PostFX.tsx | 13 | `0.4` | 0.1-1.0 |
| **Bloom Threshold** | PostFX.tsx | 14 | `0.9` | 0.7-0.98 |
| **Bloom Smoothing** | PostFX.tsx | 15 | `0.9` | 0.7-0.95 |
| **Bloom Height** | PostFX.tsx | 16 | `300` | 200-600 |
| **Default Camera Position** | CameraRig.tsx | 9 | `[0, 30, 50]` | Any [x,y,z] |
| **Default FOV** | CameraRig.tsx | 11 | `50` | 30-90 |
| **Min Distance** | CameraRig.tsx | 191 | `8` | 5-15 |
| **Max Distance** | CameraRig.tsx | 192 | `150` | 100-300 |
| **Damping Factor** | CameraRig.tsx | 196 | `0.05` | 0.01-0.1 |
| **Focus Distance** | CameraRig.tsx | 96 | `-15` | -10 to -20 |
| **Focus Height** | CameraRig.tsx | 97 | `8` | 5-15 |
| **Reset Duration** | CameraRig.tsx | 51 | `1000` | 500-2000 |
| **Focus Duration** | CameraRig.tsx | 106 | `1500` | 1000-2500 |
| **Canvas DPR** | CommandRoom3D.tsx | 319 | `[1, 1.5]` | [1,1] to [1,2] |

---

## 🎯 RECOMMENDED ADJUSTMENTS

### For Better Performance:
- Shadow map: `2048` → `1024`
- Bloom height: `300` → `200`
- Canvas DPR: `[1, 1.5]` → `[1, 1]`

### For More Dramatic Look:
- Fog far: `120` → `80`
- Key light intensity: `1.2` → `1.5`
- Bloom intensity: `0.4` → `0.6`
- Bloom threshold: `0.9` → `0.8`

### For Subtle/Professional Look:
- Fog far: `120` → `150`
- Key light intensity: `1.2` → `1.0`
- Bloom intensity: `0.4` → `0.2`
- Bloom threshold: `0.9` → `0.95`

---

**All constants are clearly marked in their respective files. Adjust values directly in the component files listed above.**
