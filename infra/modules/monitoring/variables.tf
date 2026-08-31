variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "backend_service_name" {
  description = "Cloud Run backend service name"
  type        = string
}
