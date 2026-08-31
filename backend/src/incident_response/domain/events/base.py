import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from incident_response.domain.value_objects.correlation_id import CorrelationId


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "correlation_id": str(self.correlation_id),
        }
