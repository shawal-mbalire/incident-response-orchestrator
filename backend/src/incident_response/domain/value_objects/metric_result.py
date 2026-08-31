from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricValue:
    """A single metric with current value, history, and unit."""

    current: float
    values: list[float] = field(default_factory=list)
    unit: str = "count"

    def __post_init__(self) -> None:
        if self.values and self.current not in self.values:
            pass  # current may be a summary not in the raw values

    @property
    def trend(self) -> str:
        """Simple trend detection: rising, falling, or stable."""
        if len(self.values) < 2:
            return "stable"
        first_half = sum(self.values[: len(self.values) // 2]) / max(len(self.values) // 2, 1)
        second_half = sum(self.values[len(self.values) // 2 :]) / max(
            len(self.values) - len(self.values) // 2, 1
        )
        diff_pct = (second_half - first_half) / max(first_half, 0.001) * 100
        if diff_pct > 10:
            return "rising"
        elif diff_pct < -10:
            return "falling"
        return "stable"


@dataclass(frozen=True)
class MetricResult:
    """Typed result from metrics query. Replaces raw dict returns."""

    metrics: dict[str, MetricValue]

    def get(self, metric_type: str) -> MetricValue | None:
        return self.metrics.get(metric_type)

    def get_current(self, metric_type: str, default: float = 0.0) -> float:
        mv = self.metrics.get(metric_type)
        return mv.current if mv else default

    def to_dict(self) -> dict[str, dict]:
        return {
            k: {"current": v.current, "values": v.values, "unit": v.unit, "trend": v.trend}
            for k, v in self.metrics.items()
        }
