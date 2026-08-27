terraform {
  backend "gcs" {
    bucket = "incident-response-tfstate-dev"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

locals {
  required_apis = [
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "firestore.googleapis.com",
  ]
}

resource "google_project_service" "required" {
  for_each = toset(local.required_apis)

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

module "iam" {
  source       = "../../modules/iam"
  project_id   = var.project_id
  project_name = var.project_name

  depends_on = [google_project_service.required]
}

module "cloud_run" {
  source                = "../../modules/cloud_run"
  project_id            = var.project_id
  region                = var.region
  project_name          = var.project_name
  environment           = var.environment
  backend_image         = var.backend_image
  frontend_image        = var.frontend_image
  service_account_email = module.iam.backend_email

  depends_on = [google_project_service.required, module.iam]
}

module "monitoring" {
  source               = "../../modules/monitoring"
  project_id           = var.project_id
  project_name         = var.project_name
  backend_service_name = "${var.project_name}-backend"

  depends_on = [module.cloud_run]
}

module "firestore" {
  source       = "../../modules/firestore"
  project_id   = var.project_id
  project_name = var.project_name
  region       = var.region

  depends_on = [google_project_service.required]
}
