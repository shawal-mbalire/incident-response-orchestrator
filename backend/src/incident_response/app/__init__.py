"""Incident Response Orchestrator - ADK Agent Entry Point.

This module is the entry point for `adk web` and `adk run` commands.
It exports the root_agent that ADK uses to serve the agent.
"""

from incident_response.app.factory import create_app

# Create the agent - this is what ADK discovers
root_agent, _ = create_app()
