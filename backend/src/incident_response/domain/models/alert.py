import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from incident_response.domain.exceptions import ValidationError
from incident_response.domain.value_objects.correlation_id import CorrelationId
from incident_response.domain.value_objects.severity import Severity


@dataclass
class Alert:
    """Domain model for an incoming alert with validation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service: str = ""
    severity: Severity = Severity.HIGH
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metrics: dict = field(default_factory=dict)
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)

    def __post_init__(self) -> None:
        if not self.service or not self.service.strip():
            raise ValidationError("Service name is required", field="service")
        if not self.message or not self.message.strip():
            raise ValidationError("Alert message is required", field="message")

    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        """Create from dict with validation."""
        service = data.get("service", "")
        message = data.get("message", "")

        if not service.strip():
            raise ValidationError("Service name is required", field="service")
        if not message.strip():
            raise ValidationError("Alert message is required", field="message")

        severity_str = data.get("severity", "high")
        severity = Severity.from_string(severity_str)

        ts = data.get("timestamp")
        if isinstance(ts, str):
            timestamp = datetime.fromisoformat(ts)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
        else:
            timestamp = datetime.now(UTC)

        corr_id = data.get("correlation_id")
        correlation_id = (
            CorrelationId.from_string(corr_id) if corr_id else CorrelationId.generate()
        )

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            service=service,
            severity=severity,
            message=message,
            timestamp=timestamp,
            metrics=data.get("metrics", {}),
            correlation_id=correlation_id,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "service": self.service,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "correlation_id": str(self.correlation_id),
        }
