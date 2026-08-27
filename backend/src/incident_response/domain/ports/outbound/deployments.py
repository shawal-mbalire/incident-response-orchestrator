from abc import ABC, abstractmethod


class DeploymentPort(ABC):
    """Port: what the domain needs from a deployment system."""

    @abstractmethod
    async def get_recent_deploys(
        self,
        service: str,
        hours: int = 24,
    ) -> list[dict]:
        """Get recent deployments for a Cloud Run service."""
        ...
