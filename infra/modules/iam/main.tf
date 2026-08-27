resource "google_service_account" "backend" {
  account_id   = "${var.project_name}-backend"
  display_name = "Incident Response Backend Service Account"
  project      = var.project_id
}

resource "google_service_account" "frontend" {
  account_id   = "${var.project_name}-frontend"
  display_name = "Incident Response Frontend Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "backend_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/run.viewer",
    "roles/secretmanager.secretAccessor",
    "roles/cloudtrace.agent",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "frontend_roles" {
  for_each = toset([
    "roles/run.invoker",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.frontend.email}"
}
