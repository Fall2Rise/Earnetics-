# 3D Rendering Stack Analysis - Earnetics/Fallat CrewAI

## CONFIRMED 3D STACK

**✅ React Three Fiber (R3F) with Three.js**
- **Primary Library**: `@react-three/fiber` v8.17.10
- **Helpers**: `@react-three/drei` v9.114.3
- **Base**: `three` v0.181.0
- **Additional**: `@react-three/xr` v6.6.27 (for VR/AR support)

**Architecture**: React Three Fiber (declarative React wrapper over Three.js)
- Uses React hooks (`useFrame`, `useThree`) for 3D rendering
- Direct Three.js imports (`import * as THREE from 'three'`) for geometry/materials
- Hybrid approach: R3F for scene graph, Three.js for low-level operations

---

## FRONTEND FRAMEWORK

**✅ Vite + React + TypeScript**
- **Build Tool**: Vite 7.1.5
- **Framework**: React 18.3.1
- **Language**: TypeScript 5.5.3
- **State Management**: Zustand 5.0.8
- **Styling**: Tailwind CSS 3.4.1 + Custom CSS

---

## KEY FILES - SCENE ARCHITECTURE

### 🎬 Scene Root (Main Entry Point)
**File**: `fallat_crewai_dashboard/src/components/dashboard/Office3DView.tsx`
- **Purpose**: Top-level wrapper that conditionally renders main scene or department room
- **Key Features**:
  - Manages `selectedDepartment` state
  - Renders `<CommandRoom3D />` (main nexus) or `<DepartmentRoom />` (department view)
  - Handles WebSocket connection via `useAgentStore()`
  - Fetches system status via API
  - Contains overlay UI (status pill, revenue metrics)

### 🏛️ Main 3D Scene (Command Nexus)
**File**: `fallat_crewai_dashboard/src/components/3d/CommandRoom3D.tsx`
- **Purpose**: Renders the main "Command Nexus" 3D scene
- **Key Components**:
  - `<Canvas>` wrapper (R3F entry point)
  - `<DivisionalZone>` - Department clusters (13 departments)
  - `<AgentNode>` - Individual agent representations
  - `<ConnectionLines>` - Visual connections between agents/departments
  - `<ParticleBackground>` - Starfield/grid background
  - `<HolographicPanel>` - UI overlays in 3D space
  - `<DataStream>` - Animated data flows
  - `<ActivityBurst>` - Activity indicators
  - `<WorkflowTrail>` - Workflow visualization
  - `<FloatingMetric>` - Floating metrics display
- **Camera**: `<PerspectiveCamera>` from drei (position: [0, 30, 50], fov: 50)
- **Controls**: `<OrbitControls>` from drei

### 🎯 Agent Node Renderer
**File**: `fallat_crewai_dashboard/src/components/3d/AgentNode.tsx`
- **Purpose**: Renders individual agent as 3D node
- **Features**:
  - Animated mesh (rotation, pulsing, glow effects)
  - Status-based visual states (active/idle/error/offline)
  - Click handlers for selection
  - HTML overlays via `drei/Html` for labels
  - Uses `useFrame` hook for animations
  - Direct Three.js geometry (`THREE.Mesh`, `THREE.BufferGeometry`)

### 🏢 Department Cluster Renderer
**File**: `fallat_crewai_dashboard/src/components/3d/DivisionalZone.tsx`
- **Purpose**: Renders department zones/clusters
- **Features**:
  - Themed 3D shapes per department
  - Contains multiple `<AgentNode>` components
  - Click handlers for department selection
  - Visual effects (glow, edges, animations)
  - HTML labels via `drei/Html`

### 🔗 Connection Lines
**File**: `fallat_crewai_dashboard/src/components/3d/ConnectionLines.tsx`
- **Purpose**: Renders lines connecting agents and departments
- **Features**:
  - Connects agents within same department
  - Connects Executive Board to all departments
  - Active connections (bright) vs idle connections (dim)
  - Uses `THREE.LineSegments` with animated opacity

### 🚪 Department Room (Alternative Scene)
**File**: `fallat_crewai_dashboard/src/components/3d/DepartmentRoom.tsx`
- **Purpose**: Renders individual department "room" when department is selected
- **Features**:
  - Camera transition animation
  - Door opening animation
  - Room environment (walls, floor, ceiling)
  - Agents positioned within room
  - Exit mechanism

---

## TELEMETRY INGRESS

### 📡 State Management Store
**File**: `fallat_crewai_dashboard/src/stores/agentStore.ts`
- **Library**: Zustand
- **Exports**: `useAgentStore()` hook
- **Data Flow**:
  1. **Initial Load**: `fetchAgents()` - HTTP GET to `/api/agents/status`
  2. **Real-time Updates**: WebSocket connection to `/ws`
  3. **State Updates**: `setAgents()`, `updateAgentStatus()`, `updateAgentPosition()`
