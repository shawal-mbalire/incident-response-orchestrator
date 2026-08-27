"""FastAPI entry point for the Incident Response Orchestrator.

This provides a REST API alongside the ADK agent interface.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from incident_response.app.factory import create_app
from incident_response.config.settings import Settings

app = FastAPI(
    title="Incident Response Orchestrator",
    description="Multi-agent incident analysis using Google ADK",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent and container
settings = Settings()
agent, container = create_app(settings)


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.environment}


@app.post("/api/alerts")
async def create_alert(alert_data: dict):
    from incident_response.domain.models.alert import Alert

    alert = Alert.from_dict(alert_data)
    report = await container.incident_service.analyze_incident(alert)
    return report.to_dict()


@app.get("/api/incidents/{incident_id}/report")
async def get_report(incident_id: str):
    report = await container.incident_service.get_report(incident_id)
    if report is None:
        return {"error": "Report not found"}, 404
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
