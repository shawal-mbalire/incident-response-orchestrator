from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class TimeRange:
    """Immutable time range for queries."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError(f"end ({self.end}) must be after start ({self.start})")

    @classmethod
    def last_minutes(cls, minutes: int) -> "TimeRange":
        """Create a time range for the last N minutes."""
        now = datetime.now(UTC)
        return cls(start=now - timedelta(minutes=minutes), end=now)

    @classmethod
    def last_hours(cls, hours: int) -> "TimeRange":
        """Create a time range for the last N hours."""
        now = datetime.now(UTC)
        return cls(start=now - timedelta(hours=hours), end=now)

    @property
    def duration_minutes(self) -> float:
        """Duration in minutes."""
        return (self.end - self.start).total_seconds() / 60

    def to_iso_tuple(self) -> tuple[str, str]:
        """Return start/end as ISO format strings."""
        return (self.start.isoformat(), self.end.isoformat())

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime falls within this range."""
        return self.start <= dt <= self.end
