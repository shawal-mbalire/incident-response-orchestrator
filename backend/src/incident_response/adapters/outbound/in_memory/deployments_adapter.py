from datetime import UTC, datetime, timedelta

from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.value_objects.deploy_info import DeployInfo
from incident_response.domain.value_objects.time_range import TimeRange


class InMemoryDeploymentsAdapter(DeploymentPort):
    """Outbound adapter: in-memory mock for testing and local dev."""

    def __init__(self) -> None:
        self._deploys: dict[str, list[DeployInfo]] = {}

    def seed_deploys(self, service: str, count: int = 3) -> None:
        now = datetime.now(UTC)
        self._deploys[service] = [
            DeployInfo(
                version=f"{service}-v{10 - i}.0.0",
                timestamp=now - timedelta(hours=i * 2),
                message=f"Deploy version {10 - i}.0.0",
                image=f"gcr.io/project/{service}:{10 - i}.0.0",
                author="developer@example.com",
                labels={},
            )
            for i in range(count)
        ]

    async def get_recent_deploys(
        self,
        service: str,
        time_range: TimeRange,
    ) -> list[DeployInfo]:
        if service not in self._deploys:
            self.seed_deploys(service)

        return [
            deploy
            for deploy in self._deploys[service]
            if deploy.timestamp >= time_range.start
        ]
