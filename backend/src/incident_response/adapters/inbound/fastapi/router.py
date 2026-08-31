import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from incident_response.adapters.inbound.fastapi.dependencies import get_analysis_service, get_container
from incident_response.domain.models.alert import Alert
from incident_response.domain.ports.inbound.analysis import IncidentAnalysisPort
from incident_response.domain.value_objects.correlation_id import CorrelationId
from incident_response.domain.value_objects.time_range import TimeRange

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class AlertRequest(BaseModel):
    service: str = Field(
        ..., min_length=1, description="Service name"
    )
    severity: str = Field(
        default="high", pattern="^(critical|high|medium|low)$"
    )
    message: str = Field(
        ..., min_length=1, description="Alert message"
    )
    metrics: dict = Field(default_factory=dict)


@router.post("/alerts")
async def create_alert(
    alert_data: AlertRequest,
    analysis: IncidentAnalysisPort = Depends(get_analysis_service),
    correlation_id: str | None = Query(default=None),
):
    corr_id = (
        CorrelationId.from_string(correlation_id)
        if correlation_id
        else CorrelationId.generate()
    )
    alert = Alert.from_dict(
        alert_data.model_dump() | {"correlation_id": str(corr_id)}
    )
    report = await analysis.analyze_incident(alert, correlation_id=corr_id)
    return report.to_dict()


@router.get("/incidents")
async def list_incidents(
    service: str | None = Query(default=None),
    minutes: int = Query(default=30, ge=1, le=1440),
    analysis: IncidentAnalysisPort = Depends(get_analysis_service),
):
    return await analysis.list_incidents(service=service)


@router.get("/incidents/{incident_id}/report")
async def get_report(
    incident_id: str,
    analysis: IncidentAnalysisPort = Depends(get_analysis_service),
):
    report = await analysis.get_report(incident_id)
    if report is None:
        from incident_response.domain.exceptions import NotFoundError

        raise NotFoundError("Incident", incident_id)
    return report.to_dict()


@router.get("/services")
async def list_services():
    container = get_container()
    return {"services": container.settings.services_list}


@router.get("/logs")
async def get_logs(
    service: str | None = Query(default=None),
    minutes: int = Query(default=30, ge=1, le=1440),
    severity: str = Query(default="DEFAULT"),
):
    """Pull centralized logs from monitored incident-response services."""
    container = get_container()
    services = [service] if service else container.settings.services_list
    time_range = TimeRange.last_minutes(minutes)

    all_logs = []
    for svc in services:
        try:
            logs = await container.monitoring.query_logs(
                service=svc,
                severity=severity,
                time_range=time_range,
            )
            for log in logs:
                all_logs.append({
                    "timestamp": log.timestamp.isoformat(),
                    "service": svc,
                    "severity": log.severity.value,
                    "message": log.message,
                    "labels": log.labels,
                })
        except Exception as e:
            logger.warning("log_fetch_error", extra={"service": svc, "error": str(e)})

    all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"logs": all_logs[:100], "count": len(all_logs)}


@router.get("/metrics")
async def get_metrics(
    service: str = Query(...),
    minutes: int = Query(default=30, ge=1, le=1440),
):
    """Pull metrics for a service."""
    container = get_container()
    time_range = TimeRange.last_minutes(minutes)
    result = await container.monitoring.fetch_metrics(
        service=service,
        metric_types=["error_rate", "latency_p99", "cpu", "memory"],
        time_range=time_range,
    )
    return {"service": service, "metrics": result.to_dict()}


@router.post("/analyze")
async def analyze_logs(
    service: str | None = Query(default=None),
    minutes: int = Query(default=30, ge=1, le=1440),
):
    """Auto-analyze logs from all services using Gemini to detect anomalies and generate bug reports."""
    container = get_container()
    analysis = get_analysis_service()
    services = [service] if service else container.settings.services_list
    time_range = TimeRange.last_minutes(minutes)

    reports = []
    for svc in services:
        try:
            logs = await container.monitoring.query_logs(
                service=svc, severity="DEFAULT", time_range=time_range
            )
            error_logs = [l for l in logs if l.severity.value in ("ERROR", "CRITICAL")]

            if error_logs:
                alert = Alert.from_dict({
                    "service": svc,
                    "severity": "high",
                    "message": f"Auto-detected {len(error_logs)} errors in last {minutes}min",
                })
                report = await analysis.analyze_incident(alert)
                reports.append(report.to_dict())
        except Exception as e:
            logger.warning("analyze_error", extra={"service": svc, "error": str(e)})

    return {"analyzed": len(services), "incidents_found": len(reports), "reports": reports}
