"""FastAPI entry point for the Incident Response Orchestrator.

This provides a REST API alongside the ADK agent interface.
"""

import logging
import os
import time
import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from incident_response.app.factory import create_app
from incident_response.config.settings import Settings

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("incident_response")

app = FastAPI(
    title="Incident Response Orchestrator",
    description="Multi-agent incident analysis using Google ADK",
    version="0.1.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "https://incident-response-frontend-*.run.app",
]

if settings.environment == "development":
    ALLOWED_ORIGINS.append("http://localhost:4200")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    logger.info(
        "request_started",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path},
    )
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Initialize agent and container
agent, container = create_app(settings)


class AlertRequest(BaseModel):
    service: str = Field(..., min_length=1, description="Service name")
    severity: str = Field(default="high", pattern="^(critical|high|medium|low)$")
    message: str = Field(..., min_length=1, description="Alert message")
    metrics: dict = Field(default_factory=dict)


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.environment}


@app.post("/api/alerts")
async def create_alert(alert_data: AlertRequest):
    from incident_response.domain.models.alert import Alert

    alert = Alert.from_dict(alert_data.model_dump())
    report = await container.incident_service.analyze_incident(alert)
    return report.to_dict()


@app.get("/api/incidents")
async def list_incidents(service: str | None = None, minutes: int = 30):
    if container.state_store:
        incidents = await container.state_store.list_collection("incidents", limit=100)
        return incidents
    return []


@app.get("/api/incidents/{incident_id}/report")
async def get_report(incident_id: str):
    report = await container.incident_service.get_report(incident_id)
    if report is None:
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    return report.to_dict()


@app.get("/api/services")
async def list_services():
    return {
        "services": [
            "api-gateway",
            "user-service",
            "payment-service",
            "notification-service",
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=settings.environment == "development",
    )
