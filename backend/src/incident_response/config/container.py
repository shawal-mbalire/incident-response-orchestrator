from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.ports.outbound.notifications import NotificationPort
from incident_response.domain.services.incident_service import IncidentService


class Container:
    """Simple dependency injection container.

    Centralizes adapter selection based on environment configuration.
    In production, swap InMemory adapters for Google Cloud adapters.
    """

    def __init__(
        self,
        monitoring: MonitoringPort,
        deployments: DeploymentPort,
        notifications: NotificationPort,
    ) -> None:
        self.monitoring = monitoring
        self.deployments = deployments
        self.notifications = notifications

        # Wire domain service with injected port implementations
        self.incident_service = IncidentService(
            monitoring=monitoring,
            deployments=deployments,
            notifications=notifications,
        )
