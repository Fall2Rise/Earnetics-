# Autonomy Loop Files — Complete List

## Main Autonomy Loop Files

### 1. `autonomous/automation_worker.py`
**Path**: `autonomous/automation_worker.py`  
**Class**: `AutomationWorker`  
**Main Loop**: `_run_loop()` (line 132)  
**Description**: Main continuous loop that processes queue items from the workflow queue. This is the primary autonomy worker that executes tasks autonomously.

**Key Methods**:
- `_run_loop()` - Main while loop that processes tasks
- `process_once()` - Processes available tasks once
- `_execute_queue_item()` - Executes individual queue items
- `start()` - Starts the worker loop
- `stop()` - Stops the worker loop

---

### 2. `autonomous/scheduler.py`
**Path**: `autonomous/scheduler.py`  
**Class**: `AutonomyScheduler`  
**Main Loops**: 
- `_telemetry_loop()` (line 58)
- `_workflow_loop()` (line 59)
- `_monitor_loop()` (line 63)

**Description**: Scheduler that runs multiple background loops for telemetry, workflow monitoring, and system monitoring.

---

### 3. `backend/autonomous_ai_system.py`
**Path**: `backend/autonomous_ai_system.py`  
**Class**: `AutonomousBusinessManager`  
**Main Loop**: `run_autonomous_decision_cycle()` (line 487)  
**Description**: Coordinates all AI agents to run the business autonomously. Runs decision-making cycles where agents analyze situations and make decisions.

**Key Methods**:
- `run_autonomous_decision_cycle()` - Main decision cycle
- `_coordinate_actions()` - Coordinates actions from multiple agents

---

### 4. `backend/real_ai_agents.py`
**Path**: `backend/real_ai_agents.py`  
**Classes**: Multiple `RealAIAgent` subclasses  
**Main Loops**: `_execute_actions()` methods in each agent class  
**Description**: Individual agent classes that execute actions. Each agent has its own execution logic.

**Key Agent Classes**:
- `Vortex` - `_execute_actions()` (line 1425)
- `Cascade` - `_execute_actions()` (line 1491)
- `Keeper` - `_execute_actions()` (line 1686)
- `Sentinel` - `_execute_actions()` (line 1709)
- `Pulse` - `_execute_actions()` (line 1732)
- And many more...

---

### 5. `backend/workflow_engine.py`
**Path**: `backend/workflow_engine.py`  
**Class**: `ContinuousWorkflowOrchestrator`  
**Description**: Orchestrates continuous workflow execution loops.

---

### 6. `backend/ewc/revenue_loop.py`
**Path**: `backend/ewc/revenue_loop.py`  
**Class**: `RevenueLoopRunner`  
**Main Method**: `run()` (line 154)  
**Description**: Revenue generation loop that runs through revenue generation steps.

**Key Methods**:
- `run()` - Main revenue loop execution
- `_run_step()` - Runs individual flow steps

---

### 7. `backend/autonomous_financial_processor.py`
**Path**: `backend/autonomous_financial_processor.py`  
**Class**: `AutonomousFinancialProcessor`  
**Description**: Processes financial operations autonomously (payouts, reinvestments).

---

## Startup & Integration Files

### 8. `backend/main_server.py`
**Path**: `backend/main_server.py`  
**Functions**:
- `_startup_autonomy_worker()` (line 1129) - Startup hook that initializes autonomy workers
- `_start_autonomy_worker_on_boot()` (line 400) - Starts autonomy worker on boot
- `_scheduler_loop()` (line 1188) - Background loop for scheduled revenue jobs
- `_evolution_loop()` (line 1136) - Evolution engine feedback loop
- `_init_autonomy_worker()` (line 556) - Factory function for creating workers

**Description**: Main server file that starts all autonomy loops on application startup. This is where all the loops are initialized and started.

**Key Startup Tasks**:
- Starts `AutomationWorker` via `_start_autonomy_worker_on_boot()`
- Starts evolution engine loop
- Starts workflow scheduler loop
- Starts factory engine
- Starts DFY worker

---

### 9. `backend/api/autonomy_worker_router.py`
**Path**: `backend/api/autonomy_worker_router.py`  
**Description**: API endpoints for controlling the autonomy worker (start, stop, status).

**Endpoints**:
- `GET /autonomy/worker/status` - Get worker status
- `POST /autonomy/worker/start` - Start worker
- `POST /autonomy/worker/stop` - Stop worker

---

## Supporting Files

### 10. `autonomous/workflow_queue.py`
**Path**: `autonomous/workflow_queue.py`  
**Class**: `WorkflowQueueRepository`  
**Description**: Manages the workflow queue that the automation worker processes.

---

### 11. `autonomous/workflow_manager.py`
**Path**: `autonomous/workflow_manager.py`  
**Description**: Manages workflow execution and state.

---

### 12. `backend/services/dfy_income_engine.py`
**Path**: `backend/services/dfy_income_engine.py`  
**Function**: `start_dfy_worker()`  
**Description**: Starts the DFY (Done For You) income engine worker.

---

## Summary

**Primary Autonomy Loops** (where tools are executed):
1. `autonomous/automation_worker.py` - **Main worker loop** ⭐
2. `backend/main_server.py` - **Startup integration** ⭐
3. `backend/real_ai_agents.py` - **Individual agent execution**

**Secondary Loops**:
4. `autonomous/scheduler.py` - Scheduler loops
5. `backend/autonomous_ai_system.py` - Decision cycles
6. `backend/ewc/revenue_loop.py` - Revenue generation
7. `backend/workflow_engine.py` - Workflow orchestration

**To wire tools through ToolExecutor, focus on:**
- `autonomous/automation_worker.py` - `_execute_queue_item()` method
- `backend/real_ai_agents.py` - `_execute_actions()` methods
- `backend/ewc/revenue_loop.py` - `run()` method
