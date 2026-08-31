from dataclasses import dataclass, field
from datetime import UTC, datetime

from incident_response.domain.value_objects.severity import Severity


@dataclass(frozen=True)
class LogEntry:
    """Immutable log entry from a logging system."""

    timestamp: datetime
    severity: Severity
    message: str
    labels: dict[str, str] = field(default_factory=dict)
    trace: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "LogEntry":
        """Create from a raw dict (adapter output)."""
        ts = data.get("timestamp")
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now(UTC)

        return cls(
            timestamp=dt,
            severity=Severity.from_string(data.get("severity", "INFO")),
            message=data.get("message", ""),
            labels=dict(data.get("labels", {})),
            trace=data.get("trace"),
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "message": self.message,
            "labels": self.labels,
            "trace": self.trace,
        }
