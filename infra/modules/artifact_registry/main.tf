resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "${var.project_name}-images"
  description   = "Docker images for ${var.project_name}"
  format        = "DOCKER"
  project       = var.project_id
}
