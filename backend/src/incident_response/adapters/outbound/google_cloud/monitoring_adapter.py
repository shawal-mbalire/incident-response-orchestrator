from datetime import datetime, timedelta, timezone

from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3

from incident_response.domain.ports.outbound.monitoring import MonitoringPort


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
        minutes: int = 30,
    ) -> dict:
        now = datetime.now(timezone.utc)
        interval = monitoring_v3.TimeInterval(
            end_time={"seconds": int(now.timestamp())},
            start_time={"seconds": int((now - timedelta(minutes=minutes)).timestamp())},
        )

        results = {}
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
                values = []
                for series in time_series:
                    for point in series.points:
                        values.append(point.value.double_value or point.value.int64_value)
                results[metric_type] = {
                    "current": values[-1] if values else 0,
                    "values": values[-10:],
                    "unit": self._get_metric_unit(metric_type),
                }
            except Exception as e:
                results[metric_type] = {"error": str(e), "current": 0}

        return results

    async def query_logs(
        self,
        service: str,
        severity: str = "ERROR",
        minutes: int = 30,
    ) -> list[dict]:
        logger = self._logging_client.logger("requests")

        filter_str = (
            f'resource.type="cloud_run_revision" AND '
            f'resource.labels.service_name="{service}" AND '
            f'severity>={severity}'
        )

        now = datetime.now(timezone.utc)
        entries = logger.list_entries(
            filter_=filter_str,
            order_by=cloud_logging.DESCENDING,
            max_results=100,
        )

        logs = []
        cutoff = now - timedelta(minutes=minutes)

        for entry in entries:
            entry_time = entry.timestamp.replace(tzinfo=timezone.utc) if entry.timestamp else now
            if entry_time < cutoff:
                break

            logs.append({
                "timestamp": entry_time.isoformat(),
                "severity": entry.severity or "INFO",
                "message": entry.payload.get("message", str(entry.payload)) if isinstance(entry.payload, dict) else str(entry.payload),
                "labels": dict(entry.labels) if entry.labels else {},
                "trace": entry.trace,
            })

        return logs

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
