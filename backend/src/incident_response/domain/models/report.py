from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class IncidentReport:
    incident_id: str
    executive_summary: str = ""
    timeline: list[dict] = field(default_factory=list)
    root_cause: str = ""
    confidence: str = "low"
    impact_assessment: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    supporting_evidence: dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_markdown(self) -> str:
        actions = "\n".join(f"- {action}" for action in self.recommended_actions)
        timeline_entries = "\n".join(
            f"- **{entry.get('time', 'N/A')}**: {entry.get('event', '')}"
            for entry in self.timeline
        )

        return f"""# Incident Report: {self.incident_id}

## Executive Summary
{self.executive_summary}

## Timeline
{timeline_entries}

## Root Cause
**Confidence Level:** {self.confidence}

{self.root_cause}

## Impact Assessment
{self.impact_assessment}

## Recommended Actions
{actions}

---
*Generated at {self.generated_at.isoformat()}*
"""

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "executive_summary": self.executive_summary,
            "timeline": self.timeline,
            "root_cause": self.root_cause,
            "confidence": self.confidence,
            "impact_assessment": self.impact_assessment,
            "recommended_actions": self.recommended_actions,
            "supporting_evidence": self.supporting_evidence,
            "generated_at": self.generated_at.isoformat(),
        }
