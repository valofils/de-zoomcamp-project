variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for GCS bucket"
  type        = string
  default     = "US"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "credentials_file" {
  description = "Path to GCP service account JSON key"
  type        = string
  default     = "../credentials/gcp-service-account.json"
}
