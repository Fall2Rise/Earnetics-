# Earnetics CRM Module

Offline-first CRM that lives inside the Earnetics Command Center. Manages contacts, deals, pipelines, interactions, and tasks, with AI hook stubs for summaries and next actions.

## Backend
- Stack: FastAPI + SQLAlchemy + SQLite (default: `data/earnetics_crm.db`)
- Run locally:
  ```bash
  uvicorn earnetics_crm.main:app --host 0.0.0.0 --port 8001
  ```
- API prefixes are under `/crm/*`.

### Endpoints
- Contacts: `POST/GET/PUT/DELETE /crm/contacts`, plus `/crm/contacts/{id}/deals|interactions|tasks`
- Deals: `POST/GET/PUT/DELETE /crm/deals`, `POST /crm/deals/{id}/move_stage`
- Interactions: `POST/GET/DELETE /crm/interactions`
- Tasks: `POST/GET/PUT/DELETE /crm/tasks`
- Pipelines: `GET /crm/pipelines`, `GET /crm/pipelines/{name}`
- Insights: `GET /crm/insights/deals/prioritized`
- Health: `GET /crm/health`

### Data model (SQLite tables)
- `crm_contacts`: contacts with type/source/tags/notes
- `crm_deals`: tied to contacts, pipeline/stage/value/priority
- `crm_interactions`: call/sms/email/etc. with contact/deal links
- `crm_tasks`: follow-ups/reminders with status/owner/due_at
- `crm_pipelines`: pipeline name + stages (default seeded for real_estate, automation_clients)

### AI hooks
- `services/ai_insights.py` provides stubs:
  - `generate_contact_summary(contact, interactions)`
  - `suggest_next_actions_for_deal(deal, contact, interactions)`
  - `draft_followup_message(contact, deal, tone)`
Use these from agents or expose custom endpoints as needed.

### DB config
- Path: `data/earnetics_crm.db` (created if missing). Set `EARNETICS_CRM_DATA_DIR` or `EARNETICS_CRM_DB_FILE` to override.

### Integrating into the Command Center
- Mount the FastAPI app or include its routers into the main server (prefix already `/crm`).
- For UI, call the endpoints from your command center front-end. Suggested panels: Contacts table, Deals board, Tasks list, Interactions timeline, Insights.

## Frontend (reference structure)
If you build a React module, a suggested layout:
- `CrmLayout` with tabs: Pipeline Board, Contacts, Tasks, Insights
- `DealsBoard` (kanban by pipeline stage, drag-drop updates stage via API)
- `ContactsTable` (search/filter, opens `ContactDetailDrawer`)
- `ContactDetailDrawer` shows contact info, interactions, tasks; actions to add interaction/task/deal
- `TasksPanel` (filters by status/owner/due)
- `InteractionsTimeline` (chronological interactions)
- `InsightsPanel` (suggested next moves from AI hooks)

API client sketch (TypeScript):
```ts
import axios from 'axios';
const api = axios.create({ baseURL: '/crm' });
export const getContacts = () => api.get('/contacts');
export const createContact = (data) => api.post('/contacts', data);
export const getDeals = (params) => api.get('/deals', { params });
export const updateDealStage = (id, stage) => api.post(`/deals/${id}/move_stage`, { stage });
// ...tasks, interactions, pipelines, insights...
```

## Backup/restore
- Backup: copy `data/earnetics_crm.db`
- Restore: replace the file (stop server first)

## Extend
- Add more pipelines/stages via `crm_pipelines`
- Add AI endpoints that call `ai_insights.py`
- Add webhooks/integrations as needed
