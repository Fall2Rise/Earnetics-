---
description: Repository Information Overview
alwaysApply: true
---

# Fallat Digital AI Corporation Information

## Summary
A production-ready AI corporation featuring 17 specialized autonomous agents organized into 9 strategic divisions for real-world revenue generation. The system uses FastAPI for the backend, with a React/TypeScript dashboard, and is designed for containerized deployment with Docker.

## Structure
- **backend/**: Core server implementation with AI agent logic
- **fallat_crewai_dashboard/**: React/TypeScript frontend dashboard
- **agents/**: AI agent implementations
- **operations/**: Business operation databases
- **financial/**: Financial tracking and Stripe integration
- **products/**: Product definitions and resources
- **marketing/**: Marketing campaign resources
- **templates/**: HTML templates for web views
- **tests/**: Test suite for the application

## Language & Runtime
**Language**: Python 3.9+ (Recommended: Python 3.11+)
**Framework**: FastAPI 0.104.1+
**Build System**: Python setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- fastapi>=0.104.1
- uvicorn[standard]>=0.24.0
- pydantic>=2.5.0
- openai>=1.6.0
- anthropic>=0.20.0
- stripe>=7.8.0
- httpx>=0.25.0
- requests>=2.31.0
- python-dotenv>=1.0.0

**Development Dependencies**:
- ruff>=0.1.6
- pytest>=7.4.0
- pytest-asyncio>=0.21.0

## Build & Installation
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# At minimum, add your OpenAI API key

# Install dependencies
pip install -r requirements.txt

# Run the server
python backend/main_server.py
```

## Docker
**Dockerfile**: Dockerfile
**Image**: python:3.11-slim
**Configuration**: Production-ready container with non-root user (appuser)
**Deployment**:
```bash
# Build and run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d
```

## Testing
**Framework**: pytest 7.0+
**Test Location**: tests/
**Naming Convention**: test_*.py
**Configuration**: pytest.ini
**Run Command**:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only smoke tests
pytest -m smoke

# Run tests with coverage
pytest --cov=backend
```

## Frontend Dashboard
**Framework**: React 18.3.1 with TypeScript
**Build Tool**: Vite 5.4.2
**Styling**: TailwindCSS 3.4.1
**Package Manager**: npm/yarn
**Build Commands**:
```bash
# Navigate to dashboard directory
cd fallat_crewai_dashboard

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

## Operational Status

### Fully Implemented & Ready for Deployment ✅
- **17 Autonomous AI Agents**: Complete corporate hierarchy with specialized roles
- **Real Payment Processing**: Stripe integration for live transactions
- **80/20 Revenue Split**: Automated revenue distribution system
- **Production Containerization**: Docker setup with security best practices
- **Database System**: SQLite with comprehensive business intelligence tracking
- **Test Suite**: Complete smoke and integration tests
- **Corporate Structure**: 
  - Executive Board (Akasha, Atlas, Omen, Obsidian)
  - R&D Division (Noir)
  - Revenue Division (Nova, Mercury)
  - Product Division (Forge)
  - Finance Division (Vega)
  - Infrastructure Division (Seraph)

### Technical Features Ready for Production ✅
- **Asynchronous Agent Execution**: Efficient parallel processing
- **Database Operations**: Complete data persistence for all agents
- **Error Handling & Logging**: Comprehensive error management
- **API Endpoints**: Complete FastAPI implementation
- **Market Analysis**: Integration with pytrends and yfinance
- **Health Monitoring**: System health endpoints and checks

### Pending Implementation 🚧
- Advanced AI model fine-tuning
- Multi-currency support
- Advanced analytics dashboard
- Mobile app integration
- API rate limiting & authentication
- Advanced fraud detection
- Dashboard component integration
- Real-time monitoring enhancements

## Revenue Generation Capabilities
The system is fully operational for real-world revenue generation with:

1. **Product Sales**: Ready to sell digital products ($97-$497)
2. **Payment Processing**: Complete Stripe integration
3. **Revenue Distribution**: Automated 80/20 split (owner/reinvestment)
4. **Sales Funnel**: Fully implemented conversion tracking
5. **Marketing Campaigns**: Real data tracking and optimization
6. **Financial Reporting**: Complete business intelligence

The core business operations are production-ready, with the next phase focused on scaling and enhancing the existing functionality rather than implementing missing critical features.