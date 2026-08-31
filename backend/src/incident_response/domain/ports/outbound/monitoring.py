from abc import ABC, abstractmethod

from incident_response.domain.value_objects.log_entry import LogEntry
from incident_response.domain.value_objects.metric_result import MetricResult
from incident_response.domain.value_objects.time_range import TimeRange


class MonitoringPort(ABC):
    """Port: what the domain needs from a monitoring/logging system."""

    @abstractmethod
    async def fetch_metrics(
        self,
        service: str,
        metric_types: list[str],
        time_range: TimeRange,
    ) -> MetricResult:
        """Fetch metrics for a service. Returns typed MetricResult."""
        ...

    @abstractmethod
    async def query_logs(
        self,
        service: str,
        severity: str,
        time_range: TimeRange,
    ) -> list[LogEntry]:
        """Query logs for a service. Returns typed LogEntry list."""
        ...
