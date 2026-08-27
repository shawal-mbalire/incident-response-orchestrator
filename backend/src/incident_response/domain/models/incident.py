from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class IncidentStatus(Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


@dataclass
class Incident:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    service: str = ""
    title: str = ""
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None
    root_cause: str = ""
    confidence: str = "low"

    @classmethod
    def from_alert(cls, alert_id: str, service: str, title: str) -> "Incident":
        return cls(
            alert_id=alert_id,
            service=service,
            title=title,
        )

    def resolve(self, root_cause: str = "", confidence: str = "medium") -> None:
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.root_cause = root_cause
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "service": self.service,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "root_cause": self.root_cause,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Incident":
        return cls(
            id=data["id"],
            alert_id=data.get("alert_id", ""),
            service=data["service"],
            title=data["title"],
            status=IncidentStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            resolved_at=(
                datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None
            ),
            root_cause=data.get("root_cause", ""),
            confidence=data.get("confidence", "low"),
        )
