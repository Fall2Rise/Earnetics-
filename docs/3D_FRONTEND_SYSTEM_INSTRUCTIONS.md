# 3D Interactive Command Center - System Instructions

## 1. System Overview
**Objective**: Build and maintain a high-fidelity 3D immersive command center that visualizes the "Revenue Generating Factory".
**Core Concept**: Industrial High-Tech Facility (NOT Outer Space). The environment should feel like a busy, automated digital factory floor where agents are workers producing value.
**Tech Stack**: 
- **Frontend**: React, Vite, Tailwind CSS
- **3D Engine**: React Three Fiber (@react-three/fiber), Drei (@react-three/drei), Three.js
- **State Management**: Zustand
- **Real-Time**: WebSocket (Native)

---

## 2. Visual & Aesthetic Guidelines (Strict)
**Theme**: `Dark Industrial` / `Cyber-Physical Factory`
- **Colors**: Deep Obsidian (#050505), Gold (#FFD700), Electric Purple (#A855F7), Neon Cyan (#00D4FF).
- **Lighting**: Studio lighting, localized point lights, volumetric fog. **NO** global ambient white light.
- **Environment**: 
  - **Floor**: Reflective industrial grid (GridHelper), dark metallic surfaces.
  - **Background**: `Environment preset="city"` or `"studio"`.
  - **Prohibited**: Stars, nebulas, drifting space dust, planetoids. The user explicitly rejects the "Space" theme.

---

## 3. Architecture & Components

### A. Main Scene (`CommandRoom3D.tsx`)
The entry point for the 3D experience.
- **Canvas Configuration**:
  - `shadows={true}`
  - `camera={{ position: [0, 18, 26], fov: 45 }}`
  - `gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}`
- **Scene Composition**:
  1.  **Environment**: `<CommandDeckShell />` (Physical structure), `<Grid />` (Floor).
  2.  **Lighting**: `<SceneLighting />` (Custom rig with spotlights on active zones).
  3.  **Zones**: `<DepartmentZoneNew />` (Hexagonal groupings of agents).
  4.  **Effects**: `<PostFX />` (Bloom, Chromatic Aberration - **NO** Noise/Grain).

### B. The Living Artifact (`ObsidianVault.tsx`)
The central interactive object for knowledge ingestion.
- **Visuals**: 
  - **Geometry**: `ConeGeometry` (T-Rex Tooth shape).
  - **Material**: Custom `ShaderMaterial` utilizing Simplex Noise.
  - **Effect**: "Galaxy inside a Crystal Ball" - swirling Gold and Purple energy within a glass shell.
  - **Animation**: Rotates slowly; inner energy swirls independently using `uTime`.
- **Interaction**: `onClick` trigger to open `KnowledgeVaultModal`.

### C. Agent Avatars
Visual representations of autonomous agents.
- **Positioning**: Calculated dynamically based on `Department` and `Zone` configuration.
- **State Visualization**:
  - **Idle**: Standard material, subtle breathing animation.
  - **Active/Thinking**: Emits `ActivityBurst` particles, color shifts to bright Neon.
  - **Error/Blocked**: Red pulsing aura.

---

## 4. Backend Synchronization & Data Flow

### A. The "Pulse" (WebSocket)
The 3D scene creates a living representation of backend logic via WebSocket.

**Flow**:
1.  **Backend Action**: Agent performs task (e.g., `AtomStrategicPlanner` creates a strategy).
2.  **Event Log**: `log_event("agent_action", ...)` is called in Python.
3.  **Broadcast**: `ConnectionManager` broadcasts JSON payload to all connected clients.
4.  **Frontend Receipt**: `agentStore.ts` receives message.
5.  **State Update**: 
    - Agent status set to `'active'`.
    - `currentTask` updated with message.
    - `lastActivity` timestamp updated.
6.  **3D Reaction**: 
    - `CommandRoom3D` detects state change.
    - Triggers `<ActivityBurst />` at agent's (x,y,z).
    - Draws `<DataStream />` (projectile) from Agent to Department Zone.

### B. Agent Roster Sync
- **Endpoint**: `/api/agents/roster`
- **Data**: Returns real list of agents from `backend/ai_corporation_agents.py`.
- **Mapping**: Frontend maps backend `department` strings to 3D `DEPARTMENT_ZONES` coordinates.

---

## 5. Implementation Instructions (Step-by-Step)

### Phase 1: Environment Setup
1.  Initialize `Canvas` with black background (`#050505`).
2.  Add `<Fog attach="fog" args={['#050505', 20, 90]} />` to blend floor into distance.
3.  Add `<Grid />` with `infiniteGrid`, `fadeDistance={60}`, `sectionColor="#333"`.
4.  **Verify**: Ensure NO stars or space assets are loaded.

### Phase 2: Agent Population
1.  Fetch agents from `useAgentStore`.
2.  Iterate through `DEPARTMENT_ZONES`.
3.  Filter agents by department.
4.  Calculate (x, z) positions in a ring/cluster arrangement within the zone.
5.  Instantiate Agent meshes at calculated coordinates.

### Phase 3: Live Connection
1.  In `CommandRoom3D`, use `useEffect` to subscribe to `useAgentStore` changes.
2.  Listen for `recentActivity` updates.
3.  On activity, spawn a temporary particle system (`ActivityBurst`) at the agent's location.

### Phase 4: The Artifact (Knowledge Vault)
1.  Place `ObsidianVault` at `[0, 16, 0]` (Floating above center) OR in dedicated `KnowledgeVaultPanel`.
2.  Ensure Shader uniforms (`uTime`, `uColor1`, `uColor2`) are updated frame-by-frame (`useFrame`).
3.  Bind `onClick` to React state for Modal visibility.

---

## 6. Troubleshooting

- **"I see stars"**: Check `CommandRoom3D.tsx`. Ensure `StarBackdrop` is commented out. Check `PostFX` for `Noise` component (disable it). Check `ParticleBackground` (should be null).
- **"Agents aren't moving"**: Verify WebSocket connection in Network tab (`ws://localhost:8000/ws`). Check `agentStore.ts` console logs.
- **"Vault looks flat"**: Ensure `Environment` is present (needed for glass refraction/reflection).
