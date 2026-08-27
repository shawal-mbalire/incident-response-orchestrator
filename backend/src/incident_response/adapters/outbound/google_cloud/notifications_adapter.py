from incident_response.domain.ports.outbound.notifications import NotificationPort


class PubSubNotificationsAdapter(NotificationPort):
    """Outbound adapter: wraps Google Pub/Sub for notifications."""

    def __init__(self, project_id: str) -> None:
        self._project_id = project_id

    async def send_alert(self, channel: str, message: str, details: dict | None = None) -> bool:
        # Placeholder - implement with Pub/Sub or Slack API
        return True

    async def create_incident_channel(self, incident_id: str, service: str) -> str:
        return f"incidents-{incident_id}"
