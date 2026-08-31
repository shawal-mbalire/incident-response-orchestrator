import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from incident_response.domain.exceptions import ValidationError
from incident_response.domain.value_objects.confidence import Confidence
from incident_response.domain.value_objects.correlation_id import CorrelationId


class IncidentStatus(Enum):
    """Incident lifecycle states with valid transitions."""

    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"

    def can_transition_to(self, new_status: "IncidentStatus") -> bool:
        """Check if transition to new_status is valid."""
        _valid_transitions = {
            IncidentStatus.INVESTIGATING: {IncidentStatus.IDENTIFIED},
            IncidentStatus.IDENTIFIED: {IncidentStatus.MONITORING, IncidentStatus.RESOLVED},
            IncidentStatus.MONITORING: {IncidentStatus.RESOLVED, IncidentStatus.INVESTIGATING},
            IncidentStatus.RESOLVED: set(),  # Terminal state
        }
        return new_status in _valid_transitions.get(self, set())


@dataclass
class Incident:
    """Domain model for an incident with state machine behavior."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    service: str = ""
    title: str = ""
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    root_cause: str = ""
    confidence: Confidence = Confidence.LOW
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)

    @classmethod
    def from_alert(
        cls,
        alert_id: str,
        service: str,
        title: str,
        correlation_id: CorrelationId | None = None,
    ) -> "Incident":
        return cls(
            alert_id=alert_id,
            service=service,
            title=title,
            correlation_id=correlation_id or CorrelationId.generate(),
        )

    def update_status(self, new_status: IncidentStatus) -> None:
        """Transition to a new status with validation."""
        if not self.status.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot transition from {self.status.value} to {new_status.value}",
                field="status",
            )
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def resolve(self, root_cause: str = "", confidence: str = "medium") -> None:
        """Resolve the incident."""
        if self.status == IncidentStatus.RESOLVED:
            raise ValidationError("Incident is already resolved", field="status")
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.root_cause = root_cause
        self.confidence = Confidence.from_string(confidence)

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
            "confidence": self.confidence.value,
            "correlation_id": str(self.correlation_id),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Incident":
        corr_id = data.get("correlation_id")
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
            confidence=Confidence.from_string(data.get("confidence", "low")),
            correlation_id=(
                CorrelationId.from_string(corr_id)
                if corr_id
                else CorrelationId.generate()
            ),
        )
