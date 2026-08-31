import pytest

from incident_response.domain.models.alert import Alert
from incident_response.domain.value_objects.severity import Severity


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
    assert report.confidence.value in ("high", "medium", "low")
    assert len(report.recommended_actions) > 0
    assert len(report.timeline) > 0
    assert report.correlation_id is not None


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


@pytest.mark.asyncio
async def test_analyze_incident_publishes_events(incident_service, event_publisher):
    alert = Alert(
        service="api-gateway",
        severity=Severity.HIGH,
        message="High error rate detected",
    )

    await incident_service.analyze_incident(alert)

    assert len(event_publisher.published) >= 2
    event_types = [e.event_type for e in event_publisher.published]
    assert "IncidentCreated" in event_types
    assert "IncidentAnalyzed" in event_types


@pytest.mark.asyncio
async def test_analyze_incident_with_correlation_id(incident_service):
    from incident_response.domain.value_objects.correlation_id import CorrelationId

    corr_id = CorrelationId.from_string("test-corr-123")
    alert = Alert(
        service="api-gateway",
        severity=Severity.HIGH,
        message="Test alert",
    )

    report = await incident_service.analyze_incident(alert, correlation_id=corr_id)
    assert str(report.correlation_id) == "test-corr-123"


@pytest.mark.asyncio
async def test_cache_eviction():
    from incident_response.adapters.outbound.in_memory.deployments_adapter import (
        InMemoryDeploymentsAdapter,
    )
    from incident_response.adapters.outbound.in_memory.events_adapter import InMemoryEventPublisher
    from incident_response.adapters.outbound.in_memory.monitoring_adapter import (
        InMemoryMonitoringAdapter,
    )
    from incident_response.adapters.outbound.in_memory.notifications_adapter import (
        InMemoryNotificationsAdapter,
    )
    from incident_response.adapters.outbound.in_memory.state_store_adapter import (
        InMemoryStateStoreAdapter,
    )
    from incident_response.domain.services.incident_service import IncidentService

    service = IncidentService(
        monitoring=InMemoryMonitoringAdapter(),
        deployments=InMemoryDeploymentsAdapter(),
        notifications=InMemoryNotificationsAdapter(),
        state_store=InMemoryStateStoreAdapter(),
        event_publisher=InMemoryEventPublisher(),
        max_cache_size=3,
    )

    for i in range(5):
        alert = Alert(
            service="api-gateway",
            severity=Severity.HIGH,
            message=f"Alert {i}",
        )
        await service.analyze_incident(alert)

    assert len(service._reports) <= 3
