output "backend_url" {
  description = "URL of the backend Cloud Run service"
  value       = module.cloud_run.backend_url
}

output "frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = module.cloud_run.frontend_url
}
