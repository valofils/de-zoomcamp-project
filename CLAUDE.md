# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DE Zoomcamp learning project implementing a modern data stack for NYC Yellow Taxi ride analytics. The stack: Docker/Terraform (infra) → Kestra (orchestration) → BigQuery (warehouse) → dbt (transformation) → marts for BI.

GCP Project: `food-security-pipeline` | BigQuery Dataset: `ny_taxi` | GCS Bucket: `food-security-pipeline-taxi-bucket`

## Environment Setup

This runs in GitHub Codespaces. Important one-time setup steps:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Source gcloud CLI (not in PATH by default)
source /home/codespace/google-cloud-sdk/path.bash.inc

# Terraform is at /usr/local/bin/terraform (not in PATH)
export PATH=$PATH:/usr/local/bin
```

Credentials: GCP service account key at `credentials/gcp-sa-key.json`, referenced via `GOOGLE_APPLICATION_CREDENTIALS`. Copy `.env.example` → `.env` and fill in values. **Never commit `.env` or credentials.**

`~/.dbt/profiles.yml` must exist locally — never committed to git.

## Common Commands

### Docker / Local Infrastructure
```bash
cd 01-docker-terraform/docker
docker compose up -d           # Start Postgres (5432), pgAdmin (8080), Kestra (8080/8081)
docker compose down
```

### Terraform (GCP Infrastructure)
```bash
cd 01-docker-terraform/terraform
/usr/local/bin/terraform init
/usr/local/bin/terraform plan
/usr/local/bin/terraform apply
```

### dbt (Analytics Engineering)
```bash
cd 04-analytics-engineering/taxi_rides_ny

dbt deps                          # Install dbt-utils package
dbt seed                          # Load taxi_zone_lookup.csv → BigQuery dim_zones
dbt run                           # Run all models
dbt test                          # Run all data quality tests (expect 14 pass, 4 warn)
dbt build                         # seed + run + test in one command

dbt run --select stg_yellow_tripdata   # Single model
dbt run --select staging               # All staging models
dbt docs generate && dbt docs serve --port 8081
```

### Data Ingestion Scripts
```bash
./scripts/01_start_postgres.sh
./scripts/02_ingest_data.sh [YEAR] [MONTHS...]   # e.g. 2023 1 2 3
./scripts/03_setup_gcp.sh
```

## Architecture & Data Flow

```
TLC Parquet CDN (monthly files)
    → Kestra (02-kestra/flows/nyc_taxi_ingestion.yml)
        Downloads → uploads to GCS → LoadFromGcs into BigQuery raw table
    → BigQuery: ny_taxi.yellow_tripdata (raw)
    → dbt (04-analytics-engineering/taxi_rides_ny/)
        staging (views): stg_yellow_tripdata — type casts, surrogate key, snake_case, filters 2024-01 to 2024-06
        core (tables):
          dim_zones — seeded from taxi_zone_lookup.csv (265 TLC zones)
          fact_trips — 16M rows, partitioned by pickup month, clustered by vendorid/payment_type
        mart (table):
          dm_monthly_zone_revenue — monthly rollup by pickup zone
```

### dbt Schema Layout
- Staging models → `ny_taxi_staging` BigQuery schema (materialized as views)
- Core/mart models → `ny_taxi_core` BigQuery schema (materialized as tables)

### Key dbt Macro
`get_payment_type_description` in `macros/` maps numeric TLC payment codes (1=Credit, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided).

## Known Pitfalls

- **dbt location**: BigQuery dataset must be `us-central1` (not the US multi-region). Set in `~/.dbt/profiles.yml`.
- **Kestra BigQuery ingestion**: Use the `LoadFromGcs` task type for GCS URIs, not the generic `Load` task.
- **Kestra secrets**: Inject via `SECRET_`-prefixed env vars in docker-compose, not through the UI.
- **dbt test warnings**: 4 expected warnings from known TLC data quality issues (duplicate surrogate keys from vendor data, some zone IDs missing from dim_zones). These are not failures.
- **Multi-line terminal pastes**: Get mangled in Codespaces terminal — write to a file via VS Code editor or use `python3 -c "..."` instead.
- **fact_trips quality filters**: `trip_distance > 0 AND fare_amount > 0 AND passenger_count > 0` are intentional — raw TLC data contains nulls and zero-value rows.

## Project Status

Module 3 (Analytics Engineering with dbt) complete. Modules 4–7 directories exist as placeholders for future work:
- `05-data-platforms/` — advanced platforms (Spark, DuckDB)
- `06-batch/` — batch processing (PySpark)
- `07-streaming/` — streaming (Kafka, Pub/Sub)
- `workshops/dlt/` — dlt (data load tool) workshop notebook with DuckDB demo
