terraform {
  required_version = ">= 1.7"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "taxi_bucket" {
  name          = "${var.project_id}-taxi-bucket"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }

  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "taxi_dataset" {
  dataset_id = var.bq_dataset
  location   = var.region

  labels = {
    env     = "dev"
    project = "de-zoomcamp"
  }
}

resource "google_service_account" "de_sa" {
  account_id   = "de-zoomcamp-sa"
  display_name = "DE Zoomcamp Service Account"
}

resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.de_sa.email}"
}

resource "google_project_iam_member" "sa_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.de_sa.email}"
}