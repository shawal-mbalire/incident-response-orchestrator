resource "google_monitoring_notification_channel" "email" {
  count      = length(var.notification_emails) > 0 ? 1 : 0
  display_name = "Incident Response Alerts"
  project      = var.project_id
  type         = "email"

  labels = {
    email_address = var.notification_emails[0]
  }
}

resource "google_monitoring_alert_policy" "backend_errors" {
  display_name = "Backend - High 5xx Error Rate"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "5xx error ratio > 1%"
    condition_threshold {
      filter = <<-EOT
        resource.type="cloud_run_revision" AND
        resource.labels.service_name="${var.backend_service_name}" AND
        metric.type="run.googleapis.com/request_count" AND
        metric.labels.response_code_class="500"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.01

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = length(var.notification_emails) > 0 ? [
    google_monitoring_notification_channel.email[0].name,
  ] : []

  documentation {
    content = <<-EOT
      ## Backend High Error Rate

      The 5xx error rate for ${var.backend_service_name} has exceeded 1% for 5 minutes.

      **Runbook:** Check application logs and recent deployments.
    EOT
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "backend_latency" {
  display_name = "Backend - High Latency (p99 > 3s)"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "p99 latency exceeds 3 seconds"
    condition_threshold {
      filter = <<-EOT
        resource.type="cloud_run_revision" AND
        resource.labels.service_name="${var.backend_service_name}" AND
        metric.type="run.googleapis.com/request_latencies" AND
        metric.labels.quantile="0.99"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 3000

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_99"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  notification_channels = length(var.notification_emails) > 0 ? [
    google_monitoring_notification_channel.email[0].name,
  ] : []
}
