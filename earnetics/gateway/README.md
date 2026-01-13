# Earnetics Internet Gateway

Controlled Internet Gateway layer for Earnetics - enables hybrid (local-core + online adapters) operations safely. Agents **NEVER** access the open internet directly. All network actions route through this gateway with RBAC, allowlists, throttles, audit logs, and a global kill switch.

## Architecture

**Offline-First Core + Governed Online Adapters**

- Planning, memory, orchestration: **Local** (offline)
- Research, scraping, posting, payments, outreach: **Through Gateway** (online, permissioned)

## Key Features

### Security Controls
- **RBAC**: Role-based access control (EXEC, INTELLIGENCE_RND, OPS, MARKETING, SCRAPER, FINANCE, SYSTEM)
- **Allowlists/Denylists**: Domain-level filtering for read and write operations
- **Rate Limiting**: Global, per-domain, and per-agent limits (strict mode for SCRAPER role)
- **Kill Switch**: Instant disable of all write operations
- **Approval Tokens**: Required for write actions from non-EXEC roles
- **Audit Logging**: Append-only log of all gateway actions (secrets redacted)

### Adapters
- **HTTP Reader**: Read-only HTTP requests (web.fetch, web.head)
- **Search Adapter**: Web search using internal knowledge router (offline-first)
- **Playwright Reader**: Browser-based rendering (optional, Phase 2)
- **Email Sender**: Email delivery (Phase 2)
- **Social Poster**: Social media posting (Phase 2)
- **Stripe Adapter**: Payment processing (Phase 2)

### Queue & Retry
- Automatic retry for transient errors (429, 503, timeouts)
- Exponential backoff
- Dead-letter queue after max retries

## Configuration

### `config/internet_gateway.json`
- Gateway mode, timeouts, kill switch state
- Rate limits (global, domain, agent)
- Queue settings (retries, backoff)
- Adapter enable/disable flags

### `config/allowlists.json`
- Read allowlist (wikipedia, arxiv, github, etc.)
- Write allowlist (stripe, reddit, twitter, email providers)
- Denylist (pastebin, anonfiles, etc.)
- Wildcard rules for subdomains

### `config/permissions.json`
- Role definitions with read/write permissions
- Action definitions (type, risk_level, requires_approval)
- Approval token requirements per role

## Usage

### Agent Tools API

Agents call these functions instead of direct network requests:

```python
from earnetics.tools.web_tools import web_fetch, web_search, social_post, email_send

# READ OPERATIONS (no approval needed for allowed roles)
result = web_fetch("https://en.wikipedia.org/wiki/AI", 
                  agent_id="agent1", role="INTELLIGENCE_RND")

result = web_search("revenue strategies", 
                   recency_days=7,
                   agent_id="agent1", role="INTELLIGENCE_RND")

# WRITE OPERATIONS (require approval token)
token = generate_approval_token("social.post", created_by="EXEC")
result = social_post("twitter", "Content here", 
                    approval_token=token,
                    agent_id="agent1", role="MARKETING")
```

### Kill Switch Control

```bash
# Disable all writes (activate kill switch)
python earnetics/scripts/gateway_kill_switch_off.py

# Enable writes
python earnetics/scripts/gateway_kill_switch_on.py
```

### Approval Tokens

```python
from earnetics.gateway.security.approval_tokens import ApprovalTokenManager

manager = ApprovalTokenManager()

# Generate token (EXEC role only)
token_result = manager.generate_token(
    action="social.post",
    created_by="EXEC",
    campaign_id="campaign_123",
    expires_hours=24
)

token = token_result["token"]
```

## Security Flow

1. **Permission Check**: Agent role has permission for action?
2. **Kill Switch Check**: Write operations enabled?
3. **Approval Token Check**: Write action has valid approval token?
4. **Domain Rules**: URL in allowlist? Not in denylist?
5. **Rate Limit**: Within global/domain/agent limits?
6. **Execute**: Route to appropriate adapter
7. **Audit Log**: Record action (secrets redacted)
8. **Retry Queue**: If transient error, enqueue for retry

## Audit Log

All actions are logged with:
- Agent ID, role, action
- Target URL (sanitized)
- Status (allowed/blocked/failed/success)
- Policy reason (if blocked)
- Latency, response code, bytes
- **Secrets are automatically redacted**

Query audit log:
```python
from earnetics.gateway.security.audit_logger import AuditLogger

logger = AuditLogger()
entries = logger.get_audit_log(agent_id="agent1", limit=50)
stats = logger.get_stats(hours=24)
```

## Testing

Run demo script:
```bash
python earnetics/scripts/demo_gateway.py
```

This verifies:
- ✅ Allowed web.fetch to Wikipedia → success
- ✅ Blocked web.fetch to non-allowlisted domain → blocked
- ✅ Blocked social.post without approval token → blocked
- ✅ Enabled writes + approval token → success
- ✅ Rate limiting triggers correctly
- ✅ Audit logging works

## Non-Negotiables Enforced

- ✅ Agents cannot call requests/playwright/selenium directly
- ✅ Read vs Write actions separated with permissions
- ✅ Credentials never appear in logs (vault abstraction + sanitizer)
- ✅ All actions auditable (who/what/where/when/result)
- ✅ Global kill switch disables all writes instantly

## Phase 2 (Future)

- Playwright render_fetch for JS-heavy pages
- Email sender adapter (Mailgun/SendGrid)
- Social poster adapters (Reddit, Twitter/X)
- Stripe adapter for payment operations
- Download adapter with quarantine

## Status

**MVP Complete**: Read operations (web.fetch, web.search) fully functional with all security controls.

**Phase 2**: Write adapters can be added incrementally without changing agent logic.
