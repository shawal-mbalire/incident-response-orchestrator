from datetime import datetime, timedelta, timezone

from google.cloud import run_v2

from incident_response.domain.ports.outbound.deployments import DeploymentPort


class CloudDeploymentsAdapter(DeploymentPort):
    """Outbound adapter: wraps Google Cloud Run API for deployment info."""

    def __init__(self, project_id: str, region: str = "us-central1") -> None:
        self._project_id = project_id
        self._region = region
        self._client = run_v2.ServicesClient()

    async def get_recent_deploys(
        self,
        service: str,
        hours: int = 24,
    ) -> list[dict]:
        parent = f"projects/{self._project_id}/locations/{self._region}/services/{service}"

        try:
            request = run_v2.ListRevisionsRequest(parent=parent)
            revisions = self._client.list_revisions(request=request)

            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            deploys = []

            for revision in revisions:
                create_time = revision.create_time
                if create_time:
                    create_dt = datetime.fromtimestamp(create_time.timestamp(), tz=timezone.utc)
                    if create_dt < cutoff:
                        continue

                labels = dict(revision.labels) if revision.labels else {}
                annotations = dict(revision.annotations) if revision.annotations else {}

                deploys.append({
                    "version": revision.name.split("/")[-1],
                    "timestamp": create_time.isoformat() if create_time else "unknown",
                    "message": annotations.get("deployment.kubernetes.io/description", ""),
                    "image": revision.containers[0].image if revision.containers else "",
                    "author": annotations.get("run.googleapis.com/creator", ""),
                    "labels": labels,
                })

            deploys.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return deploys[:10]

        except Exception as e:
            return [{"error": str(e)}]
