output "alert_policy_names" {
  description = "Names of the created alert policies"
  value = [
    google_monitoring_alert_policy.backend_errors.name,
    google_monitoring_alert_policy.backend_latency.name,
  ]
}
