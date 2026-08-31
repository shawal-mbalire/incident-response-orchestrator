import pytest

from incident_response.adapters.outbound.in_memory.deployments_adapter import (
    InMemoryDeploymentsAdapter,
)
from incident_response.adapters.outbound.in_memory.events_adapter import (
    InMemoryEventPublisher,
)
from incident_response.adapters.outbound.in_memory.monitoring_adapter import (
    InMemoryMonitoringAdapter,
)
from incident_response.adapters.outbound.in_memory.notifications_adapter import (
    InMemoryNotificationsAdapter,
)
from incident_response.adapters.outbound.in_memory.state_store_adapter import (
    InMemoryStateStoreAdapter,
)
from incident_response.config.container import Container


@pytest.fixture
def monitoring_adapter():
    adapter = InMemoryMonitoringAdapter()
    adapter.seed_logs("api-gateway", count=20)
    adapter.seed_metrics("api-gateway")
    return adapter


@pytest.fixture
def deployments_adapter():
    adapter = InMemoryDeploymentsAdapter()
    adapter.seed_deploys("api-gateway", count=3)
    return adapter


@pytest.fixture
def notifications_adapter():
    return InMemoryNotificationsAdapter()


@pytest.fixture
def state_store_adapter():
    return InMemoryStateStoreAdapter()


@pytest.fixture
def event_publisher():
    return InMemoryEventPublisher()


@pytest.fixture
def container(
    monitoring_adapter,
    deployments_adapter,
    notifications_adapter,
    state_store_adapter,
    event_publisher,
):
    return Container(
        monitoring=monitoring_adapter,
        deployments=deployments_adapter,
        notifications=notifications_adapter,
        state_store=state_store_adapter,
        event_publisher=event_publisher,
    )


@pytest.fixture
def incident_service(container):
    return container.incident_service
