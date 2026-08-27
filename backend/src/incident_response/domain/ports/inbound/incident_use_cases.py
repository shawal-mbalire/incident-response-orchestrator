from abc import ABC, abstractmethod

from incident_response.domain.models.alert import Alert
from incident_response.domain.models.report import IncidentReport


class AnalyzeIncidentUseCase(ABC):
    """Inbound port: what the outside world can ask the domain to do."""

    @abstractmethod
    async def analyze_incident(self, alert: Alert) -> IncidentReport:
        """Analyze an alert and produce an incident report."""
        ...

    @abstractmethod
    async def get_report(self, incident_id: str) -> IncidentReport | None:
        """Retrieve a previously generated report."""
        ...
