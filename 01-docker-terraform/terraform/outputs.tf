output "gcs_bucket_name" {
  value       = google_storage_bucket.taxi_bucket.name
  description = "GCS bucket for raw data"
}

output "bq_dataset_id" {
  value       = google_bigquery_dataset.taxi_dataset.dataset_id
  description = "BigQuery dataset"
}

output "service_account_email" {
  value       = google_service_account.de_sa.email
  description = "Service account email"
}