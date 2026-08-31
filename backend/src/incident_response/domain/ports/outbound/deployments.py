from abc import ABC, abstractmethod

from incident_response.domain.value_objects.deploy_info import DeployInfo
from incident_response.domain.value_objects.time_range import TimeRange


class DeploymentPort(ABC):
    """Port: what the domain needs from a deployment system."""

    @abstractmethod
    async def get_recent_deploys(
        self,
        service: str,
        time_range: TimeRange,
    ) -> list[DeployInfo]:
        """Get recent deployments for a service. Returns typed DeployInfo list."""
        ...
