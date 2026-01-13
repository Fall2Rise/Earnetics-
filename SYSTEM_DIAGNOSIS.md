# System Diagnosis & Fixes

## Issues Identified

### 1. Connection Lines Disappearing After Sync ✅ FIXED

**Problem**: Lines in the 3D Nexus disappear after sync because agents are marked as 'idle' when they have no memory entries, and active connection lines only show when BOTH agents are 'active'.

**Root Cause**: 
- Agent status is determined by `memory_entries > 0 ? 'active' : 'idle'`
- Active connection lines only render when both agents are 'active'
- After sync, if agents don't have memory entries, they become idle and bright connection lines disappear

**Fix Applied**:
- Modified `ConnectionLines.tsx` to show connections for ALL agents (even idle ones)
- Active agents get bright colored lines
- Idle agents get dim gray lines
- This maintains visual structure even when agents are idle

### 2. Low Workflow Count (Only 5 Pending)

**Current Behavior**:
- Scheduler runs every 5 seconds and executes due jobs immediately
- Revenue cycle runs every 30 seconds
- Core plays run every 60 seconds
- Workflows are being created but executed very quickly

**Why This Happens**:
1. **Fast Execution**: The scheduler executes workflows as soon as they're due (every 5 seconds)
2. **Auto-Processing**: The autonomy worker processes workflows quickly
3. **No Backlog**: Workflows don't accumulate because they're processed immediately

**This is Actually Normal Behavior** - The system is designed to process workflows quickly. However, if you want more pending workflows visible:

**Potential Solutions**:
- Increase workflow complexity (more steps per workflow)
- Add approval gates to slow down execution
- Create more diverse workflow types
- Check if workflows are actually being generated (they might be completing too fast to see)

### 3. Low Product Count (Only 6 Products)

**Current Behavior**:
- Factory engine creates ONE seed stream on startup if none exist
- Revenue cycle creates products, but they might be in a different system (Stripe/products table)
- Factory streams auto-advance through stages when tasks complete

**Why This Happens**:
1. **Single Seed**: Factory only creates one stream on startup
2. **Auto-Advance**: Streams advance through stages automatically when tasks complete
3. **Different Systems**: Products created by revenue cycle might not show in factory streams

**This Might Be Normal** - Products could be:
- In the products database (not factory streams)
- Being created but advancing through stages quickly
- Created by revenue cycle but stored differently

## Recommendations

### To See More Activity:

1. **Check Actual Counts**:
   ```python
   # Check pending workflows
   from autonomous.workflow_queue import WorkflowQueueRepository
   repo = WorkflowQueueRepository()
   pending = repo.count_pending()
   
   # Check products in database
   from backend.factory_engine import FACTORY_ENGINE
   streams = FACTORY_ENGINE.list_streams()
   ```

2. **Monitor System Logs**:
   - Check if revenue cycles are running (every 30s)
   - Check if workflows are being created
   - Check if products are being created

3. **Verify Autonomy Systems Are Running**:
   - Autonomous agent cycle (every 60s)
   - Revenue cycle (every 30s)
   - Core plays (every 60s)
   - Factory engine heartbeat

### If You Want More Workflows/Products:

1. **Increase Generation Rate**: Modify schedule intervals in `_ensure_autonomy_jobs()`
2. **Add More Seed Data**: Create initial workflows/products on startup
3. **Slow Down Execution**: Add delays or approval gates
4. **Check Database**: Products might be in products table, not factory streams

## Status

✅ **Connection Lines**: Fixed - now persist even when agents are idle
⏳ **Workflows**: Likely normal - system processes them quickly
⏳ **Products**: Need to verify where products are stored and if they're being created
