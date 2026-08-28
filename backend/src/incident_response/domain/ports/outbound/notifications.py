from abc import ABC, abstractmethod


class NotificationPort(ABC):
    """Port: what the domain needs from a notification system."""

    @abstractmethod
    async def send_alert(self, channel: str, message: str, details: dict | None = None) -> bool:
        """Send a notification to a channel."""
        ...

    @abstractmethod
    async def create_incident_channel(self, incident_id: str, service: str) -> str:
        """Create a dedicated channel/thread for an incident."""
        ...
