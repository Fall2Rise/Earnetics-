# Earnetics Command Cockpit UI

Futuristic cockpit-style control panel for the Earnetics Command Center. Built with React + TypeScript, TailwindCSS, and Framer Motion. Designed to plug into the existing backend (`http://localhost:8000`) and remain offline-first.

## Getting Started

```bash
cd earnets-command-cockpit
npm install
npm run dev   # or npm run build && npm run start
```

Default API targets are `http://localhost:8000`. Adjust in `src/api/*Client.ts` if needed.

## Layout

- `CommandCenterLayout` (main shell)
  - `TopHudBar` (logo/title, mode, time, high-level KPIs)
  - `NavRail` (Dashboard, Streams, CRM, Agents, Library, Settings)
  - `StatusDock` (notifications, system health)
  - Main panes: Dashboard overview, Revenue Streams panel, CRM panel, Agent Ops Deck, Internal Library.

## Key Panels

- **Dashboard Overview:** KPI tiles + snapshots for streams/agents + “Today’s Mission” summary.
- **Revenue Streams Panel:** Cockpit cards with status, KPIs, progress, and actions (view/advance/maintenance). Calls `streamsClient`.
- **CRM Panel:** Contacts table + detail side pane. Calls `/crm/*` endpoints from the Earnetics CRM backend.
- **Agent Ops Deck:** 2D ops floor (fallback) and optional 3D scene. Agent list/detail with task feed. Calls `agentsClient`.
- **Internal Library:** Placeholder list for knowledge items; extend to hit your library endpoint.
- **Notifications/Status Dock:** Recent events, system/API health.

## API Clients

- `streamsClient.ts`: GET `/streams`, POST `/streams/{id}/advance`, etc.
- `agentsClient.ts`: GET `/api/agents/roster`, `/api/agents/activity`, etc.
- `crmClient.ts`: GET/POST `/crm/contacts`, `/crm/deals`, `/crm/tasks`, etc.

## Extending

- Add new modules under `src/components` and wire them into `CommandCenterLayout` tabs.
- Replace mock data with live endpoints in the client files.
- Style tweaks in `tailwind.config.js` and component classes (glassmorphism + neon HUD accents).

## Earnetics Agent Roster & Visual System
- Catalog lives in `src/agentScene/agentCatalog.ts` with canonical agents (Stream Architect, Funnel Engineer, Lead Hunter, Recon Analyst, CRM Sentinel, Deal Closer, Library Curator, Systems Orchestrator).
- Department colors and status visuals are in `src/agentScene/agentStyles.ts`.
- The Ops Deck merges backend agents with these presets (by id/role). Add or edit agents in `agentCatalog.ts` to change roles/visuals.

## Notes

- 3D scene (`AgentScene3D`) is optional; `AgentScene2D` is the default fallback.
- Animations use Framer Motion (hover lifts, panel fades, status pulses). Keep them subtle for readability.
