from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.ports.outbound.events import EventPublisherPort
from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.ports.outbound.notifications import NotificationPort
from incident_response.domain.ports.outbound.state_store import StateStorePort
from incident_response.domain.services.incident_service import IncidentService


class Container:
    """Dependency injection container.

    Centralizes adapter selection based on environment configuration.
    In production, swap InMemory adapters for Google Cloud adapters.
    """

    def __init__(
        self,
        monitoring: MonitoringPort,
        deployments: DeploymentPort,
        notifications: NotificationPort,
        state_store: StateStorePort,
        event_publisher: EventPublisherPort | None = None,
        max_cache_size: int = 1000,
        settings: "Settings | None" = None,
    ) -> None:
        self.monitoring = monitoring
        self.deployments = deployments
        self.notifications = notifications
        self.state_store = state_store
        self.event_publisher = event_publisher
        self.settings = settings

        self.incident_service = IncidentService(
            monitoring=monitoring,
            deployments=deployments,
            notifications=notifications,
            state_store=state_store,
            event_publisher=event_publisher,
            max_cache_size=max_cache_size,
        )
