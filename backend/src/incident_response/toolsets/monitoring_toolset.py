from typing import Optional
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.readonly_context import ReadonlyContext

from incident_response.domain.ports.outbound.monitoring import MonitoringPort


class MonitoringToolset(BaseToolset):
    """ADK Toolset that adapts a MonitoringPort into agent-callable tools.

    This is the bridge between hexagonal architecture's outbound ports
    and ADK's tool system.
    """

    def __init__(self, monitoring_port: MonitoringPort) -> None:
        super().__init__(tool_name_prefix="monitoring")
        self._port = monitoring_port
        self._tools = [
            FunctionTool(func=self._fetch_metrics),
            FunctionTool(func=self._query_logs),
        ]

    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> list[BaseTool]:
        return self._tools

    async def close(self) -> None:
        pass

    async def _fetch_metrics(
        self, service: str, metric_types: str, minutes: int = 30, ctx: ToolContext = None
    ) -> dict:
        """Fetch metrics for a Cloud Run service from Cloud Monitoring.

        Args:
            service: The Cloud Run service name to query.
            metric_types: Comma-separated list of metric types (error_rate, latency_p99, cpu, memory).
            minutes: Time range in minutes to look back (default: 30).

        Returns:
            Dict with status and metric data including current values and trends.
        """
        types = [t.strip() for t in metric_types.split(",")]
        result = await self._port.fetch_metrics(service, types, minutes)
        return {"status": "success", "service": service, "metrics": result}

    async def _query_logs(
        self, service: str, severity: str = "ERROR", minutes: int = 30, ctx: ToolContext = None
    ) -> dict:
        """Query logs for a Cloud Run service from Cloud Logging.

        Args:
            service: The Cloud Run service name to query.
            severity: Minimum log severity level (ERROR, WARNING, INFO).
            minutes: Time range in minutes to look back (default: 30).

        Returns:
            Dict with status, log entries, and count.
        """
        logs = await self._port.query_logs(service, severity, minutes)
        return {
            "status": "success",
            "service": service,
            "severity": severity,
            "logs": logs,
            "count": len(logs),
        }
