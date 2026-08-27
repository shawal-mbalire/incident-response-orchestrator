from abc import ABC, abstractmethod
from typing import Any


class MonitoringPort(ABC):
    """Port: what the domain needs from a monitoring/logging system."""

    @abstractmethod
    async def fetch_metrics(
        self,
        service: str,
        metric_types: list[str],
        minutes: int = 30,
    ) -> dict[str, Any]:
        """Fetch metrics for a service from Cloud Monitoring."""
        ...

    @abstractmethod
    async def query_logs(
        self,
        service: str,
        severity: str = "ERROR",
        minutes: int = 30,
    ) -> list[dict]:
        """Query logs for a service from Cloud Logging."""
        ...
