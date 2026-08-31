from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DeployInfo:
    """Immutable deployment information."""

    version: str
    timestamp: datetime
    message: str = ""
    image: str = ""
    author: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "DeployInfo":
        """Create from a raw dict (adapter output)."""
        ts = data.get("timestamp")
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now(UTC)

        return cls(
            version=data.get("version", "unknown"),
            timestamp=dt,
            message=data.get("message", ""),
            image=data.get("image", ""),
            author=data.get("author", ""),
            labels=dict(data.get("labels", {})),
        )

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "image": self.image,
            "author": self.author,
            "labels": self.labels,
        }
