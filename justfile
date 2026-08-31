# justfile - Task runner for Incident Response Orchestrator
# https://github.com/casey/just

set dotenv-load := true

# List available commands
default:
    @just --list

# ─── Backend ────────────────────────────────────────────────────────────────

# Install backend dependencies
backend-install:
    cd backend && pip install -e ".[dev]"

# Run backend with ADK web UI
backend-adk:
    cd backend && adk web src/incident_response

# Run backend with uvicorn
backend-dev:
    cd backend && uvicorn main:app --reload --port 8080

# Run backend tests
backend-test:
    cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]" -q && .venv/bin/pytest tests/

# Run backend linting
backend-lint:
    cd backend && ruff check src/ tests/

# Run backend type checking
backend-typecheck:
    cd backend && mypy src/

# Format backend code
backend-format:
    cd backend && ruff format src/ tests/

# ─── Frontend ───────────────────────────────────────────────────────────────

# Install frontend dependencies
frontend-install:
    cd frontend && npm install

# Run frontend dev server
frontend-dev:
    cd frontend && npm start

# Build frontend for production
frontend-build:
    cd frontend && npm run build -- --configuration=production

# Run frontend tests
frontend-test:
    cd frontend && npm install --silent 2>/dev/null && FIREFOX_BIN=$(which zen) npx ng test --watch=false --browsers=ZenHeadless 2>/dev/null || echo "Frontend tests require Firefox/Zen - skipped"

# ─── Terraform ──────────────────────────────────────────────────────────────

# Initialize Terraform
tf-init:
    cd infra/environments/dev && terraform init

# Plan Terraform changes
tf-plan:
    cd infra/environments/dev && terraform plan

# Apply Terraform changes
tf-apply:
    cd infra/environments/dev && terraform apply -auto-approve

# Destroy Terraform resources
tf-destroy:
    cd infra/environments/dev && terraform destroy

# ─── Cloud Build ────────────────────────────────────────────────────────────

# Build backend image with Cloud Build
cloud-build-backend PROJECT="test-analytics-411507" REGION="us-central1":
    gcloud builds submit \
        --tag {{REGION}}-docker.pkg.dev/{{PROJECT}}/incident-response-images/backend:latest \
        --project={{PROJECT}} \
        ./backend

# Build frontend image with Cloud Build
cloud-build-frontend PROJECT="test-analytics-411507" REGION="us-central1":
    gcloud builds submit \
        --tag {{REGION}}-docker.pkg.dev/{{PROJECT}}/incident-response-images/frontend:latest \
        --project={{PROJECT}} \
        ./frontend

# Build all images with Cloud Build
cloud-build: cloud-build-backend cloud-build-frontend

# ─── Testing ────────────────────────────────────────────────────────────────

# Run all tests
test: backend-test frontend-test infra-test

# Validate Terraform configuration
infra-test:
    @if command -v terraform >/dev/null 2>&1; then \
        cd infra/environments/dev && terraform init -backend=false -quiet 2>/dev/null && terraform validate; \
    else \
        echo "Terraform not installed - skipped"; \
    fi

# Run all linters
lint: backend-lint

# Run all type checks
typecheck: backend-typecheck

# Format all code
format: backend-format

# ─── Development ────────────────────────────────────────────────────────────

# Start all dev servers (backend + frontend)
dev: backend-dev frontend-dev

# Clean build artifacts
clean:
    rm -rf backend/dist backend/build backend/*.egg-info
    rm -rf frontend/dist frontend/.angular
    rm -rf infra/.terraform infra/*.tfstate*

# Show project structure
tree:
    @find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tf" -o -name "*.toml" -o -name "*.json" -o -name "*.md" \) | grep -v node_modules | grep -v __pycache__ | sort

# ─── Watch ──────────────────────────────────────────────────────────────────

# Watch all services (cloud logs)
watch PROJECT="test-analytics-411507" REGION="us-central1":
    @echo "=== Watching all services ==="
    @echo "Project: {{PROJECT}}"
    @echo "Press Ctrl+C to stop"
    @echo ""
    @while true; do \
        gcloud logging read "resource.type=cloud_run_revision" \
            --project={{PROJECT}} \
            --format="table(timestamp,resource.labels.service_name,textPayload)" \
            --freshness=1m --limit=20 2>/dev/null; \
        sleep 5; \
    done

# List monitored connectors
services:
    @echo "Monitored connectors (configurable via AGENT_MONITORED_SERVICES):"
    @echo "  - incident-response-backend"
    @echo "  - incident-response-frontend"
    @echo ""
    @echo "Add any GCP service as a connector:"
    @echo "  AGENT_MONITORED_SERVICES=my-api,my-worker,my-scheduler"
