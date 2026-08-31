
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext

from incident_response.domain.ports.inbound.analysis import IncidentAnalysisPort


class MonitoringToolset(BaseToolset):
    """ADK Toolset that adapts IncidentAnalysisPort into agent-callable tools.

    Routes through the application layer for proper orchestration,
    correlation ID tracking, and error handling.
    """

    def __init__(self, analysis_port: IncidentAnalysisPort) -> None:
        super().__init__(tool_name_prefix="monitoring")
        self._port = analysis_port
        self._tools = [
            FunctionTool(func=self._fetch_metrics),
            FunctionTool(func=self._query_logs),
        ]

    async def get_tools(self, readonly_context: ReadonlyContext | None = None) -> list[BaseTool]:
        return self._tools

    async def close(self) -> None:
        pass

    async def _fetch_metrics(
        self, service: str, metric_types: str, minutes: int = 30, ctx: ToolContext = None
    ) -> dict:
        """Fetch metrics for a Cloud Run service from Cloud Monitoring.

        Args:
            service: The Cloud Run service name to query.
            metric_types: Comma-separated list of metric types
                (error_rate, latency_p99, cpu, memory).
            minutes: Time range in minutes to look back (default: 30).

        Returns:
            Dict with status and metric data including current values and trends.
        """
        return await self._port.fetch_service_metrics(service, metric_types, minutes)

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
        return await self._port.query_service_logs(service, severity, minutes)
