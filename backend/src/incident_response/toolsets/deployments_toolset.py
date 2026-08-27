from typing import Optional
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.readonly_context import ReadonlyContext

from incident_response.domain.ports.outbound.deployments import DeploymentPort


class DeploymentsToolset(BaseToolset):
    """ADK Toolset that adapts a DeploymentPort into agent-callable tools."""

    def __init__(self, deployments_port: DeploymentPort) -> None:
        super().__init__(tool_name_prefix="deployments")
        self._port = deployments_port
        self._tools = [
            FunctionTool(func=self._get_recent_deploys),
        ]

    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> list[BaseTool]:
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
        deploys = await self._port.get_recent_deploys(service, hours)
        return {
            "status": "success",
            "service": service,
            "hours": hours,
            "deployments": deploys,
            "count": len(deploys),
        }
