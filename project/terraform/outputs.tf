output "gcs_bucket_name" {
  description = "GCS raw bucket name"
  value       = google_storage_bucket.fewsnet_raw.name
}

output "bq_raw_dataset" {
  description = "BigQuery raw dataset ID"
  value       = google_bigquery_dataset.fewsnet_raw.dataset_id
}

output "bq_dbt_dataset" {
  description = "BigQuery dbt dataset ID"
  value       = google_bigquery_dataset.fewsnet_dbt.dataset_id
}
