from google.adk.agents import LlmAgent

from incident_response.toolsets.monitoring_toolset import MonitoringToolset


def create_metrics_agent(monitoring_toolset: MonitoringToolset) -> LlmAgent:
    """Creates the metrics analysis agent that fetches and analyzes performance data."""

    return LlmAgent(
        name="MetricsAnalyzerAgent",
        model="gemini-2.5-flash",
        instruction="""You are a metrics analysis specialist. Your job is to fetch and analyze performance metrics.

When given a service name and time range:
1. Use the fetch_metrics tool to get error_rate, latency_p99, cpu, and memory metrics
2. Analyze the current values against thresholds
3. Identify anomalies and spikes
4. Detect correlations between different metrics
5. Pinpoint when the incident likely started based on metric trends

Write your findings to session state with key 'metrics_snapshot' as a structured summary:
- Current metric values with units
- Threshold breaches (which metrics exceed normal)
- Anomaly detection results
- Correlated metric changes
- Estimated incident start time

Use these thresholds as guidelines:
- Error rate: normal < 1%, warning 1-5%, critical > 5%
- Latency p99: normal < 500ms, warning 500-2000ms, critical > 2000ms
- CPU: normal < 70%, warning 70-90%, critical > 90%
- Memory: normal < 80%, warning 80-90%, critical > 90%""",
        description="Fetches and analyzes performance metrics from Cloud Monitoring.",
        tools=[monitoring_toolset],
        output_key="metrics_snapshot",
    )
