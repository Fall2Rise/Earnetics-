# Earnetics Command Center V3

An offline-first, event-sourced, 3D navigable operations environment.

## Tech Stack
- **Electron**: Desktop shell
- **Vite + React**: UI Framework
- **TypeScript**: Language
- **React Three Fiber**: 3D Scene
- **Better SQLite3**: Local Database
- **Zustand**: State Management

## Project Structure
- `packages/core`: Shared logic, Event Bus, DB, Types.
- `packages/ui`: Shared UI components (2D).
- `packages/scene`: 3D Scene components.
- `packages/main`: Electron Main process.
- `packages/renderer`: Electron Renderer process (The App).

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Build Core**:
   ```bash
   npm run build --workspace=packages/core
   ```

3. **Start Development**:
   ```bash
   npm run dev
   ```
   (This starts the Vite server)

4. **Start Electron**:
   ```bash
   npm start
   ```

## Demo Flow
1. Launch the app.
2. Observe the **3D Ops Room** with the HoloTable and Department Orbs.
3. Switch to **2D Department Bay** using the top toggle.
4. Watch the **Live Feed** (bottom rail) update with simulated events.
5. Events are persisted to `earnetics-v3.db` in your user data folder.

## Architecture
- **Event Sourcing**: All state changes are recorded as events in SQLite.
- **Offline-First**: No external dependencies required for core operation.
- **Simulator**: A built-in simulator emits events to demonstrate the system.

## Troubleshooting
### Native Module Build Errors
If you encounter errors building `better-sqlite3` (e.g., `MSB8020: The build tools for ClangCL cannot be found`), you may need to install the **C++ Clang Compiler for Windows** component in Visual Studio Build Tools, or use a Node.js version that has prebuilt binaries available for `better-sqlite3`.

To bypass build scripts during installation (for development/inspection only):
```bash
npm install --ignore-scripts
```
Note: The app will not run correctly without the native modules built.
