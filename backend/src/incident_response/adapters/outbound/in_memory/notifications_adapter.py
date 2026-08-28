from incident_response.domain.ports.outbound.notifications import NotificationPort


class InMemoryNotificationsAdapter(NotificationPort):
    """Outbound adapter: in-memory mock for notifications."""

    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.channels: dict[str, str] = {}

    async def send_alert(self, channel: str, message: str, details: dict | None = None) -> bool:
        self.sent.append({"channel": channel, "message": message, "details": details})
        return True

    async def create_incident_channel(self, incident_id: str, service: str) -> str:
        channel_id = f"incidents-{incident_id}"
        self.channels[incident_id] = channel_id
        return channel_id
