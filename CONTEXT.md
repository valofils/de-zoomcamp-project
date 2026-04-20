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
- SA_EMAIL=de-zoomcamp-sa@food-security-pipeline.iam.gserviceaccount.com

## Current State
- MODULE: 1 - Containerization & Infrastructure as Code
- STATUS: Complete
- LAST_COMMIT: 1a4dbcf - fix: gitignore terraform.tfvars
- GCP authenticated as: valofils@gmail.com
- Postgres running: 3,041,717 rows in yellow_taxi_trips
- GCS bucket provisioned
- BigQuery dataset provisioned
- NEXT_STEP: Module 2 - Kestra workflow orchestration

## Known Pitfalls
- gcloud not in PATH by default: run source /home/codespace/google-cloud-sdk/path.bash.inc
- terraform not in PATH by default: installed to /usr/local/bin/terraform
- pip install needs: pip install -r requirements.txt (not auto-installed)
- Multi-line terminal pastes get mangled: use python3 -c or VS Code editor instead