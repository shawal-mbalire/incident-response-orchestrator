from incident_response.domain.models.alert import Alert
from incident_response.domain.models.incident import Incident
from incident_response.domain.models.report import IncidentReport
from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.ports.outbound.notifications import NotificationPort
from incident_response.domain.ports.outbound.state_store import StateStorePort


class IncidentService:
    """Core business logic. Knows only ports -- never concrete adapters.

    Dependencies are injected through the constructor (dependency inversion).
    """

    def __init__(
        self,
        monitoring: MonitoringPort,
        deployments: DeploymentPort,
        notifications: NotificationPort,
        state_store: StateStorePort | None = None,
    ) -> None:
        self._monitoring = monitoring
        self._deployments = deployments
        self._notifications = notifications
        self._state_store = state_store
        self._reports: dict[str, IncidentReport] = {}

    async def analyze_incident(self, alert: Alert) -> IncidentReport:
        """Analyze an alert and produce an incident report."""
        incident = Incident.from_alert(
            alert_id=alert.id,
            service=alert.service,
            title=f"Incident: {alert.message}",
        )

        # Gather data from all sources in parallel
        log_data = await self._monitoring.query_logs(
            service=alert.service,
            severity="ERROR",
            minutes=30,
        )
        metric_data = await self._monitoring.fetch_metrics(
            service=alert.service,
            metric_types=["error_rate", "latency_p99", "cpu", "memory"],
            minutes=30,
        )
        deploy_data = await self._deployments.get_recent_deploys(
            service=alert.service,
            hours=24,
        )

        # Build the report
        report = IncidentReport(
            incident_id=incident.id,
            executive_summary=self._build_summary(alert, log_data, metric_data, deploy_data),
            timeline=self._build_timeline(alert, deploy_data, log_data),
            root_cause=self._infer_root_cause(alert, log_data, metric_data, deploy_data),
            confidence=self._assess_confidence(log_data, metric_data, deploy_data),
            impact_assessment=self._assess_impact(alert, metric_data),
            recommended_actions=self._recommend_actions(alert, log_data, deploy_data),
            supporting_evidence={
                "logs": log_data[:10],
                "metrics": metric_data,
                "deployments": deploy_data,
                "alert": alert.to_dict(),
            },
        )

        # Persist to state store (primary), cache in memory
        if self._state_store:
            await self._state_store.save("incidents", incident.id, report.to_dict())
        self._reports[incident.id] = report

        return report

    async def get_report(self, incident_id: str) -> IncidentReport | None:
        # Check in-memory cache first
        if incident_id in self._reports:
            return self._reports[incident_id]

        # Load from state store
        if self._state_store:
            data = await self._state_store.load("incidents", incident_id)
            if data:
                report = IncidentReport(
                    incident_id=data["incident_id"],
                    executive_summary=data.get("executive_summary", ""),
                    timeline=data.get("timeline", []),
                    root_cause=data.get("root_cause", ""),
                    confidence=data.get("confidence", "low"),
                    impact_assessment=data.get("impact_assessment", ""),
                    recommended_actions=data.get("recommended_actions", []),
                    supporting_evidence=data.get("supporting_evidence", {}),
                )
                self._reports[incident_id] = report
                return report

        return None

    def _build_summary(
        self, alert: Alert, logs: list, metrics: dict, deploys: list
    ) -> str:
        error_count = sum(1 for log in logs if log.get("severity") == "ERROR")
        recent_deploy = deploys[0] if deploys else None
        deploy_info = f" (deployed {recent_deploy.get('version', 'unknown')} recently)" if recent_deploy else ""

        return (
            f"Alert triggered for {alert.service}: {alert.message}. "
            f"Found {error_count} error logs. "
            f"Metrics show error rate at {metrics.get('error_rate', 'N/A')}%.{deploy_info}"
        )

    def _build_timeline(self, alert: Alert, deploys: list, logs: list) -> list[dict]:
        timeline = [
            {"time": alert.timestamp.isoformat(), "event": f"Alert triggered: {alert.message}"},
        ]

        for deploy in deploys[:3]:
            timeline.append({
                "time": deploy.get("timestamp", "N/A"),
                "event": f"Deployment: {deploy.get('version', 'unknown')} - {deploy.get('message', '')}",
            })

        error_logs = [log for log in logs if log.get("severity") == "ERROR"][:5]
        for log in error_logs:
            timeline.append({
                "time": log.get("timestamp", "N/A"),
                "event": f"Error: {log.get('message', 'Unknown error')}",
            })

        timeline.sort(key=lambda x: x.get("time", ""))
        return timeline

    def _infer_root_cause(
        self, alert: Alert, logs: list, metrics: dict, deploys: list
    ) -> str:
        has_recent_deploy = len(deploys) > 0
        error_patterns = self._extract_error_patterns(logs)

        if has_recent_deploy and error_patterns:
            return (
                f"Likely caused by recent deployment {deploys[0].get('version', 'unknown')}. "
                f"Error pattern: {error_patterns[0]}. "
                f"Recommend rolling back to previous version."
            )
        elif error_patterns:
            return f"Error pattern detected: {error_patterns[0]}. Requires further investigation."
        else:
            return "Unable to determine root cause from available data. Manual investigation required."

    def _extract_error_patterns(self, logs: list) -> list[str]:
        error_messages = [log.get("message", "") for log in logs if log.get("severity") == "ERROR"]
        patterns = []
        for msg in error_messages[:5]:
            if msg and msg not in patterns:
                patterns.append(msg)
        return patterns

    def _assess_confidence(self, logs: list, metrics: dict, deploys: list) -> str:
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
            return "high"
        elif score >= 2:
            return "medium"
        return "low"

    def _assess_impact(self, alert: Alert, metrics: dict) -> str:
        severity = alert.severity.value
        error_rate_data = metrics.get("error_rate", {})
        error_rate = error_rate_data.get("current", 0) if isinstance(error_rate_data, dict) else 0

        if severity == "critical" or error_rate > 10:
            return "Critical impact - production service degraded, immediate action required."
        elif severity == "high" or error_rate > 5:
            return "High impact - significant service degradation affecting users."
        else:
            return "Moderate impact - service experiencing issues but may be recoverable."

    def _recommend_actions(
        self, alert: Alert, logs: list, deploys: list
    ) -> list[str]:
        actions = []

        if deploys:
            actions.append(f"Consider rolling back deployment {deploys[0].get('version', 'unknown')}")
        
        actions.append("Monitor error rates for next 30 minutes")
        actions.append("Review related services for cascading effects")
        
        if alert.severity.value in ("critical", "high"):
            actions.append("Notify stakeholders of incident status")
            actions.append("Create postmortem document for review")

        return actions
