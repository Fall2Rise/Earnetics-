# Earnetics Intelligence System

A comprehensive intelligence, knowledge management, and revenue loop system for autonomous AI operations.

## Overview

The Earnetics Intelligence System provides:

- **Knowledge Core**: Unified knowledge store with citation tracking and multi-tier source routing
- **Truth Library**: Validated playbooks, SOPs, strategies, and experiments
- **Lead Vault**: PII-compliant lead storage with RBAC and audit logging
- **Intelligence Department**: Opportunity triage, synthesis, and decision packet generation
- **Revenue Loop Engine**: Deployment orchestration, KPI telemetry, and feedback loops
- **Knowledge Radio**: Continuous brief-card stream for passive learning
- **Internet Gateway**: Controlled network access with RBAC, allowlists, and audit logging

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite3
- Virtual environment (recommended)

### Installation

1. **Navigate to project root:**
   ```bash
   cd C:\AI_Projects\Fallat_CrewAI
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize databases:**
   The system will automatically create SQLite databases on first use.

### Configuration

1. **Set environment variables** (`.env` file):
   ```env
   FALLAT_API_TOKEN=your_token_here
   STRIPE_SECRET_KEY=sk_test_... (optional)
   MAILGUN_API_KEY=... (optional, for email adapter)
   SENDGRID_API_KEY=... (optional, for email adapter)
   REDDIT_CLIENT_ID=... (optional, for social adapter)
   TWITTER_API_KEY=... (optional, for social adapter)
   ```

2. **Configure Internet Gateway** (`earnetics/config/internet_gateway.json`):
   - Set `kill_switch.writes_enabled` to `true` to enable write operations
   - Configure rate limits per your needs
   - Enable/disable adapters as needed

3. **Configure Knowledge Sources** (`earnetics/config/knowledge_sources.json`):
   - Enable/disable knowledge source connectors
   - Adjust trust scores and rate limits

## Usage

### Knowledge Core

```python
from earnetics.tools.knowledge_tools import KnowledgeTools

tools = KnowledgeTools()

# Search knowledge
results = tools.search("revenue generation strategies", tiers=[0, 1, 2])

# Fetch specific record
record = tools.fetch("record_id_here")

# Remember (store in Tier 0)
tools.remember(record)
```

### Intelligence Department

```python
from earnetics.intelligence.scoring import OpportunityScorer
from earnetics.intelligence.triage import TriageWorkflow
from earnetics.revenue_loop.opportunity import Opportunity

# Score opportunity
scorer = OpportunityScorer()
score = scorer.score(opportunity)

# Triage opportunity
triage = TriageWorkflow()
result = triage.triage(opportunity)
```

### Internet Gateway

```python
from earnetics.tools.web_tools import web_fetch, email_send, social_post

# Read operation (no approval needed)
result = web_fetch("https://example.com", agent_id="agent1", role="INTELLIGENCE_RND")

# Write operation (requires approval token)
result = email_send(
    provider="mailgun",
    to_list_ref="customer@example.com",
    subject="Welcome",
    body="Welcome to Earnetics!",
    approval_token="token_from_exec",
    agent_id="agent1",
    role="MARKETING"
)
```

### Revenue Loop

```python
from earnetics.revenue_loop.deployment_orchestrator import DeploymentOrchestrator
from earnetics.revenue_loop.telemetry import KPITelemetry

# Generate deployment plan
orchestrator = DeploymentOrchestrator()
plan = orchestrator.generate_deployment_plan(opportunity, decision_packet)

# Execute deployment
result = orchestrator.execute_deployment(plan)

# Log telemetry
telemetry = KPITelemetry()
telemetry.log_event("conversion.purchase", campaign_id="camp_123", value=99.99)
```

## Demo Scripts

### Intelligence Pipeline Demo

```bash
python earnetics/scripts/demo_intel_pipeline.py
```

This demonstrates:
- Knowledge ingestion
- Opportunity creation and triage
- Decision packet generation
- Deployment orchestration
- KPI telemetry

### Internet Gateway Demo

```bash
python earnetics/scripts/demo_gateway.py
```

This demonstrates:
- Allowed/blocked read operations
- Kill switch functionality
- Approval token system
- Write operations with proper authorization

## Architecture

### Directory Structure

```
earnetics/
├── config/              # Configuration files
├── knowledge_sources/   # Knowledge source connectors
├── knowledge_store/    # Knowledge storage and retrieval
├── knowledge_router/   # Intent-based routing
├── truth_library/      # Validated assets (playbooks, SOPs)
├── lead_vault/         # PII-compliant lead storage
├── intelligence/       # Intelligence workflows
├── revenue_loop/      # Revenue generation engine
├── gateway/           # Internet Gateway (security layer)
├── tools/             # Agent-facing APIs
└── services/          # Background services
```

### Data Flow

1. **Signal → Triage**: Opportunities are scored and routed
2. **Triage → Synthesis**: High-scoring opportunities become playbooks
3. **Synthesis → Decision Packet**: Executive-ready summaries
4. **Decision → Deployment**: Approved opportunities are deployed
5. **Deployment → Telemetry**: KPIs are tracked
6. **Telemetry → Feedback**: Results feed back into Truth Library

## Security

### Internet Gateway

- **RBAC**: Role-based access control for all network operations
- **Allowlists/Denylists**: Domain-based filtering
- **Rate Limiting**: Global, per-domain, and per-agent limits
- **Kill Switch**: Emergency disable for all write operations
- **Approval Tokens**: Required for sensitive write actions
- **Audit Logging**: Complete audit trail for all operations

### Lead Vault

- **RBAC**: Role-based access to PII
- **Audit Logs**: All access is logged
- **Suppression Lists**: Do-not-contact enforcement
- **Retention Policies**: Automatic expiry
- **Channel Permissions**: Per-channel access control

## API Endpoints

### Intelligence Department

- `GET /api/intelligence/signals` - Get ranked signals
- `GET /api/intelligence/truth-library` - Browse Truth Library
- `GET /api/intelligence/lead-vault` - Browse Lead Vault (gated)
- `GET /api/intelligence/executive-inbox` - Get Decision Packets
- `GET /api/intelligence/opportunity-backlog` - Get Kanban board
- `GET /api/intelligence/experiments` - List experiments

### Internet Gateway

All gateway operations are accessed through agent tools, not direct HTTP endpoints.

## Troubleshooting

### Import Errors

If you see import errors:
1. Ensure you're in the project root directory
2. Activate the virtual environment
3. Check that all dependencies are installed: `pip install -r requirements.txt`

### Database Errors

Databases are created automatically. If you see errors:
1. Check file permissions in the project directory
2. Ensure SQLite3 is available

### Gateway Errors

If write operations are blocked:
1. Check `kill_switch.writes_enabled` in `internet_gateway.json`
2. Ensure approval tokens are provided for write actions
3. Check role permissions in `permissions.json`

## Contributing

When adding new components:

1. Follow the existing patterns for adapters, tools, and services
2. Include proper error handling and logging
3. Add audit logging for security-sensitive operations
4. Update this README with usage examples
5. Add tests where applicable

## License

Part of the Earnetics autonomous AI system.
