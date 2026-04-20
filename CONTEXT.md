# DE Zoomcamp Project — CONTEXT.md
# Paste this file at the start of every new Claude chat to restore full context.

## Project Identity
- **Repo**: https://github.com/valofils/de-zoomcamp-project
- **Dataset**: NYC Yellow Taxi Rides (TLC parquet files)
- **Environment**: GitHub Codespaces + VS Code
- **Python**: 3.12

## Key Config
- POSTGRES_HOST=localhost
- POSTGRES_PORT=5432
- POSTGRES_DB=ny_taxi
- POSTGRES_USER=root
- POSTGRES_PASSWORD=root
- GCP_PROJECT_ID=food-security-pipeline
- GCP_REGION=us-central1
- GCS_BUCKET=food-security-pipeline-taxi-bucket
- BQ_DATASET=ny_taxi
- SA_EMAIL=food-security-pipeline@food-security-pipeline.iam.gserviceaccount.com
- GCP_KEY=/home/codespace/.gcp/gcp-key.json

## Current State
- MODULE: 3 - Analytics Engineering (dbt)
- STATUS: Complete
- LAST_COMMIT: d18a79c - chore: remove profiles.yml from tracking
- dbt project: 04-analytics-engineering/taxi_rides_ny/
- BigQuery staging: ny_taxi_staging.stg_yellow_tripdata (view)
- BigQuery core: ny_taxi_core.dim_zones (255 rows), ny_taxi_core.fact_trips (16.1M rows), ny_taxi_core.dm_monthly_zone_revenue (1.4k rows)
- dbt tests: 14 pass, 4 warn (expected TLC data quality issues), 0 errors
- NEXT_STEP: Module 4 - Data Ingestion (dlt workshop) or Module 5 - Batch (Spark)

## Known Pitfalls
- gcloud not in PATH by default: run source /home/codespace/google-cloud-sdk/path.bash.inc
- terraform not in PATH by default: installed to /usr/local/bin/terraform
- pip install needs: pip install -r requirements.txt (not auto-installed)
- Multi-line terminal pastes get mangled: use python3 -c or VS Code editor instead
- docker compose must be run from 01-docker-terraform/docker/ directory
- Kestra OSS secrets: use SECRET_ prefixed env vars in docker-compose, not UI
- Kestra BigQuery: use LoadFromGcs task for GCS URIs, not Load
- dbt location must match BQ dataset: us-central1 (not US)
- dbt profiles.yml: keep only at ~/.dbt/profiles.yml, never commit to git
- dbt target/, dbt_packages/, logs/ are gitignored
