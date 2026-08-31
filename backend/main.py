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

from incident_response.adapters.inbound.fastapi.dependencies import set_container
from incident_response.adapters.inbound.fastapi.error_handlers import register_error_handlers
from incident_response.adapters.inbound.fastapi.router import router
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
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    request.state.correlation_id = correlation_id

    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    logger.info(
        "request_started",
        extra={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Correlation-ID"] = correlation_id
    return response


agent, container = create_app(settings)
set_container(container)

app.include_router(router)
register_error_handlers(app)


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.environment}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=settings.environment == "development",
    )
