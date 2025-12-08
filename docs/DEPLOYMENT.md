# AI Revenue Command Center Deployment Guide

This guide covers preparing a production deployment of the AI Revenue Command Center platform stack.

## 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended runtime)
- Stripe account (secret + publishable key + webhook secret)
- SMTP provider credentials (e.g., Gmail app password, SendGrid API key)
- Local LLM host (Ollama) or hosted LLM credentials

## 2. Configure Secrets

1. Copy `.env.example` to `.env`.
2. Populate at minimum:
   - `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`
   - `LLM_PROVIDER` (default `ollama`) and `OLLAMA_MODEL`
3. Optional integrations: Twitter, Shopify, affiliate networks, Google Analytics, etc.
4. Run the helper:
   ```bash
   python scripts/validate_secrets.py
   ```
   The command exits with code `1` if any critical secret is missing.

## 3. Local Verification

```bash
pip install -r requirements.txt
python backend/main_server.py
```

- API docs: <http://localhost:8080/docs>
- Worker status: `GET /autonomy/worker/status`
- Email campaign API: `POST /email/campaigns`, `GET /email/campaigns/clones`

## 4. Containerised Deployment

```bash
docker-compose up --build -d
```

- Logs stream in JSON via `docker-compose logs -f`
- Built-in health check queries `/api/health`

## 5. Background Workers & Scheduler

- `AUTONOMY_SCHEDULER_ENABLED` toggles directive orchestration
- `AUTONOMY_WORKER_ENABLED` controls queue execution
- Runtime endpoints:
  - `POST /autonomy/worker/start`
  - `POST /autonomy/worker/stop`
  - `POST /autonomy/worker/process_once`
  - `GET /autonomy/worker/status`

## 6. Monitoring & Logging

- Structured JSON logs emit to stdout/stderr (configure with `LOG_LEVEL`)
- Key endpoints:
  - `GET /metrics` – unified snapshot (worker, scheduler, queue, clones, alerts)
  - `GET /autonomy/alerts`
  - `GET /email/campaigns/clones`
- In Docker, `./logs` is mounted for archival or log shipping

## 7. Backup & Persistence

- SQLite DB lives in `./data`; bind mount to durable storage when containerised
- Schedule periodic exports (e.g., `sqlite3 business_database.db .dump > backup.sql`)

## 8. Upgrades & Customisation

- Swap the LLM provider by updating `LLM_PROVIDER` and related keys
- Extend the email division by adding new handlers in `autonomous/automation_worker.py`
- Enable Shopify or affiliate automations by providing credentials and un-commenting worker handlers

## 9. Smoke Test

After deployment, run the automated readiness checks:
```bash
python scripts/run_smoke.py --base-url http://localhost:8080
```
Use `--enqueue-demo` to queue a sample email campaign and confirm Beacon/Quill are operational.

## Branding

The stack loads defaults from `config/branding.json`. Update the file or call `PUT /api/branding` after launch to tailor names, colors, dashboard messaging, and logos for each deployment.

## 10. Production Hardening

### 10.1 Reverse proxy & TLS

- Use `deployment/nginx.conf.example` as the starting point for your Nginx host. Update `server_name`, certificate paths, and static directory (`/opt/fallat_crewai/static/`).
- Terminate TLS with Let's Encrypt (`certbot --nginx -d your-domain.com`), then reload Nginx.
- Keep `proxy_set_header` directives intact so FastAPI sees the original client IP and protocol.

### 10.2 Systemd service

- Copy `deployment/fallat_crewai.service` to `/etc/systemd/system/`.
- Adjust `WorkingDirectory`, `EnvironmentFile`, and `ExecStart` to match your install path.
- Reload and enable:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable --now fallat_crewai.service
  sudo systemctl status fallat_crewai.service
  ```

### 10.3 Datastore initialization

- Run `python scripts/init_datastores.py` after configuring `.env` to create/upgrade all SQLite databases (business, audit, vector memory). Append `--include-vault` to verify the credential vault key is valid.

### 10.4 Credential vault operations

- Generate a new vault key with `python scripts/vault_tool.py generate-key`.
- Check vault status or list stored secrets without decrypting them:
  ```bash
  python scripts/vault_tool.py status
  python scripts/vault_tool.py list --service stripe
  ```

### 10.5 Health & monitoring

- The `/health` endpoint now reports database, vector memory, credential vault, and Stripe status. Point your uptime monitor at `https://your-domain.com/health`.
- Stripe webhooks are served at `/api/stripe/webhook`. Remember to update the endpoint URL inside the Stripe dashboard and copy the `whsec_…` signing secret into `.env`.
