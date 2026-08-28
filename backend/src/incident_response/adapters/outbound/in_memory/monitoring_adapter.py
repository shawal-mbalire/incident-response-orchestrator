from datetime import datetime, timedelta, timezone

from incident_response.domain.ports.outbound.monitoring import MonitoringPort

_SEVERITY_LEVELS: dict[str, int] = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4,
}


class InMemoryMonitoringAdapter(MonitoringPort):
    """Outbound adapter: in-memory mock for testing and local dev."""

    def __init__(self) -> None:
        self._logs: list[dict] = []
        self._metrics: dict[str, dict] = {}

    def seed_logs(self, service: str, count: int = 20) -> None:
        now = datetime.now(timezone.utc)
        for i in range(count):
            self._logs.append({
                "timestamp": (now - timedelta(minutes=i)).isoformat(),
                "severity": "ERROR" if i % 3 == 0 else "WARNING" if i % 2 == 0 else "INFO",
                "message": f"Sample log entry {i} for {service}",
                "labels": {"service": service},
                "trace": f"trace-{i}",
            })

    def seed_metrics(self, service: str) -> None:
        import random

        self._metrics[service] = {
            "error_rate": {
                "current": round(random.uniform(0.5, 15.0), 2),
                "values": [round(random.uniform(0.5, 15.0), 2) for _ in range(10)],
                "unit": "percent",
            },
            "latency_p99": {
                "current": round(random.uniform(100, 3000), 0),
                "values": [round(random.uniform(100, 3000), 0) for _ in range(10)],
                "unit": "ms",
            },
            "cpu": {
                "current": round(random.uniform(30, 95), 1),
                "values": [round(random.uniform(30, 95), 1) for _ in range(10)],
                "unit": "percent",
            },
            "memory": {
                "current": round(random.uniform(40, 85), 1),
                "values": [round(random.uniform(40, 85), 1) for _ in range(10)],
                "unit": "percent",
            },
        }

    async def fetch_metrics(
        self,
        service: str,
        metric_types: list[str],
        minutes: int = 30,
    ) -> dict:
        if service not in self._metrics:
            self.seed_metrics(service)

        return {
            mt: self._metrics[service].get(mt, {"current": 0, "values": [], "unit": "count"})
            for mt in metric_types
        }

    async def query_logs(
        self,
        service: str,
        severity: str = "ERROR",
        minutes: int = 30,
    ) -> list[dict]:
        if not self._logs:
            self.seed_logs(service)

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        min_level = _SEVERITY_LEVELS.get(severity.upper(), 0)
        return [
            log
            for log in self._logs
            if log["labels"].get("service") == service
            and _SEVERITY_LEVELS.get(log["severity"], 0) >= min_level
            and datetime.fromisoformat(log["timestamp"]).replace(tzinfo=timezone.utc) >= cutoff
        ]
