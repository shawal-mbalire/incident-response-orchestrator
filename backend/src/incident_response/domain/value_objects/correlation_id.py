import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CorrelationId:
    """Immutable correlation ID for tracing requests through the system."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("CorrelationId must be non-empty")

    @classmethod
    def generate(cls) -> "CorrelationId":
        """Generate a new random correlation ID."""
        return cls(value=str(uuid.uuid4())[:12])

    @classmethod
    def from_string(cls, value: str) -> "CorrelationId":
        """Create from an existing string value."""
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CorrelationId):
            return NotImplemented
        return self.value == other.value
