from enum import Enum


class Confidence(Enum):
    """Confidence level for root cause analysis with ordering."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def numeric(self) -> int:
        """Numeric value for comparison (higher = more confident)."""
        _map = {"high": 3, "medium": 2, "low": 1}
        return _map[self.value]

    def is_high(self) -> bool:
        return self == Confidence.HIGH

    def is_acceptable(self) -> bool:
        """Whether confidence is high or medium (actionable)."""
        return self.numeric >= Confidence.MEDIUM.numeric

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.numeric < other.numeric

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.numeric <= other.numeric

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.numeric > other.numeric

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Confidence):
            return NotImplemented
        return self.numeric >= other.numeric

    @classmethod
    def from_string(cls, value: str) -> "Confidence":
        """Parse confidence from string, raising ValueError for invalid values."""
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(c.value for c in cls)
            raise ValueError(
                f"Invalid confidence '{value}'. Must be one of: {valid}"
            ) from None
