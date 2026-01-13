# 📘 Earnetics AI Corporation - Complete Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Architecture](#architecture)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [API Documentation](#api-documentation)
7. [Agent System](#agent-system)
8. [Features & Capabilities](#features--capabilities)
9. [Troubleshooting](#troubleshooting)
10. [Configuration](#configuration)

---

## System Overview

**Earnetics** is an autonomous AI corporation system with 41 specialized AI agents organized into 12 departments. The system operates continuously to generate revenue, manage operations, and optimize performance.

### Key Components
- **Backend**: FastAPI server with WebSocket support
- **Frontend**: React/TypeScript 3D Command Nexus dashboard
- **Agents**: 41 AI agents across 12 departments
- **Database**: SQLite databases for persistence
- **Performance Monitoring**: Real-time health tracking and optimization

---

## Quick Start Guide

### Prerequisites
- Python 3.12+
- Node.js 18+
- Virtual environment activated

### Starting the System

#### 1. Navigate to Project Directory
```powershell
cd C:\AI_Projects\Fallat_CrewAI
```

#### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

#### 3. Start Backend Server
```powershell
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Start Frontend (New Terminal)
```powershell
# IMPORTANT: Make sure you're starting from the project root
# If you're not sure, run this first:
cd C:\AI_Projects\Fallat_CrewAI

# Then navigate to frontend directory
cd fallat_crewai_dashboard

# Verify you're in the right place (should show package.json)
Get-ChildItem package.json

# Start the dev server
npm run dev
```

#### 5. Access the System
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Quick Start Script
```powershell
.\START_TONIGHT.ps1
```

---

## Architecture

### Backend Structure
```
backend/
├── main_server.py          # Main FastAPI application
├── real_ai_agents.py       # 41 AI agents implementation
├── api/                     # API routers
│   ├── agents_router.py
│   ├── performance_router.py
│   ├── dashboard_router.py
│   └── ... (30+ routers)
├── services/                # Business logic services
│   ├── performance_monitor.py
│   ├── intelligent_cache.py
│   ├── lead_generation_service.py
│   └── mailops_service.py
├── middleware/              # Middleware components
│   └── rate_limiter.py
└── corporate_memory.py      # Database layer
```

### Frontend Structure
```
fallat_crewai_dashboard/
├── src/
│   ├── scenes/              # 3D scenes
│   │   └── CommandRoom.tsx
│   ├── components/
│   │   ├── 3d/             # 3D components
│   │   │   ├── CommandRoom3D.tsx
│   │   │   ├── DivisionalZone.tsx
│   │   │   ├── ConnectionLines.tsx
│   │   │   └── ...
│   │   └── dashboard/      # Dashboard panels
│   ├── stores/             # Zustand state management
│   └── api/                # API client services
```

---

## Backend Setup

### Environment Variables
Create a `.env` file in the project root:

```env
# Required
FALLAT_API_TOKEN=your_api_token_here

# Optional but Recommended
STRIPE_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
SMTP_EMAIL=your@email.com
SMTP_PASSWORD=your_password

# Performance
FALLAT_RATE_LIMIT_PER_MIN=60
```

### Database Files
The system uses SQLite databases:
- `business_database.db` - Main business data
- `performance_metrics.db` - Performance tracking
- `cache.db` - Intelligent caching
- `audit_log.db` - Audit logs
- `vector_memory.db` - Vector embeddings

### Starting Backend
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
```

### Backend Features
- ✅ 41 AI agents across 12 departments
- ✅ Real-time WebSocket communication
- ✅ Performance monitoring
- ✅ Intelligent caching
- ✅ Task prioritization
- ✅ Lead generation & email marketing
- ✅ Revenue generation automation
- ✅ Workflow scheduling

---

## Frontend Setup

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager

### Installation
```powershell
# First, navigate to project root
cd C:\AI_Projects\Fallat_CrewAI

# Then go to frontend directory
cd fallat_crewai_dashboard

# Verify you're in the right place
# You should see: package.json, src/, node_modules/, etc.
Get-Location  # Should show: C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard

# Install dependencies
npm install
```

### Starting Frontend
```powershell
# Make sure you're in the frontend directory
# If not, navigate there first:
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard

# Verify current location
Get-Location

# Start development server
npm run dev
```

### Frontend Features
- ✅ 3D Command Nexus visualization
- ✅ Real-time agent status
- ✅ Department visualization
- ✅ Performance metrics dashboard
- ✅ Lead management panels
- ✅ Marketing recipients view
- ✅ Subscriber management
- ✅ Interactive 3D environment

### Frontend URLs
- **Development**: http://localhost:5173
- **Production Build**: `npm run build`

---

## API Documentation

### Core Endpoints

#### System Status
```
GET /api/system/status
GET /api/system_status (legacy)
```
Returns system health, metrics, and agent status.

#### Agent Management
```
GET /api/agents/status
GET /api/agents/{agent_name}
POST /api/agents/update
```

#### Performance Monitoring
```
GET /api/performance/health
GET /api/performance/bottlenecks?timeframe_hours=24
GET /api/performance/success-rates
GET /api/performance/cache/stats
POST /api/performance/cache/invalidate
```

#### Lead Management
```
GET /api/leads/scraped?limit=50&offset=0
POST /api/leads/{lead_id}/qualify
GET /api/marketing/recipients
GET /api/subscribers?category=all
```

#### Revenue & Products
```
GET /api/products/list
GET /api/financial/metrics
GET /api/workflows/pending
```

### WebSocket
```
WS /ws
```
Real-time updates for agent activity, system status, and metrics.

### Full API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

---

## Agent System

### Departments & Agents

#### 1. Executive Board
- **Akasha** - CEO
- **Atlas** - CTO
- **Vega** - CFO
- **Omen** - COO

#### 2. Finance & Revenue
- **StripeOps** - Payment Operations
- **Orion** - Financial Analyst

#### 3. Creative & Product
- **Nova** - Marketing Director
- **Mercury** - Sales Director
- **Muse** - Creative Director
- **Lex** - Content Strategist

#### 4. Tech & Infrastructure
- **Vortex** - DevOps Engineer
- **Lumen** - System Architect
- **Cascade** - Integration Specialist

#### 5. Legal & Sovereignty
- **Keeper** - Legal Advisor
- **Sentinel** - Compliance Officer

#### 6. Health & Human Factor
- **WellnessCoordinator** - Employee Wellness

#### 7. Corporate Analytics
- **DataAnalyst** - Data Analysis
- **MetricsReporter** - Performance Reporting

#### 8. Corporate Execution
- **Pulse** - Operations Manager
- **Relay** - Task Coordinator
- **Harbor** - Resource Manager

#### 9. Email Marketing
- **Aurora** - Email Campaign Manager
- **Echo** - List Manager
- **Quill** - Copywriter

#### 10. Revenue Strategy Cell
- **StrategyDirector** - Strategic Planning
- **MarketAnalyst** - Market Research
- **OpportunityScout** - Opportunity Identification
- **PlayValidator** - Strategy Validation

#### 11. Revenue Execution
- **ExecutionCommander** - Execution Oversight
- **LaunchSpecialist** - Product Launch
- **RevenueOperator** - Revenue Operations

#### 12. Lead Generation & Acquisition
- **WebScraper** - Web Scraping
- **LeadQualifier** - Lead Qualification
- **ListBuilder** - Email List Building

### Agent Capabilities
- ✅ Autonomous decision-making
- ✅ Performance tracking
- ✅ Success rate learning
- ✅ Revenue impact measurement
- ✅ Adaptive strategy selection
- ✅ Retry logic with exponential backoff

---

## Features & Capabilities

### Performance Optimization
- **Performance Monitoring**: Real-time health tracking
- **Bottleneck Detection**: Automatic identification of slow operations
- **Success Rate Analytics**: Track what works and what doesn't
- **Intelligent Caching**: Reduce database and API load
- **Task Prioritization**: Revenue-impact-based scheduling

### Revenue Generation
- **Automated Product Creation**: Stripe integration
- **Payment Link Generation**: Automatic checkout links
- **Landing Page Generation**: HTML landing pages
- **Marketing Campaigns**: Automated email campaigns
- **Lead Generation**: Web scraping and qualification

### Lead Management
- **Web Scraping**: Targeted website scraping
- **Lead Qualification**: Automatic validation
- **Email List Building**: Subscriber management
- **Campaign Management**: Marketing automation
- **Category Organization**: Subscriber categorization

### 3D Visualization
- **Command Nexus**: Interactive 3D environment
- **Department Zones**: Visual department representation
- **Agent Nodes**: Individual agent visualization
- **Connection Lines**: Inter-department communication
- **Data Streams**: Real-time data flow visualization
- **Activity Bursts**: Visual feedback for agent actions
- **Floating Metrics**: Key metrics in 3D space

---

## Troubleshooting

### Backend Won't Start

**Issue**: Import errors or circular imports
```powershell
# Check for syntax errors
python -m py_compile backend/main_server.py

# Verify imports
python -c "import backend.main_server"
```

**Issue**: Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
Stop-Process -Id <PID> -Force
```

### Frontend Won't Start

**Issue**: Node modules not installed
```powershell
cd fallat_crewai_dashboard
npm install
```

**Issue**: Port 5173 in use
```powershell
# Change port in vite.config.ts or use:
npm run dev -- --port 5174
```

### Connection Issues

**Issue**: Frontend can't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in `backend/main_server.py`
- Verify API base URL in frontend config

**Issue**: WebSocket connection fails
- Check WebSocket endpoint: `ws://localhost:8000/ws`
- Verify backend WebSocket handler is active
- Check browser console for errors

### Performance Issues

**Issue**: Slow response times
- Check `/api/performance/bottlenecks` endpoint
- Review database query performance
- Enable caching for expensive operations
- Check system resources (CPU, memory)

**Issue**: High request count
- Review frontend polling intervals
- Enable caching where appropriate
- Check for duplicate API calls

---

## Configuration

### Backend Configuration

#### Rate Limiting
```python
# In backend/main_server.py
FALLAT_RATE_LIMIT_PER_MIN=60  # Requests per minute
```

#### Performance Monitoring
```python
# Automatic - no configuration needed
# Metrics stored in performance_metrics.db
```

#### Caching
```python
# In backend/services/intelligent_cache.py
max_size_mb = 100  # Maximum cache size
```

### Frontend Configuration

#### API Base URL
```typescript
// In fallat_crewai_dashboard/src/api/
const API_BASE_URL = 'http://localhost:8000';
```

#### WebSocket URL
```typescript
// In fallat_crewai_dashboard/src/stores/
const WS_URL = 'ws://localhost:8000/ws';
```

### Agent Configuration

#### LLM Provider
Agents use Ollama by default. To change:
```python
# Set environment variable
OPENAI_API_KEY=sk-...  # For OpenAI
# Or configure in backend/llm_client.py
```

#### Department Positions (3D)
```typescript
// In fallat_crewai_dashboard/src/scenes/CommandRoom.tsx
const DEPARTMENT_ZONES = [
  {
    department: 'Executive Board',
    position: [0, 2, 0],
    scale: [4, 3, 4],
    color: '#FFD700',
  },
  // ... other departments
];
```

---

## Advanced Features

### Custom Agents
Create new agents in `backend/real_ai_agents.py`:
```python
class MyCustomAgent(RealAIAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            role="Custom Role",
            division="Custom Department",
            # ...
        )
```

### Custom API Endpoints
Add new endpoints in `backend/api/`:
```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/endpoint")
def custom_endpoint():
    return {"message": "Hello"}
```

### Workflow Automation
Configure workflows in `backend/workflow_scheduler.py`:
```python
@scheduler.register_handler("my_workflow")
async def handle_my_workflow(context):
    # Your workflow logic
    pass
```

---

## Maintenance

### Database Backup
```powershell
# Backup all databases
Copy-Item *.db backup/
```

### Log Management
Logs are stored in:
- `logs/` - Application logs
- `uvicorn.out.log` - Server output
- `uvicorn.err.log` - Server errors

### Performance Cleanup
```powershell
# Clear old performance metrics (via API)
POST /api/performance/cache/invalidate?pattern=old_
```

---

## Support & Resources

### Documentation Files
- `README.md` - Project overview
- `START_HERE.md` - Getting started
- `EFFICIENCY_IMPROVEMENTS.md` - Performance features
- `OPERATIONS_GUIDE.md` - Operations reference

### API Documentation
- Interactive: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### System Status
- Health: `GET /api/performance/health`
- Metrics: `GET /api/system/status`
- Bottlenecks: `GET /api/performance/bottlenecks`

---

## Quick Reference

### Start Everything
```powershell
# Terminal 1: Backend
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
# Navigate to project root first
cd C:\AI_Projects\Fallat_CrewAI

# Then go to frontend directory
cd fallat_crewai_dashboard

# Verify you're in the right directory
Get-Location  # Should show: C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
Get-ChildItem package.json  # Should show the file

# Start the frontend
npm run dev
```

### Stop Everything
```powershell
# Stop all Python/Node processes
Get-Process | Where-Object {$_.ProcessName -match "python|node"} | Stop-Process -Force
```

### Check Status
```powershell
# Backend health
Invoke-WebRequest http://localhost:8000/api/system/status

# Frontend
Start-Process http://localhost:5173
```

---

**Last Updated**: January 2025
**Version**: 1.0
**System**: Earnetics AI Corporation
