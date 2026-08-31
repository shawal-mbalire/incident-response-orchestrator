from abc import ABC, abstractmethod

from incident_response.domain.models.alert import Alert
from incident_response.domain.models.report import IncidentReport
from incident_response.domain.value_objects.correlation_id import CorrelationId


class IncidentAnalysisPort(ABC):
    """Inbound port: use case interface for incident analysis."""

    @abstractmethod
    async def analyze_incident(
        self,
        alert: Alert,
        correlation_id: CorrelationId | None = None,
    ) -> IncidentReport:
        """Analyze an alert and produce an incident report."""
        ...

    @abstractmethod
    async def get_report(self, incident_id: str) -> IncidentReport | None:
        """Retrieve an existing incident report by ID."""
        ...

    @abstractmethod
    async def list_incidents(
        self,
        service: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List incidents, optionally filtered by service."""
        ...

    @abstractmethod
    async def fetch_service_metrics(
        self,
        service: str,
        metric_types: str,
        minutes: int = 30,
    ) -> dict:
        """Fetch metrics for a service (used by toolsets)."""
        ...

    @abstractmethod
    async def query_service_logs(
        self,
        service: str,
        severity: str = "ERROR",
        minutes: int = 30,
    ) -> dict:
        """Query logs for a service (used by toolsets)."""
        ...

    @abstractmethod
    async def get_recent_deploys(
        self,
        service: str,
        hours: int = 24,
    ) -> dict:
        """Get recent deployments for a service (used by toolsets)."""
        ...
