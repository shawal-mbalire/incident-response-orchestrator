import logging

from incident_response.domain.ports.outbound.notifications import NotificationPort

logger = logging.getLogger(__name__)


class PubSubNotificationsAdapter(NotificationPort):
    """Outbound adapter: wraps Google Pub/Sub for notifications."""

    def __init__(self, project_id: str) -> None:
        self._project_id = project_id

    async def send_alert(self, channel: str, message: str, details: dict | None = None) -> bool:
        logger.info("send_alert", extra={"channel": channel, "message": message[:100]})
        return True

    async def create_incident_channel(self, incident_id: str, service: str) -> str:
        channel_id = f"incidents-{incident_id}"
        logger.info("create_channel", extra={"incident_id": incident_id, "channel": channel_id})
        return channel_id
