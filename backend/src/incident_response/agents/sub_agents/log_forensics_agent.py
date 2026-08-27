from google.adk.agents import LlmAgent

from incident_response.toolsets.monitoring_toolset import MonitoringToolset


def create_log_forensics_agent(monitoring_toolset: MonitoringToolset) -> LlmAgent:
    """Creates the log forensics agent that analyzes error logs."""

    return LlmAgent(
        name="LogForensicsAgent",
        model="gemini-3.5-flash",
        instruction="""You are a log forensics specialist. Your job is to analyze error logs and identify patterns.

When given a service name and time range:
1. Use the query_logs tool to fetch ERROR and WARNING logs
2. Analyze the log entries for patterns and anomalies
3. Identify the most common error messages
4. Extract stack traces and error details
5. Note the frequency and timing of errors

Write your findings to session state with key 'log_analysis' as a structured summary:
- Common error patterns (list)
- Error frequency (count per minute)
- Notable stack traces
- Timeline of error occurrences
- Any correlations you notice

Be specific and evidence-based. Do not speculate without data.""",
        description="Analyzes error logs and identifies patterns for incident investigation.",
        tools=[monitoring_toolset],
        output_key="log_analysis",
    )
