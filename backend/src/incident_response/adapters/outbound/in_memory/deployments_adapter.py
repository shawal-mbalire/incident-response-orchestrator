from datetime import datetime, timedelta, timezone

from incident_response.domain.ports.outbound.deployments import DeploymentPort


class InMemoryDeploymentsAdapter(DeploymentPort):
    """Outbound adapter: in-memory mock for testing and local dev."""

    def __init__(self) -> None:
        self._deploys: dict[str, list[dict]] = {}

    def seed_deploys(self, service: str, count: int = 3) -> None:
        now = datetime.now(timezone.utc)
        self._deploys[service] = [
            {
                "version": f"{service}-v{10 - i}.0.0",
                "timestamp": (now - timedelta(hours=i * 2)).isoformat(),
                "message": f"Deploy version {10 - i}.0.0",
                "image": f"gcr.io/project/{service}:{10 - i}.0.0",
                "author": "developer@example.com",
                "labels": {},
            }
            for i in range(count)
        ]

    async def get_recent_deploys(
        self,
        service: str,
        hours: int = 24,
    ) -> list[dict]:
        if service not in self._deploys:
            self.seed_deploys(service)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            deploy
            for deploy in self._deploys[service]
            if datetime.fromisoformat(deploy["timestamp"]).replace(tzinfo=timezone.utc) >= cutoff
        ]