- **WebSocket Connection**:
  - Managed by `connectWebSocket()` / `disconnectWebSocket()`
  - Connects to `ws://127.0.0.1:8000/ws` (or env-configured URL)
  - Listens for events: `agent_thinking`, `agent_action`, `agent_status_update`
  - Updates agent state in real-time

### 🔌 WebSocket Integration Points
1. **Office3DView.tsx** (line 38, 68, 80)
   - Calls `connectWebSocket()` on mount
   - Calls `disconnectWebSocket()` on unmount

2. **CommandRoom3D.tsx** (lines 144-175)
   - Listens to WebSocket for activity events
   - Creates `<ActivityBurst>` components on activity
   - Updates workflow trails

3. **RealTimeLogViewer.tsx**
   - Listens to WebSocket for log events

4. **AssistantConsole.tsx**
   - Listens to WebSocket for ATOM responses

### 📊 API Integration
**File**: `fallat_crewai_dashboard/src/api/systemStatusApi.ts`
- Fetches system status via HTTP
- Used by `Office3DView.tsx` for status display

**File**: `fallat_crewai_dashboard/src/api/agentApi.ts`
- Fetches agent status via HTTP
- Used by `agentStore.ts` for initial load

---

## STYLES

### Main Stylesheet
**File**: `fallat_crewai_dashboard/src/styles/index.css`
- Tailwind CSS directives
- Custom CSS variables for theming
- Component-specific styles
- 3D-related styles (glass panels, gradients, etc.)

### Inline Styles
- 3D components use inline styles via React props
- Material properties set via Three.js material objects
- Colors defined in component constants (DEPARTMENT_ZONES)

---

## FILE STRUCTURE MAP

```
fallat_crewai_dashboard/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   └── Office3DView.tsx          ← SCENE ROOT (entry point)
│   │   └── 3d/
│   │       ├── CommandRoom3D.tsx          ← MAIN SCENE (Command Nexus)
│   │       ├── AgentNode.tsx             ← AGENT RENDERER
│   │       ├── DivisionalZone.tsx        ← DEPARTMENT CLUSTER
│   │       ├── ConnectionLines.tsx       ← CONNECTION VISUALIZATION
│   │       ├── DepartmentRoom.tsx        ← DEPARTMENT ROOM SCENE
│   │       ├── ParticleBackground.tsx     ← BACKGROUND
│   │       ├── HolographicPanel.tsx      ← UI OVERLAYS
│   │       ├── DataStream.tsx            ← DATA FLOWS
│   │       ├── ActivityBurst.tsx         ← ACTIVITY INDICATORS
│   │       ├── WorkflowTrail.tsx         ← WORKFLOW VISUALIZATION
│   │       └── FloatingMetrics.tsx      ← FLOATING METRICS
│   ├── stores/
│   │   └── agentStore.ts                 ← TELEMETRY STORE (Zustand)
│   ├── api/
│   │   ├── systemStatusApi.ts            ← API CLIENT
│   │   └── agentApi.ts                   ← API CLIENT
│   └── styles/
│       └── index.css                     ← STYLES
├── package.json                          ← DEPENDENCIES
└── vite.config.ts                        ← BUILD CONFIG
```

---

## SUMMARY

| Category | Technology/File |
|----------|----------------|
| **Frontend Framework** | Vite + React 18 + TypeScript |
| **3D Stack** | React Three Fiber v8 + Three.js v0.181 + drei v9 |
| **Scene Root** | `src/components/dashboard/Office3DView.tsx` |
| **Main Scene** | `src/components/3d/CommandRoom3D.tsx` |
| **Node Renderer** | `src/components/3d/AgentNode.tsx` |
| **Department Clusters** | `src/components/3d/DivisionalZone.tsx` |
| **Telemetry Store** | `src/stores/agentStore.ts` (Zustand) |
| **WebSocket Endpoint** | `ws://127.0.0.1:8000/ws` |
| **HTTP API** | `http://127.0.0.1:8000/api/agents/status` |
| **Styles** | `src/styles/index.css` (Tailwind + Custom) |

---

## NOTES

- **Hybrid Rendering**: Uses R3F for React integration but directly manipulates Three.js objects for performance-critical operations
- **Real-time Updates**: WebSocket provides live telemetry; HTTP used for initial state
- **Scene Switching**: `Office3DView` conditionally renders `CommandRoom3D` (main) or `DepartmentRoom` (detail) based on selection
- **XR Support**: `@react-three/xr` included but usage not confirmed in current implementation
- **Performance**: Vite config includes Three.js deduplication to prevent multiple instances
