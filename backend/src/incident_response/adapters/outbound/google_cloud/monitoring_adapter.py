import logging
from datetime import UTC, datetime

from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3

from incident_response.domain.exceptions import AdapterError
from incident_response.domain.ports.outbound.monitoring import MonitoringPort
from incident_response.domain.value_objects.log_entry import LogEntry
from incident_response.domain.value_objects.metric_result import MetricResult, MetricValue
from incident_response.domain.value_objects.severity import Severity
from incident_response.domain.value_objects.time_range import TimeRange

logger = logging.getLogger(__name__)


class CloudMonitoringAdapter(MonitoringPort):
    """Outbound adapter: wraps Google Cloud Logging + Monitoring.

    This is the ONLY place in the codebase that imports google.cloud.*
    The domain and agents never know this implementation exists.
    """

    def __init__(self, project_id: str) -> None:
        self._project_id = project_id
        self._logging_client = cloud_logging.Client(project=project_id)
        self._monitoring_client = monitoring_v3.MetricServiceClient()
        self._project_name = f"projects/{project_id}"

    async def fetch_metrics(
        self,
        service: str,
        metric_types: list[str],
        time_range: TimeRange,
    ) -> MetricResult:
        interval = monitoring_v3.TimeInterval(
            end_time={"seconds": int(time_range.end.timestamp())},
            start_time={"seconds": int(time_range.start.timestamp())},
        )

        results: dict[str, MetricValue] = {}
        for metric_type in metric_types:
            metric_filter = self._build_metric_filter(service, metric_type)
            request = monitoring_v3.ListTimeSeriesRequest(
                name=self._project_name,
                filter=metric_filter,
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            )

            try:
                time_series = self._monitoring_client.list_time_series(request=request)
                values: list[float] = []
                for series in time_series:
                    for point in series.points:
                        if point.value.double_value is not None:
                            values.append(point.value.double_value)
                        elif point.value.int64_value is not None:
                            values.append(float(point.value.int64_value))

                results[metric_type] = MetricValue(
                    current=values[-1] if values else 0,
                    values=values[-10:],
                    unit=self._get_metric_unit(metric_type),
                )
            except Exception as e:
                logger.error(
                    "fetch_metrics_error",
                    extra={"service": service, "metric_type": metric_type, "error": str(e)},
                )
                results[metric_type] = MetricValue(current=0, values=[], unit="count")

        return MetricResult(metrics=results)

    async def query_logs(
        self,
        service: str,
        severity: str,
        time_range: TimeRange,
    ) -> list[LogEntry]:
        try:
            logger_obj = self._logging_client.logger("requests")

            filter_str = (
                f'resource.type="cloud_run_revision" AND '
                f'resource.labels.service_name="{service}" AND '
                f'severity>={severity}'
            )

            entries = logger_obj.list_entries(
                filter_=filter_str,
                order_by=cloud_logging.DESCENDING,
                max_results=100,
            )

            logs: list[LogEntry] = []
            for entry in entries:
                entry_time = entry.timestamp.replace(tzinfo=UTC) if entry.timestamp else datetime.now(UTC)
                if entry_time < time_range.start:
                    break

                message = (
                    entry.payload.get("message", str(entry.payload))
                    if isinstance(entry.payload, dict)
                    else str(entry.payload)
                )

                logs.append(
                    LogEntry(
                        timestamp=entry_time,
                        severity=Severity.from_string(entry.severity or "INFO"),
                        message=message,
                        labels=dict(entry.labels) if entry.labels else {},
                        trace=entry.trace,
                    )
                )

            return logs
        except Exception as e:
            logger.error("query_logs_error", extra={"service": service, "error": str(e)})
            raise AdapterError("CloudLogging", f"Failed to query logs: {e}", cause=e) from e

    def _build_metric_filter(self, service: str, metric_type: str) -> str:
        metric_map = {
            "error_rate": 'metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="500"',
            "latency_p99": 'metric.type="run.googleapis.com/request_latencies" AND metric.labels.quantile="0.99"',
            "cpu": 'metric.type="run.googleapis.com/cpu/utilization"',
            "memory": 'metric.type="run.googleapis.com/memory/utilization"',
        }
        base_filter = metric_map.get(metric_type, f'metric.type="{metric_type}"')
        return (
            f'{base_filter} AND '
            f'resource.type="cloud_run_revision" AND '
            f'resource.labels.service_name="{service}"'
        )

    def _get_metric_unit(self, metric_type: str) -> str:
        units = {
            "error_rate": "percent",
            "latency_p99": "ms",
            "cpu": "percent",
            "memory": "percent",
        }
        return units.get(metric_type, "count")
