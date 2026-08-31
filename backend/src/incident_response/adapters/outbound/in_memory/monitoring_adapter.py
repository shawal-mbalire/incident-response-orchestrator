from datetime import UTC, datetime, timedelta

from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.value_objects.log_entry import LogEntry
from incident_response.domain.value_objects.metric_result import MetricResult, MetricValue
from incident_response.domain.value_objects.severity import Severity
from incident_response.domain.value_objects.time_range import TimeRange

_SEVERITY_LEVELS: dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class InMemoryMonitoringAdapter(MonitoringPort):
    """Outbound adapter: in-memory mock for testing and local dev."""

    def __init__(self) -> None:
        self._logs: list[LogEntry] = []
        self._metrics: dict[str, dict[str, MetricValue]] = {}

    def seed_logs(self, service: str, count: int = 20) -> None:
        now = datetime.now(UTC)
        error_messages = [
            "ConnectionError: Failed to connect to database - timeout after 30s",
            "NullPointerException: User session expired during request processing",
            "HTTP 503: Upstream service unavailable - payment-gateway timeout",
            "MemoryError: Heap space exhausted - current usage 98%",
            "TimeoutError: Request to external API exceeded 10s deadline",
            "ValueError: Invalid JSON payload received from client",
            "RuntimeError: Connection pool exhausted - all 50 connections in use",
            "IOError: Failed to write to disk - no space left on device",
        ]
        for i in range(count):
            severity = (
                Severity.CRITICAL if i % 5 == 0
                else Severity.HIGH if i % 3 == 0
                else Severity.MEDIUM if i % 2 == 0
                else Severity.LOW
            )
            message = (
                error_messages[i % len(error_messages)]
                if severity.numeric >= 3
                else f"Sample log entry {i} for {service}"
            )
            self._logs.append(
                LogEntry(
                    timestamp=now - timedelta(minutes=i),
                    severity=severity,
                    message=message,
                    labels={"service": service},
                    trace=f"trace-{i}",
                )
            )

    def seed_metrics(self, service: str) -> None:
        import random

        self._metrics[service] = {
            "error_rate": MetricValue(
                current=round(random.uniform(0.5, 15.0), 2),
                values=[round(random.uniform(0.5, 15.0), 2) for _ in range(10)],
                unit="percent",
            ),
            "latency_p99": MetricValue(
                current=round(random.uniform(100, 3000), 0),
                values=[round(random.uniform(100, 3000), 0) for _ in range(10)],
                unit="ms",
            ),
            "cpu": MetricValue(
                current=round(random.uniform(30, 95), 1),
                values=[round(random.uniform(30, 95), 1) for _ in range(10)],
                unit="percent",
            ),
            "memory": MetricValue(
                current=round(random.uniform(40, 85), 1),
                values=[round(random.uniform(40, 85), 1) for _ in range(10)],
                unit="percent",
            ),
        }

    async def fetch_metrics(
        self,
        service: str,
        metric_types: list[str],
        time_range: TimeRange,
    ) -> MetricResult:
        if service not in self._metrics:
            self.seed_metrics(service)

        return MetricResult(
            metrics={
                mt: self._metrics[service].get(
                    mt, MetricValue(current=0, values=[], unit="count")
                )
                for mt in metric_types
            }
        )

    async def query_logs(
        self,
        service: str,
        severity: str,
        time_range: TimeRange,
    ) -> list[LogEntry]:
        if not self._logs:
            self.seed_logs(service)

        min_level = _SEVERITY_LEVELS.get(severity.upper(), 0)
        return [
            log
            for log in self._logs
            if log.labels.get("service") == service
            and _SEVERITY_LEVELS.get(log.severity.value, 0) >= min_level
            and log.timestamp >= time_range.start
        ]
