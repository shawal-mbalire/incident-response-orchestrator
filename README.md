# Incident Response Orchestrator

Multi-agent incident response system built with Google ADK, hexagonal architecture, and Angular 22.

> **Track:** Taskmaster — Event-driven autonomous workflows

## What It Does

When production breaks, engineers waste 30+ minutes context-switching between logs, metrics, alerts, and docs. This agent system does that work in **60 seconds**.

1. **Alert fires** — You input the alert details
2. **3 agents work in parallel** — Log forensics, metrics analysis, deployment tracking
3. **Synthesizer combines findings** — Identifies root cause with confidence level
4. **Report generated** — Structured incident report with timeline, evidence, and actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent Framework** | Google ADK (Agent Development Kit) |
| **Architecture** | Hexagonal (Ports & Adapters) |
| **Backend** | Python 3.12+, FastAPI |
| **Frontend** | Angular 22 (Signals, httpResource) |
| **Infrastructure** | Terraform, Google Cloud Run |
| **Cloud APIs** | Cloud Logging, Cloud Monitoring, Cloud Run |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- Google Cloud SDK
- Terraform (optional, for deployment)

### Backend

```bash
cd backend
pip install -e ".[dev]"

# Run with ADK web UI
adk web src/incident_response

# Or run with uvicorn
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:4200` and proxies API calls to the backend on port 8080.

## Project Structure

```
all_things_agentic_hack/
├── backend/                          # Python ADK Agent (Hexagonal Architecture)
│   ├── src/incident_response/
│   │   ├── domain/                   # Core business logic (zero external deps)
│   │   ├── adapters/                 # Concrete implementations (GCP, In-Memory)
│   │   ├── toolsets/                 # ADK bridges (ports → FunctionTools)
│   │   ├── agents/                   # Multi-agent orchestration
│   │   └── app/                      # Factory, entry points
│   └── main.py                       # FastAPI entry point
│
├── frontend/                         # Angular 22 Dashboard
│   └── src/app/features/             # Dashboard, Alert Input, Report View
│
├── infra/                            # Terraform IaC
│   ├── modules/                      # Cloud Run, IAM, Monitoring
│   └── environments/                 # Dev/Prod configs
│
├── ARCHITECTURE.md                   # Detailed architecture docs
├── justfile                          # Task runner
└── README.md
```

## Usage

### Create an Alert

1. Navigate to the dashboard
2. Click "New Alert"
3. Select service, severity, and describe the issue
4. Click "Trigger Analysis"

### View Reports

After analysis completes, you'll see:
- **Executive Summary** — 1-2 sentence overview
- **Root Cause** — With confidence level (high/medium/low)
- **Timeline** — Chronological events
- **Impact Assessment** — Business impact
- **Recommended Actions** — Specific next steps
- **Supporting Evidence** — Raw data from agents

## Development

### Using just

```bash
# List all commands
just

# Backend
just backend-install
just backend-adk        # Run with ADK web UI
just backend-dev        # Run with uvicorn
just backend-test       # Run tests
just backend-lint       # Lint code

# Frontend
just frontend-install
just frontend-dev       # Start dev server
just frontend-build     # Build for production

# Docker
just docker-build       # Build all images
just docker-backend-run # Run backend in Docker

# Terraform
just tf-init            # Initialize Terraform
just tf-plan            # Preview changes
just tf-apply           # Apply changes

# All-in-one
just dev                # Start all dev servers
just test               # Run all tests
just lint               # Run all linters
just format             # Format all code
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ENVIRONMENT` | `development` | Environment (development/production) |
| `AGENT_GCP_PROJECT_ID` | — | Google Cloud project ID |
| `AGENT_GCP_REGION` | `us-central1` | Google Cloud region |
| `AGENT_AGENT_MODEL` | `gemini-2.5-flash` | Gemini model to use |

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation with diagrams.

## License

MIT
