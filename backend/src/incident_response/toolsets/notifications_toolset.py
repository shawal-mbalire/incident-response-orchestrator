from typing import Optional
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.readonly_context import ReadonlyContext

from incident_response.domain.ports.outbound.notifications import NotificationPort


class NotificationsToolset(BaseToolset):
    """ADK Toolset that adapts a NotificationPort into agent-callable tools."""

    def __init__(self, notifications_port: NotificationPort) -> None:
        super().__init__(tool_name_prefix="notifications")
        self._port = notifications_port
        self._tools = [
            FunctionTool(func=self._send_alert),
            FunctionTool(func=self._create_incident_channel),
        ]

    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> list[BaseTool]:
        return self._tools

    async def close(self) -> None:
        pass

    async def _send_alert(
        self, channel: str, message: str, ctx: ToolContext = None
    ) -> dict:
        """Send an alert notification to a channel.

        Args:
            channel: The notification channel (e.g., Slack channel, email).
            message: The alert message to send.

        Returns:
            Dict with status and confirmation.
        """
        success = await self._port.send_alert(channel, message)
        return {
            "status": "success" if success else "failed",
            "channel": channel,
            "message": message,
        }

    async def _create_incident_channel(
        self, incident_id: str, service: str, ctx: ToolContext = None
    ) -> dict:
        """Create a dedicated channel for an incident.

        Args:
            incident_id: The incident identifier.
            service: The affected service name.

        Returns:
            Dict with status and channel name.
        """
        channel = await self._port.create_incident_channel(incident_id, service)
        return {
            "status": "success",
            "incident_id": incident_id,
            "channel": channel,
        }
