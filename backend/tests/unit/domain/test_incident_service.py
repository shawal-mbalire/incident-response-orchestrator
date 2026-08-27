import pytest
from incident_response.domain.models.alert import Alert, Severity


@pytest.mark.asyncio
async def test_analyze_incident(incident_service):
    alert = Alert(
        service="api-gateway",
        severity=Severity.HIGH,
        message="High error rate detected in production",
    )

    report = await incident_service.analyze_incident(alert)

    assert report.incident_id is not None
    assert report.executive_summary != ""
    assert report.root_cause != ""
    assert report.confidence in ("high", "medium", "low")
    assert len(report.recommended_actions) > 0
    assert len(report.timeline) > 0


@pytest.mark.asyncio
async def test_get_report(incident_service):
    alert = Alert(
        service="api-gateway",
        severity=Severity.CRITICAL,
        message="Service down",
    )

    report = await incident_service.analyze_incident(alert)
    retrieved = await incident_service.get_report(report.incident_id)

    assert retrieved is not None
    assert retrieved.incident_id == report.incident_id


@pytest.mark.asyncio
async def test_get_nonexistent_report(incident_service):
    result = await incident_service.get_report("nonexistent-id")
    assert result is None
