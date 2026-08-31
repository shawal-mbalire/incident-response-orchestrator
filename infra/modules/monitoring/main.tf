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
}
