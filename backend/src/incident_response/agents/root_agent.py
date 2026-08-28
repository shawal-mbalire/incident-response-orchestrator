from google.adk.agents import SequentialAgent, ParallelAgent

from incident_response.toolsets.monitoring_toolset import MonitoringToolset
from incident_response.toolsets.deployments_toolset import DeploymentsToolset
from incident_response.agents.sub_agents.log_forensics_agent import create_log_forensics_agent
from incident_response.agents.sub_agents.metrics_agent import create_metrics_agent
from incident_response.agents.sub_agents.deploy_tracker_agent import create_deploy_tracker_agent
from incident_response.agents.sub_agents.synthesizer_agent import create_synthesizer_agent
from incident_response.agents.sub_agents.report_generator_agent import create_report_generator_agent


def create_root_agent(
    monitoring_toolset: MonitoringToolset,
    deployments_toolset: DeploymentsToolset,
    model: str = "gemini-3.5-flash",
) -> SequentialAgent:
    """Factory: assembles the multi-agent incident response pipeline.

    Architecture:
    ┌──────────────────────────────────────────────────┐
    │           SequentialAgent (root)                 │
    │  ┌────────────────────────────────────────────┐  │
    │  │      ParallelAgent (fan-out)               │  │
    │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
    │  │  │   Log    │ │ Metrics  │ │ Deploy   │  │  │
    │  │  │ Forensics│ │ Analyzer │ │ Tracker  │  │  │
    │  │  └──────────┘ └──────────┘ └──────────┘  │  │
    │  └────────────────────────────────────────────┘  │
    │                      ↓                           │
    │  ┌────────────────────────────────────────────┐  │
    │  │         Synthesizer Agent                  │  │
    │  └────────────────────────────────────────────┘  │
    │                      ↓                           │
    │  ┌────────────────────────────────────────────┐  │
    │  │        Report Generator Agent              │  │
    │  └────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────┘
    """

    # Create specialized sub-agents
    log_forensics = create_log_forensics_agent(monitoring_toolset, model=model)
    metrics_analyzer = create_metrics_agent(monitoring_toolset, model=model)
    deploy_tracker = create_deploy_tracker_agent(deployments_toolset, model=model)

    # Fan-out: all 3 run concurrently
    parallel_analysis = ParallelAgent(
        name="ParallelAnalysisAgent",
        sub_agents=[log_forensics, metrics_analyzer, deploy_tracker],
        description="Runs log, metrics, and deployment analysis in parallel for faster investigation.",
    )

    # Fan-in: synthesizer combines findings
    synthesizer = create_synthesizer_agent(model=model)

    # Report generator
    report_generator = create_report_generator_agent(model=model)

    # Sequential pipeline: parallel → synthesize → report
    return SequentialAgent(
        name="IncidentResponsePipeline",
        sub_agents=[parallel_analysis, synthesizer, report_generator],
        description="Orchestrates incident analysis: parallel data gathering → synthesis → report generation.",
    )
