import logging
from datetime import UTC, datetime

from google.cloud import run_v2

from incident_response.domain.exceptions import AdapterError
from incident_response.domain.ports.outbound.deployments import DeploymentPort
from incident_response.domain.value_objects.deploy_info import DeployInfo
from incident_response.domain.value_objects.time_range import TimeRange

logger = logging.getLogger(__name__)


class CloudDeploymentsAdapter(DeploymentPort):
    """Outbound adapter: wraps Google Cloud Run API for deployment info."""

    def __init__(self, project_id: str, region: str = "us-central1") -> None:
        self._project_id = project_id
        self._region = region
        self._client = run_v2.ServicesClient()

    async def get_recent_deploys(
        self,
        service: str,
        time_range: TimeRange,
    ) -> list[DeployInfo]:
        parent = f"projects/{self._project_id}/locations/{self._region}/services/{service}"

        try:
            request = run_v2.ListRevisionsRequest(parent=parent)
            revisions = self._client.list_revisions(request=request)

            deploys: list[DeployInfo] = []
            for revision in revisions:
                create_time = revision.create_time
                if create_time:
                    create_dt = datetime.fromtimestamp(create_time.timestamp(), tz=UTC)
                    if create_dt < time_range.start:
                        continue

                labels = dict(revision.labels) if revision.labels else {}
                annotations = dict(revision.annotations) if revision.annotations else {}

                deploys.append(
                    DeployInfo(
                        version=revision.name.split("/")[-1],
                        timestamp=(
                            datetime.fromtimestamp(create_time.timestamp(), tz=UTC)
                            if create_time
                            else datetime.now(UTC)
                        ),
                        message=annotations.get("deployment.kubernetes.io/description", ""),
                        image=revision.containers[0].image if revision.containers else "",
                        author=annotations.get("run.googleapis.com/creator", ""),
                        labels=labels,
                    )
                )

            deploys.sort(key=lambda d: d.timestamp, reverse=True)
            return deploys[:10]

        except Exception as e:
            logger.error("get_recent_deploys_error", extra={"service": service, "error": str(e)})
            raise AdapterError("CloudRun", f"Failed to get deployments: {e}", cause=e) from e
