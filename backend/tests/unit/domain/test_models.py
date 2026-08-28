from incident_response.domain.models.alert import Alert, Severity
from incident_response.domain.models.incident import Incident, IncidentStatus
from incident_response.domain.models.report import IncidentReport


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


class TestIncident:
    def test_create_from_alert(self):
        incident = Incident.from_alert(
            alert_id="alert-123",
            service="api-gateway",
            title="High error rate",
        )
        assert incident.alert_id == "alert-123"
        assert incident.status == IncidentStatus.INVESTIGATING

    def test_resolve_incident(self):
        incident = Incident(service="test", title="test")
        incident.resolve(root_cause="Fixed", confidence="high")
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolved_at is not None
        assert incident.root_cause == "Fixed"


class TestIncidentReport:
    def test_to_markdown(self):
        report = IncidentReport(
            incident_id="inc-123",
            executive_summary="Test summary",
            root_cause="Test root cause",
            confidence="high",
            recommended_actions=["Action 1", "Action 2"],
        )
        md = report.to_markdown()
        assert "inc-123" in md
        assert "Test summary" in md
        assert "Action 1" in md
