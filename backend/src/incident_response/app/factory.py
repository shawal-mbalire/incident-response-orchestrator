from incident_response.config.settings import Settings
from incident_response.config.container import Container
from incident_response.agents.root_agent import create_root_agent
from incident_response.toolsets.monitoring_toolset import MonitoringToolset
from incident_response.toolsets.deployments_toolset import DeploymentsToolset


def create_app(settings: Settings | None = None):
    """Application factory. Assembles adapters based on configuration.

    This is the composition root -- the only place that knows about
    both ports AND their concrete implementations.
    """
    settings = settings or Settings()

    # Select adapters based on environment
    if settings.environment == "production":
        from incident_response.adapters.outbound.google_cloud.monitoring_adapter import (
            CloudMonitoringAdapter,
        )
        from incident_response.adapters.outbound.google_cloud.deployments_adapter import (
            CloudDeploymentsAdapter,
        )
        from incident_response.adapters.outbound.google_cloud.notifications_adapter import (
            PubSubNotificationsAdapter,
        )
        from incident_response.adapters.outbound.google_cloud.state_store_adapter import (
            FirestoreStateStoreAdapter,
        )

        monitoring_port = CloudMonitoringAdapter(project_id=settings.gcp_project_id)
        deployments_port = CloudDeploymentsAdapter(
            project_id=settings.gcp_project_id, region=settings.gcp_region
        )
        notifications_port = PubSubNotificationsAdapter(project_id=settings.gcp_project_id)
        state_store_port = FirestoreStateStoreAdapter(project_id=settings.gcp_project_id)
    else:
        from incident_response.adapters.outbound.in_memory.monitoring_adapter import (
            InMemoryMonitoringAdapter,
        )
        from incident_response.adapters.outbound.in_memory.deployments_adapter import (
            InMemoryDeploymentsAdapter,
        )
        from incident_response.adapters.outbound.in_memory.state_store_adapter import (
            InMemoryStateStoreAdapter,
        )
        from incident_response.adapters.outbound.in_memory.notifications_adapter import (
            InMemoryNotificationsAdapter,
        )

        monitoring_port = InMemoryMonitoringAdapter()
        deployments_port = InMemoryDeploymentsAdapter()
        notifications_port = InMemoryNotificationsAdapter()
        state_store_port = InMemoryStateStoreAdapter()

    # Wire the container
    container = Container(
        monitoring=monitoring_port,
        deployments=deployments_port,
        notifications=notifications_port,
        state_store=state_store_port,
    )

    # Create ADK toolsets from ports
    monitoring_toolset = MonitoringToolset(monitoring_port)
    deployments_toolset = DeploymentsToolset(deployments_port)

    # Assemble the multi-agent system
    root_agent = create_root_agent(
        monitoring_toolset=monitoring_toolset,
        deployments_toolset=deployments_toolset,
        model=settings.agent_model,
    )

    return root_agent, container
