from dataclasses import dataclass

from incident_response.domain.events.base import DomainEvent
from incident_response.domain.value_objects.confidence import Confidence
from incident_response.domain.value_objects.severity import Severity


@dataclass(frozen=True)
class IncidentCreated(DomainEvent):
    """Fired when a new incident is created from an alert."""

    incident_id: str = ""
    alert_id: str = ""
    service: str = ""
    severity: Severity = Severity.HIGH

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            incident_id=self.incident_id,
            alert_id=self.alert_id,
            service=self.service,
            severity=self.severity.value,
        )
        return base


@dataclass(frozen=True)
class IncidentAnalyzed(DomainEvent):
    """Fired when incident analysis completes."""

    incident_id: str = ""
    confidence: Confidence = Confidence.LOW
    has_root_cause: bool = False
    log_count: int = 0
    metric_count: int = 0
    deploy_count: int = 0

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            incident_id=self.incident_id,
            confidence=self.confidence.value,
            has_root_cause=self.has_root_cause,
            log_count=self.log_count,
            metric_count=self.metric_count,
            deploy_count=self.deploy_count,
        )
        return base


@dataclass(frozen=True)
class RootCauseIdentified(DomainEvent):
    """Fired when a root cause is identified."""

    incident_id: str = ""
    root_cause: str = ""
    confidence: Confidence = Confidence.LOW

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            incident_id=self.incident_id,
            root_cause=self.root_cause,
            confidence=self.confidence.value,
        )
        return base


@dataclass(frozen=True)
class IncidentResolved(DomainEvent):
    """Fired when an incident is resolved."""

    incident_id: str = ""
    resolution_time_seconds: float = 0.0

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            incident_id=self.incident_id,
            resolution_time_seconds=self.resolution_time_seconds,
        )
        return base
