# 🏢 AI REVENUE COMMAND CENTER

**17+ Autonomous Agents Running End-to-End Business Operations**

A production-grade AI corporation featuring specialized agents across finance, marketing, product, operations, compliance, infrastructure, innovation, affiliate growth, and the newly expanded email marketing division. The stack is tuned for real-world revenue—structured logging, automation workers, and live integrations (Stripe, SMTP, LLM) included.

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
git clone https://github.com/your-username/fallat-crewai.git
cd fallat-crewai
```

### 2. Configure Environment
```bash
cp .env.example .env
# fill in FALLAT_API_TOKEN, Stripe, SMTP, LLM, and any optional integrations
```

Generate a credential-vault key (if you plan to store API keys locally):

```bash
python -c "from backend.credential_vault import CredentialVault; print(CredentialVault.generate_key())"
```
Copy the printed value into `CREDENTIAL_VAULT_KEY` inside `.env`.

### 3. Install Dependencies & Validate Secrets
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/validate_secrets.py
```

### 4. Run Locally (single entrypoint)
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\run_all.ps1
```

- Command Center Dashboard: <http://localhost:5173>
- Backend API: <http://127.0.0.1:8000>
- API Docs / OpenAPI: <http://127.0.0.1:8000/docs>

## 🐳 Docker Deployment
```bash
docker-compose up --build -d
```
- Logs stream in JSON via `docker-compose logs -f`
- Health check monitors `/api/health`
- Data and logs persist in `./data` and `./logs`

## 🔧 Operations Control

| Endpoint | Description |
| --- | --- |
| `GET /autonomy/worker/status` | View worker state, queue depth, intervals |
| `POST /autonomy/worker/start` / `stop` | Toggle queue execution |
| `POST /autonomy/worker/process_once` | Drain a single worker cycle |
| `POST /email/campaigns` | Queue Beacon/Quill tasks for a campaign |
| `GET /email/campaigns/clones` | Inspect cloned specialists per campaign |
| `GET /autonomy/alerts` | Monitor queue and SLA alerts |

Email marketing agents (Beacon & Quill) spin up fresh clones for every campaign. Finance handlers talk directly to Stripe; SMTP tasks send real emails when credentials are present.

## 📦 Package Contents

- `backend/` – FastAPI app, corporate memory, agent hierarchy, automation worker, logging config
- `autonomous/` – Orchestrator, queue manager, worker scheduler
- `docs/DEPLOYMENT.md` – Production rollout instructions
- `scripts/validate_secrets.py` – Secret completeness check
- `Dockerfile` + `docker-compose.yml` – Containerized deployment
- `tests/` – Pytest coverage for schedulers and worker flows

## 🧪 Testing
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --override-ini asyncio_mode= --override-ini addopts="" tests
```

## 🛠️ Utility Scripts

- `python scripts/init_datastores.py` — create/upgrade the business, audit, and vector-memory databases (`--include-vault` also verifies the credential vault key).
- `python scripts/vault_tool.py generate-key` — mint a new vault key (other subcommands: `status`, `list --service=foo`).
- `python scripts/validate_secrets.py` — confirm critical env vars are present.

## 🔍 Smoke Test
```bash
python scripts/validate_secrets.py
python scripts/run_smoke.py --base-url http://localhost:8000
```
Add `--enqueue-demo` to queue a sample email campaign and verify Beacon/Quill task generation.

## 📝 Logging & Monitoring

- Structured JSON logs via `structlog` for all services
- `LOG_LEVEL` env var controls verbosity (default `INFO`)
- `./logs` directory mounts for archival or log shipper integration

## 🗝️ Secrets Overview

