# Earnetics Intelligence System - Setup Guide

## Complete Setup Instructions

### Step 1: Environment Setup

1. **Navigate to project root:**
   ```powershell
   cd C:\AI_Projects\Fallat_CrewAI
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Verify Python version:**
   ```powershell
   python --version  # Should be 3.11+
   ```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

**Key dependencies:**
- `fastapi` - API framework
- `sqlalchemy` - Database ORM
- `requests` - HTTP client
- `stripe` - Payment processing (optional)
- `pydantic` - Data validation

### Step 3: Configure Environment Variables

Create or update `.env` file in project root:

```env
# Required
FALLAT_API_TOKEN=your_api_token_here

# Optional - Email Services
MAILGUN_API_KEY=key-...
MAILGUN_DOMAIN=mg.example.com
SENDGRID_API_KEY=SG....

# Optional - Social Media
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

# Optional - Payment Processing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Step 4: Configure Internet Gateway

Edit `earnetics/config/internet_gateway.json`:

```json
{
  "enabled": true,
  "kill_switch": {
    "writes_enabled": true,  // Set to true to enable write operations
    "global_enabled": true
  },
  "rate_limits": {
    "global_per_min": 120,
    "per_domain_per_min": 30,
    "per_agent_per_min": 20
  }
}
```

### Step 5: Configure Permissions

Edit `earnetics/config/permissions.json` to set role permissions:

- **EXEC**: Full access, no approval needed
- **INTELLIGENCE_RND**: Read-only web access
- **OPS**: Limited writes with approval
- **MARKETING**: Draft only, requires approval
- **SCRAPER**: Read-only, strict rate limits

### Step 6: Initialize Databases

Databases are created automatically on first use. To verify:

```python
python -c "from earnetics.knowledge_store.store import KnowledgeStore; s = KnowledgeStore(); print('Knowledge Store initialized')"
```

### Step 7: Test Installation

Run the demo scripts:

```powershell
# Intelligence Pipeline Demo
python earnetics/scripts/demo_intel_pipeline.py

# Internet Gateway Demo
python earnetics/scripts/demo_gateway.py
```

### Step 8: Start Backend Server

```powershell
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
```

### Step 9: Access Intelligence Page

1. Start frontend (in separate terminal):
   ```powershell
   cd fallat_crewai_dashboard
   npm run dev
   ```

2. Navigate to: `http://localhost:5173`

3. Click on "Intelligence" in the navigation

## Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured with `FALLAT_API_TOKEN`
- [ ] Internet Gateway config updated
- [ ] Permissions config reviewed
- [ ] Demo scripts run successfully
- [ ] Backend server starts without errors
- [ ] Frontend loads Intelligence page
- [ ] All 6 Intelligence components visible

## Common Issues

### "ModuleNotFoundError"

**Solution:** Ensure virtual environment is activated and dependencies are installed.

### "FALLAT_API_TOKEN required"

**Solution:** Add `FALLAT_API_TOKEN` to `.env` file.

### Write operations blocked

**Solution:** 
1. Set `kill_switch.writes_enabled: true` in `internet_gateway.json`
2. Provide approval tokens for write actions
3. Check role permissions

### Database locked errors

**Solution:** Ensure only one process is accessing the database at a time.

## Next Steps

1. **Add Knowledge Sources**: Configure additional connectors in `knowledge_sources.json`
2. **Create Opportunities**: Use Intelligence workflows to discover and triage opportunities
3. **Deploy Campaigns**: Use Revenue Loop Engine to deploy validated opportunities
4. **Monitor KPIs**: Track performance through telemetry system
5. **Build Playbooks**: Convert successful campaigns into validated playbooks

## Support

For issues or questions:
1. Check `earnetics/README.md` for usage examples
2. Review `earnetics/STATUS.md` for implementation status
3. Check backend logs for detailed error messages
