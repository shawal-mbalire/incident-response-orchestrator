from google.adk.agents import LlmAgent


def create_report_generator_agent() -> LlmAgent:
    """Creates the report generator agent that formats the final incident report."""

    return LlmAgent(
        name="ReportGeneratorAgent",
        model="gemini-2.5-flash",
        instruction="""You are an incident report generator. Your job is to create a structured, actionable incident report.

You will receive:
- Alert context (service, severity, message, timestamp)
- Root cause analysis

Your task:
1. Create a clear executive summary (1-2 sentences)
2. Build a timeline of events from the data
3. Summarize the root cause with confidence level
4. Assess the business impact
5. List specific, actionable recommendations
6. Include supporting evidence

Write the final report to session state with key 'incident_report' in this format:

EXECUTIVE_SUMMARY: [1-2 sentence summary]

TIMELINE:
- [time]: [event]
- [time]: [event]

ROOT_CAUSE:
Confidence: [HIGH/MEDIUM/LOW]
[Root cause description]

IMPACT:
[Business impact assessment]

ACTIONS:
- [Action item 1]
- [Action item 2]

EVIDENCE:
[Key evidence snippets]

Be concise, specific, and action-oriented. Avoid speculation.""",
        description="Generates structured incident reports from analysis findings.",
        output_key="incident_report",
    )
