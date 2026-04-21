terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3"
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_file)
}

# -----------------------------------------------------------------
# GCS bucket — raw landing zone for FEWS NET CSVs
# -----------------------------------------------------------------
resource "google_storage_bucket" "fewsnet_raw" {
  name          = "fewsnet-raw-${var.project_id}"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition { age = 90 }
    action { type = "Delete" }
  }

  uniform_bucket_level_access = true
}

# -----------------------------------------------------------------
# BigQuery datasets
# -----------------------------------------------------------------
resource "google_bigquery_dataset" "fewsnet_raw" {
  dataset_id  = "fewsnet_raw"
  location    = var.bq_location
  description = "Raw ingested tables from FEWS NET FDW API"

  labels = {
    env     = "production"
    project = "dezoomcamp"
  }
}

resource "google_bigquery_dataset" "fewsnet_dbt" {
  dataset_id  = "fewsnet_dbt"
  location    = var.bq_location
  description = "dbt-transformed FEWS NET models (staging + marts)"

  labels = {
    env     = "production"
    project = "dezoomcamp"
  }
}
