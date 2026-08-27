from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Alert:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service: str = ""
    severity: Severity = Severity.HIGH
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            service=data["service"],
            severity=Severity(data.get("severity", "high")),
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(timezone.utc),
            metrics=data.get("metrics", {}),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "service": self.service,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
        }
