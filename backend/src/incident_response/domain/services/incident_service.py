import logging
from collections import OrderedDict

from incident_response.domain.events.incident_events import (
    IncidentAnalyzed,
    IncidentCreated,
    RootCauseIdentified,
)
from incident_response.domain.models.alert import Alert
from incident_response.domain.models.incident import Incident
from incident_response.domain.models.report import IncidentReport
from incident_response.domain.ports.inbound.analysis import IncidentAnalysisPort
from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.ports.outbound.events import EventPublisherPort
from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.ports.outbound.notifications import NotificationPort
from incident_response.domain.ports.outbound.state_store import StateStorePort
from incident_response.domain.value_objects.confidence import Confidence
from incident_response.domain.value_objects.correlation_id import CorrelationId
from incident_response.domain.value_objects.deploy_info import DeployInfo
from incident_response.domain.value_objects.log_entry import LogEntry
from incident_response.domain.value_objects.metric_result import MetricResult
from incident_response.domain.value_objects.time_range import TimeRange

logger = logging.getLogger(__name__)


class IncidentService(IncidentAnalysisPort):
    """Core business logic implementing the incident analysis use case.

    Knows only ports -- never concrete adapters.
    Dependencies are injected through the constructor (dependency inversion).
    """

    def __init__(
        self,
        monitoring: MonitoringPort,
        deployments: DeploymentPort,
        notifications: NotificationPort,
        state_store: StateStorePort | None = None,
        event_publisher: EventPublisherPort | None = None,
        max_cache_size: int = 1000,
    ) -> None:
        self._monitoring = monitoring
        self._deployments = deployments
        self._notifications = notifications
        self._state_store = state_store
        self._event_publisher = event_publisher
        self._max_cache_size = max_cache_size
        self._reports: OrderedDict[str, IncidentReport] = OrderedDict()

    async def analyze_incident(
        self,
        alert: Alert,
        correlation_id: CorrelationId | None = None,
    ) -> IncidentReport:
        """Analyze an alert and produce an incident report."""
        correlation_id = correlation_id or alert.correlation_id

        logger.info(
            "analyzing_incident",
            extra={
                "correlation_id": str(correlation_id),
                "service": alert.service,
                "severity": alert.severity.value,
            },
        )

        incident = Incident.from_alert(
            alert_id=alert.id,
            service=alert.service,
            title=f"Incident: {alert.message}",
            correlation_id=correlation_id,
        )

        await self._publish_event(
            IncidentCreated(
                incident_id=incident.id,
                alert_id=alert.id,
                service=alert.service,
                severity=alert.severity,
                correlation_id=correlation_id,
            )
        )

        time_range = TimeRange.last_minutes(30)

        log_entries = await self._monitoring.query_logs(
            service=alert.service,
            severity="ERROR",
            time_range=time_range,
        )
        metric_result = await self._monitoring.fetch_metrics(
            service=alert.service,
            metric_types=["error_rate", "latency_p99", "cpu", "memory"],
            time_range=time_range,
        )
        deploy_entries = await self._deployments.get_recent_deploys(
            service=alert.service,
            time_range=TimeRange.last_hours(24),
        )

        log_data = [entry.to_dict() for entry in log_entries]
        metric_data = metric_result.to_dict()
        deploy_data = [deploy.to_dict() for deploy in deploy_entries]

        confidence = self._assess_confidence(log_entries, metric_result, deploy_entries)
        root_cause = self._infer_root_cause(alert, log_entries, metric_result, deploy_entries)

        report = IncidentReport(
            incident_id=incident.id,
            executive_summary=self._build_summary(
                alert, log_entries, metric_result, deploy_entries
            ),
            timeline=self._build_timeline(alert, deploy_entries, log_entries),
            root_cause=root_cause,
            confidence=confidence,
            impact_assessment=self._assess_impact(alert, metric_result),
            recommended_actions=self._recommend_actions(
                alert, log_entries, deploy_entries
            ),
            supporting_evidence={
                "logs": log_data[:10],
                "metrics": metric_data,
                "deployments": deploy_data,
                "alert": alert.to_dict(),
            },
            correlation_id=correlation_id,
        )

        await self._publish_event(
            IncidentAnalyzed(
                incident_id=incident.id,
                confidence=confidence,
                has_root_cause=bool(root_cause),
                log_count=len(log_entries),
                metric_count=len(metric_result.metrics),
                deploy_count=len(deploy_entries),
                correlation_id=correlation_id,
            )
        )

        if root_cause:
            await self._publish_event(
                RootCauseIdentified(
                    incident_id=incident.id,
                    root_cause=root_cause,
                    confidence=confidence,
                    correlation_id=correlation_id,
                )
            )

        if self._state_store:
            await self._state_store.save("incidents", incident.id, report.to_dict())

        self._reports[incident.id] = report
        self._evict_cache_if_needed()

        logger.info(
            "incident_analyzed",
            extra={
                "correlation_id": str(correlation_id),
                "incident_id": incident.id,
                "confidence": confidence.value,
            },
        )

        return report

    async def get_report(self, incident_id: str) -> IncidentReport | None:
        if incident_id in self._reports:
            self._reports.move_to_end(incident_id)
            return self._reports[incident_id]

        if self._state_store:
            data = await self._state_store.load("incidents", incident_id)
            if data:
                report = IncidentReport.from_dict(data)
                self._reports[incident_id] = report
                self._evict_cache_if_needed()
                return report

        return None

    async def list_incidents(
        self,
        service: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        if self._state_store:
            incidents = await self._state_store.list_collection("incidents", limit=limit)
            if service:
                incidents = [i for i in incidents if i.get("service") == service]
            return incidents
        return []

    async def fetch_service_metrics(
        self,
        service: str,
        metric_types: str,
        minutes: int = 30,
    ) -> dict:
        types = [t.strip() for t in metric_types.split(",")]
        time_range = TimeRange.last_minutes(minutes)
        result = await self._monitoring.fetch_metrics(service, types, time_range)
        return {"status": "success", "service": service, "metrics": result.to_dict()}

    async def query_service_logs(
        self,
        service: str,
        severity: str = "ERROR",
        minutes: int = 30,
    ) -> dict:
        time_range = TimeRange.last_minutes(minutes)
        logs = await self._monitoring.query_logs(service, severity, time_range)
        return {
            "status": "success",
            "service": service,
            "severity": severity,
            "logs": [entry.to_dict() for entry in logs],
            "count": len(logs),
        }

    async def get_recent_deploys(
        self,
        service: str,
        hours: int = 24,
    ) -> dict:
        time_range = TimeRange.last_hours(hours)
        deploys = await self._deployments.get_recent_deploys(service, time_range)
        return {
            "status": "success",
            "service": service,
            "hours": hours,
            "deployments": [d.to_dict() for d in deploys],
            "count": len(deploys),
        }

    def _evict_cache_if_needed(self) -> None:
        while len(self._reports) > self._max_cache_size:
            self._reports.popitem(last=False)

    async def _publish_event(self, event: object) -> None:
        if self._event_publisher:
            try:
                await self._event_publisher.publish(event)  # type: ignore[arg-type]
            except Exception:
                logger.warning("failed_to_publish_event", exc_info=True)

    def _build_summary(
        self,
        alert: Alert,
        logs: list[LogEntry],
        metrics: MetricResult,
        deploys: list[DeployInfo],
    ) -> str:
        error_count = sum(1 for log in logs if log.severity.value == "ERROR")
        recent_deploy = deploys[0] if deploys else None
        deploy_info = (
            f" (deployed {recent_deploy.version} recently)" if recent_deploy else ""
        )
        error_rate = metrics.get_current("error_rate", 0)

        return (
            f"Alert triggered for {alert.service}: {alert.message}. "
            f"Found {error_count} error logs. "
            f"Metrics show error rate at {error_rate}%.{deploy_info}"
        )

    def _build_timeline(
        self,
        alert: Alert,
        deploys: list[DeployInfo],
        logs: list[LogEntry],
    ) -> list[dict]:
        timeline = [
            {"time": alert.timestamp.isoformat(), "event": f"Alert triggered: {alert.message}"},
        ]

        for deploy in deploys[:3]:
            timeline.append({
                "time": deploy.timestamp.isoformat(),
                "event": f"Deployment: {deploy.version} - {deploy.message}",
            })

        error_logs = [log for log in logs if log.severity.value == "ERROR"][:5]
        for log in error_logs:
            timeline.append({
                "time": log.timestamp.isoformat(),
                "event": f"Error: {log.message}",
            })

        timeline.sort(key=lambda x: x.get("time", ""))
        return timeline

    def _infer_root_cause(
        self,
        alert: Alert,
        logs: list[LogEntry],
        metrics: MetricResult,
        deploys: list[DeployInfo],
    ) -> str:
        has_recent_deploy = len(deploys) > 0
        error_patterns = self._extract_error_patterns(logs)

        if has_recent_deploy and error_patterns:
            return (
                f"Likely caused by recent deployment {deploys[0].version}. "
                f"Error pattern: {error_patterns[0]}. "
                f"Recommend rolling back to previous version."
            )
        elif error_patterns:
            return (
                f"Error pattern detected: {error_patterns[0]}. "
                f"Requires further investigation."
            )
        else:
            return (
                "Unable to determine root cause from available data. "
                "Manual investigation required."
            )

    def _extract_error_patterns(self, logs: list[LogEntry]) -> list[str]:
        error_messages = [log.message for log in logs if log.severity.value == "ERROR"]
        patterns: list[str] = []
        for msg in error_messages[:5]:
            if msg and msg not in patterns:
                patterns.append(msg)
        return patterns

    def _assess_confidence(
        self,
        logs: list[LogEntry],
        metrics: MetricResult,
        deploys: list[DeployInfo],
    ) -> Confidence:
        score = 0
        if logs:
            score += 1
        if metrics.get("error_rate"):
            score += 1
        if deploys:
            score += 1
        if len(logs) > 5:
            score += 1

        if score >= 3:
            return Confidence.HIGH
        elif score >= 2:
            return Confidence.MEDIUM
        return Confidence.LOW

    def _assess_impact(self, alert: Alert, metrics: MetricResult) -> str:
        severity = alert.severity
        error_rate = metrics.get_current("error_rate", 0)

        if severity.is_critical() or error_rate > 10:
            return "Critical impact - production service degraded, immediate action required."
        elif severity.is_high_or_above() or error_rate > 5:
            return "High impact - significant service degradation affecting users."
        else:
            return "Moderate impact - service experiencing issues but may be recoverable."

    def _recommend_actions(
        self,
        alert: Alert,
        logs: list[LogEntry],
        deploys: list[DeployInfo],
    ) -> list[str]:
        actions: list[str] = []

        if deploys:
            actions.append(f"Consider rolling back deployment {deploys[0].version}")

        actions.append("Monitor error rates for next 30 minutes")
        actions.append("Review related services for cascading effects")

        if alert.severity.is_high_or_above():
            actions.append("Notify stakeholders of incident status")
            actions.append("Create postmortem document for review")

        return actions
