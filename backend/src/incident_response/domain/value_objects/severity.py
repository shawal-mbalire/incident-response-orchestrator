from enum import Enum


class Severity(Enum):
    """Alert severity levels with ordering and validation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def numeric(self) -> int:
        """Numeric value for comparison (higher = more severe)."""
        _map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return _map[self.value]

    def is_critical(self) -> bool:
        return self == Severity.CRITICAL

    def is_high_or_above(self) -> bool:
        return self.numeric >= Severity.HIGH.numeric

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.numeric < other.numeric

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.numeric <= other.numeric

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.numeric > other.numeric

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.numeric >= other.numeric

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """Parse severity from string, raising ValueError for invalid values."""
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(s.value for s in cls)
            raise ValueError(
                f"Invalid severity '{value}'. Must be one of: {valid}"
            ) from None
