variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "backend_image" {
  description = "Docker image for the backend service"
  type        = string
}

variable "frontend_image" {
  description = "Docker image for the frontend service"
  type        = string
}
