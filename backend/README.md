# Incident Response Orchestrator

Multi-agent incident response system built with Google ADK, hexagonal architecture, and Angular 22.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INCIDENT RESPONSE ORCHESTRATOR            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │   Coordinator │ ◄── Alert Input                          │
│  └──────┬───────┘                                           │
│         ▼                                                    │
│  ┌──────────────────────────────────────────────┐           │
│  │              ParallelAgent (fan-out)          │           │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────┐ │           │
│  │  │   Log        │ │  Metrics    │ │ Deploy │ │           │
│  │  │   Forensics  │ │  Analyzer   │ │Tracker │ │           │
│  │  └─────────────┘ └─────────────┘ └────────┘ │           │
│  └──────────────────────────────────────────────┘           │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │  Synthesizer  │ ◄── Combines findings                    │
│  └──────┬───────┘                                           │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   Report      │ ──► Structured incident report           │
│  │   Generator   │                                          │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Local Development

```bash
# Install dependencies
cd backend
pip install -e ".[dev]"

# Run with ADK web UI
adk web src/incident_response

# Or run with uvicorn
uvicorn main:app --reload
```

### Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy incident-response-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Project Structure

```
backend/
├── src/incident_response/
│   ├── domain/              # Core business logic (no external deps)
│   │   ├── models/          # Domain entities
│   │   ├── ports/           # Abstract interfaces
│   │   └── services/        # Business rules
│   ├── adapters/            # Concrete implementations
│   │   ├── inbound/         # API, CLI
│   │   └── outbound/        # Google Cloud, In-Memory
│   ├── toolsets/            # ADK tool bridges
│   ├── agents/              # Multi-agent orchestration
│   ├── config/              # Settings, DI container
│   └── app/                 # Factory, entry points
├── main.py                  # FastAPI entry point
└── pyproject.toml
```

## Environment Variables

```bash
AGENT_ENVIRONMENT=development
AGENT_GCP_PROJECT_ID=your-project-id
AGENT_GCP_REGION=us-central1
AGENT_AGENT_MODEL=gemini-2.5-flash
```
