from dataclasses import dataclass, field
from datetime import UTC, datetime

from incident_response.domain.exceptions import ValidationError
from incident_response.domain.value_objects.confidence import Confidence
from incident_response.domain.value_objects.correlation_id import CorrelationId


@dataclass
class IncidentReport:
    """Domain model for an incident report with validation."""

    incident_id: str
    executive_summary: str = ""
    timeline: list[dict] = field(default_factory=list)
    root_cause: str = ""
    confidence: Confidence = Confidence.LOW
    impact_assessment: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    supporting_evidence: dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise ValidationError("incident_id is required", field="incident_id")

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
**Confidence Level:** {self.confidence.value}

{self.root_cause}

## Impact Assessment
{self.impact_assessment}

## Recommended Actions
{actions}

---
*Generated at {self.generated_at.isoformat()}*
*Correlation ID: {self.correlation_id}*
"""

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "executive_summary": self.executive_summary,
            "timeline": self.timeline,
            "root_cause": self.root_cause,
            "confidence": self.confidence.value,
            "impact_assessment": self.impact_assessment,
            "recommended_actions": self.recommended_actions,
            "supporting_evidence": self.supporting_evidence,
            "generated_at": self.generated_at.isoformat(),
            "correlation_id": str(self.correlation_id),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IncidentReport":
        corr_id = data.get("correlation_id")
        return cls(
            incident_id=data["incident_id"],
            executive_summary=data.get("executive_summary", ""),
            timeline=data.get("timeline", []),
            root_cause=data.get("root_cause", ""),
            confidence=Confidence.from_string(data.get("confidence", "low")),
            impact_assessment=data.get("impact_assessment", ""),
            recommended_actions=data.get("recommended_actions", []),
            supporting_evidence=data.get("supporting_evidence", {}),
            correlation_id=(
                CorrelationId.from_string(corr_id)
                if corr_id
                else CorrelationId.generate()
            ),
        )