Critical:
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- SMTP: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`
- LLM: `LLM_PROVIDER` (default `ollama`), `OLLAMA_MODEL`

Optional integrations include Twitter, Shopify, affiliate networks, Google Analytics, etc. Populate as needed—handlers degrade gracefully when a key is absent.
Additional `.env` placeholders are provided for every major channel so your customers can opt in to the ones they use:

- **Social**: `YOUTUBE_API_KEY`, `TIKTOK_CLIENT_KEY`, `FACEBOOK_APP_ID`, `INSTAGRAM_APP_ID`, `LINKEDIN_CLIENT_ID`, `PINTEREST_ACCESS_TOKEN`, `REDDIT_CLIENT_ID`, etc.
- **Email & Messaging**: `MAILCHIMP_API_KEY`, `CONVERTKIT_API_KEY`, `SENDGRID_API_KEY`, `TWILIO_ACCOUNT_SID`, `SLACK_BOT_TOKEN`, `DISCORD_WEBHOOK_URL`, and more.
- **Commerce & Fulfillment**: `PAYPAL_CLIENT_ID`, `ETSY_API_KEY`, `GUMROAD_API_TOKEN`, `PRINTFUL_API_KEY`, `PRINTIFY_API_TOKEN`.
- **Affiliate & Ads**: `CLICKBANK_API_KEY`, `DIGISTORE_API_KEY`, `CJ_DEVELOPER_KEY`, `GOOGLE_ANALYTICS_PROPERTY_ID`, `META_ADS_API_TOKEN`, etc.
- **Real Estate & Finance**: `ZILLOW_API_KEY`, `PROPSTREAM_API_KEY`, `BINANCE_API_KEY`, `BINANCE_API_SECRET`.
- **Knowledge & Workflow**: `NOTION_API_KEY`, `AIRTABLE_API_KEY`.
- **Governance / Alignment**: `PRIME_DIRECTIVE_PATH` (optional custom location), `PRIME_DIRECTIVE_SECRET` (HMAC key), `PRIME_DIRECTIVE_MAC` (golden HMAC for validation).

Leave unused entries blank—Fallat CrewAI will automatically disable connectors that don’t have credentials.

## 📚 Additional Resources
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) – Environment prep, Docker tips, monitoring checklist
- `/docs` – FastAPI interactive API Explorer

## ✅ Production Checklist
- [ ] Secrets configured (`scripts/validate_secrets.py`)
- [ ] Automation worker running (`/autonomy/worker/status`)
- [ ] Stripe webhook pointed to `/stripe/webhook`
- [ ] Email deliverability verified (SPF/DKIM)
- [ ] Data backup policy for `./data` and log retention plan

Run it, iterate, and ship campaigns directly from the AI corporation.

## 🛠️ Troubleshooting
- **Missing secrets** – run `python scripts/validate_secrets.py`; the script reports any critical keys that are absent.
- **Automation worker idle** – check `/autonomy/worker/status`; use `/autonomy/worker/start` to resume or `/metrics` to inspect queue depth.
- **Email campaigns stay pending** – confirm SMTP credentials and that Beacon/Quill clones appear under `/email/campaigns/clones`.
- **Stripe callbacks** – ensure your dashboard points the webhook to `/stripe/webhook` and the secret matches `STRIPE_WEBHOOK_SECRET`.
- **Logs** – JSON logs stream to stdout and `./logs` (Docker). Set `LOG_LEVEL=DEBUG` for deeper inspection.

## Customize Your Brand

- Update `config/branding.json` to change the default name, tagline, colors, and optional dashboard snippets.
- Use `PUT /api/branding` to apply changes at runtime.
- Upload a new logo with `POST /api/branding/logo` (PNG/JPG/SVG/GIF/WEBP).
- Supply rich HTML sections with the `custom_dashboard_html` field and page-wide overrides with `custom_css`.
- Reset to defaults anytime with `POST /api/branding/reset`.
- Custom CSS snippets are injected automatically across the dashboard, command center, and storefront.


## Security & Packaging
- API token support via `FALLAT_API_TOKEN` for dashboard/API access.
- Docker deployment: `deployment/docker-compose.yml` and `deployment/Dockerfile.backend`.
- Setup script: `deployment/bootstrap.sh` to create venv, install deps, build UI.
