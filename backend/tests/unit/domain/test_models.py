import pytest

from incident_response.domain.exceptions import ValidationError
from incident_response.domain.models.alert import Alert
from incident_response.domain.models.incident import Incident, IncidentStatus
from incident_response.domain.models.report import IncidentReport
from incident_response.domain.value_objects.confidence import Confidence
from incident_response.domain.value_objects.correlation_id import CorrelationId
from incident_response.domain.value_objects.severity import Severity


class TestAlert:
    def test_create_alert(self):
        alert = Alert(
            service="api-gateway",
            severity=Severity.HIGH,
            message="High error rate detected",
        )
        assert alert.service == "api-gateway"
        assert alert.severity == Severity.HIGH
        assert alert.id is not None
        assert alert.correlation_id is not None

    def test_alert_from_dict(self):
        data = {
            "service": "user-service",
            "severity": "critical",
            "message": "Service unavailable",
            "timestamp": "2026-08-27T14:30:00Z",
        }
        alert = Alert.from_dict(data)
        assert alert.service == "user-service"
        assert alert.severity == Severity.CRITICAL

    def test_alert_to_dict(self):
        alert = Alert(service="test", severity=Severity.LOW, message="test message")
        d = alert.to_dict()
        assert d["service"] == "test"
        assert d["severity"] == "low"
        assert "correlation_id" in d

    def test_alert_validation_empty_service(self):
        with pytest.raises(ValidationError) as exc_info:
            Alert(service="", severity=Severity.HIGH, message="test")
        assert exc_info.value.field == "service"

    def test_alert_validation_empty_message(self):
        with pytest.raises(ValidationError) as exc_info:
            Alert(service="test", severity=Severity.HIGH, message="")
        assert exc_info.value.field == "message"


class TestIncident:
    def test_create_from_alert(self):
        incident = Incident.from_alert(
            alert_id="alert-123",
            service="api-gateway",
            title="High error rate",
        )
        assert incident.alert_id == "alert-123"
        assert incident.status == IncidentStatus.INVESTIGATING
        assert incident.correlation_id is not None

    def test_resolve_incident(self):
        incident = Incident(service="test", title="test")
        incident.resolve(root_cause="Fixed", confidence="high")
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolved_at is not None
        assert incident.root_cause == "Fixed"
        assert incident.confidence == Confidence.HIGH

    def test_resolve_already_resolved(self):
        incident = Incident(service="test", title="test")
        incident.resolve(root_cause="Fixed", confidence="high")
        with pytest.raises(ValidationError):
            incident.resolve(root_cause="Fixed again", confidence="high")

    def test_status_transition(self):
        incident = Incident(service="test", title="test")
        incident.update_status(IncidentStatus.IDENTIFIED)
        assert incident.status == IncidentStatus.IDENTIFIED

    def test_invalid_status_transition(self):
        incident = Incident(service="test", title="test")
        with pytest.raises(ValidationError):
            incident.update_status(IncidentStatus.RESOLVED)


class TestIncidentReport:
    def test_to_markdown(self):
        report = IncidentReport(
            incident_id="inc-123",
            executive_summary="Test summary",
            root_cause="Test root cause",
            confidence=Confidence.HIGH,
            recommended_actions=["Action 1", "Action 2"],
        )
        md = report.to_markdown()
        assert "inc-123" in md
        assert "Test summary" in md
        assert "Action 1" in md

    def test_to_dict(self):
        report = IncidentReport(
            incident_id="inc-123",
            executive_summary="Test",
            confidence=Confidence.MEDIUM,
        )
        d = report.to_dict()
        assert d["incident_id"] == "inc-123"
        assert d["confidence"] == "medium"
        assert "correlation_id" in d

    def test_from_dict(self):
        data = {
            "incident_id": "inc-123",
            "executive_summary": "Test",
            "confidence": "high",
            "correlation_id": "test-corr",
        }
        report = IncidentReport.from_dict(data)
        assert report.incident_id == "inc-123"
        assert report.confidence == Confidence.HIGH
        assert str(report.correlation_id) == "test-corr"


class TestSeverity:
    def test_ordering(self):
        assert Severity.CRITICAL > Severity.HIGH
        assert Severity.HIGH > Severity.MEDIUM
        assert Severity.MEDIUM > Severity.LOW

    def test_is_critical(self):
        assert Severity.CRITICAL.is_critical()
        assert not Severity.HIGH.is_critical()

    def test_is_high_or_above(self):
        assert Severity.CRITICAL.is_high_or_above()
        assert Severity.HIGH.is_high_or_above()
        assert not Severity.MEDIUM.is_high_or_above()

    def test_from_string(self):
        assert Severity.from_string("critical") == Severity.CRITICAL
        assert Severity.from_string("HIGH") == Severity.HIGH
        with pytest.raises(ValueError):
            Severity.from_string("invalid")


class TestConfidence:
    def test_ordering(self):
        assert Confidence.HIGH > Confidence.MEDIUM
        assert Confidence.MEDIUM > Confidence.LOW

    def test_is_acceptable(self):
        assert Confidence.HIGH.is_acceptable()
        assert Confidence.MEDIUM.is_acceptable()
        assert not Confidence.LOW.is_acceptable()


class TestCorrelationId:
    def test_generate(self):
        cid = CorrelationId.generate()
        assert cid.value
        assert len(cid.value) == 12

    def test_from_string(self):
        cid = CorrelationId.from_string("test-123")
        assert str(cid) == "test-123"

    def test_immutable(self):
        cid = CorrelationId.from_string("test")
        with pytest.raises(AttributeError):
            cid.value = "changed"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            CorrelationId(value="")
