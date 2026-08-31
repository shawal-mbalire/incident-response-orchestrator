
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext

from incident_response.domain.ports.inbound.analysis import IncidentAnalysisPort


class DeploymentsToolset(BaseToolset):
    """ADK Toolset that adapts IncidentAnalysisPort into agent-callable tools.

    Routes through the application layer for proper orchestration,
    correlation ID tracking, and error handling.
    """

    def __init__(self, analysis_port: IncidentAnalysisPort) -> None:
        super().__init__(tool_name_prefix="deployments")
        self._port = analysis_port
        self._tools = [
            FunctionTool(func=self._get_recent_deploys),
        ]

    async def get_tools(self, readonly_context: ReadonlyContext | None = None) -> list[BaseTool]:
        return self._tools

    async def close(self) -> None:
        pass

    async def _get_recent_deploys(
        self, service: str, hours: int = 24, ctx: ToolContext = None
    ) -> dict:
        """Get recent deployments for a Cloud Run service.

        Args:
            service: The Cloud Run service name to check.
            hours: How many hours back to look (default: 24).

        Returns:
            Dict with status and list of recent deployments with timestamps and versions.
        """
        return await self._port.get_recent_deploys(service, hours)
