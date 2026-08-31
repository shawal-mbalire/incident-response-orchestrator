output "alert_policy_ids" {
  description = "IDs of created alert policies"
  value = [
    google_monitoring_alert_policy.backend_errors.name,
  ]
}
