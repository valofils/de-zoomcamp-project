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
- MODULE: 2 - Kestra Workflow Orchestration
- STATUS: Complete
- LAST_COMMIT: 1515a3e - feat: add monthly schedule trigger to taxi ingestion flow
- Kestra running at port 8080 (pgAdmin at 8090)
- Flow: nyc_taxi_ingestion (de.zoomcamp namespace)
- BigQuery: 20.3M rows in food-security-pipeline.ny_taxi.yellow_tripdata (2024-01 to 2024-06)
- GCS: parquet files in food-security-pipeline-taxi-bucket
- NEXT_STEP: Module 3 - dbt transformations

## Known Pitfalls
- gcloud not in PATH by default: run source /home/codespace/google-cloud-sdk/path.bash.inc
- terraform not in PATH by default: installed to /usr/local/bin/terraform
- pip install needs: pip install -r requirements.txt (not auto-installed)
- Multi-line terminal pastes get mangled: use python3 -c or VS Code editor instead
- docker compose must be run from 01-docker-terraform/docker/ directory
- Kestra OSS secrets: use SECRET_ prefixed env vars in docker-compose, not UI
- Kestra BigQuery: use LoadFromGcs task for GCS URIs, not Load
