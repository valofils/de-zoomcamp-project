# FEWS NET Acute Food Insecurity Pipeline — Africa Region

## DE Zoomcamp 2025 Final Project

**Author:** Mariel ([@valofils](https://github.com/valofils))

---

## Problem Statement

Acute food insecurity in Sub-Saharan Africa affects hundreds of millions of people. The Famine Early Warning Systems Network (FEWS NET) produces IPC-compatible food security classifications and population estimates at subnational level, published three times per year. Without accessible, up-to-date infrastructure to ingest and analyse this data, tracking food crisis evolution across countries and time requires significant manual effort.

This pipeline automates the full data journey:

1. **Ingest** — pulls population estimates and area-level IPC phase classifications from the FEWS NET Data Warehouse (FDW) public API across 12 Sub-Saharan African countries
2. **Store** — lands raw CSVs in Google Cloud Storage
3. **Load** — loads partitioned, clustered tables into BigQuery
4. **Transform** — applies dbt models to produce analyst-ready marts
5. **Visualise** — Looker Studio dashboard with two tiles: current crisis snapshot and historical trend

**IPC Phase reference:**

| Phase | Label | Humanitarian relevance |
|---|---|---|
| 1 | Minimal | No intervention needed |
| 2 | Stressed | Monitoring |
| 3 | Crisis | **Intervention required** |
| 4 | Emergency | **Priority response** |
| 5 | Famine | **Maximum response** |

The standard humanitarian reporting threshold is **Phase 3+** (Crisis or worse), used by UNICEF, WFP, and OCHA.

---

## Architecture

```
FEWS NET FDW API (public, no auth)
        │
        ▼
  Kestra (orchestration — monthly schedule)
  ├── Task 1: fetch_fewsnet.py  →  GCS raw/
  ├── Task 2: load_to_bigquery.py  →  BigQuery fewsnet_raw
  └── Task 3: dbt run + test
        │
        ▼
  Google Cloud Storage
  └── gs://fewsnet-raw-<project_id>/
      ├── raw/ipc_population/<COUNTRY>/
      └── raw/ipc_phases/<COUNTRY>/
        │
        ▼
  BigQuery
  ├── fewsnet_raw.ipc_population   (partitioned: period_date, clustered: country_code)
  └── fewsnet_raw.ipc_phases       (partitioned: period_date, clustered: country_code)
        │
        ▼
  dbt Core (BigQuery adapter)
  ├── staging/
  │   ├── stg_ipc_population   (view)
  │   └── stg_ipc_phases       (view)
  └── marts/
      ├── dim_countries        (table)
      ├── fct_food_insecurity  (table)
      └── dm_crisis_trends     (table)
        │
        ▼
  Looker Studio Dashboard
  ├── Tile 1: Population by IPC phase per country (latest period, bar chart)
  └── Tile 2: Phase 3+ population trend 2017–present (line chart by country)
```

**Infrastructure provisioned by Terraform:** GCS bucket + BigQuery datasets.

---

## Technologies

| Layer | Tool |
|---|---|
| Infrastructure as Code | Terraform (GCS + BigQuery) |
| Orchestration | Kestra (Docker Compose) |
| Data Lake | Google Cloud Storage |
| Data Warehouse | BigQuery (partitioned + clustered) |
| Transformations | dbt Core (BigQuery adapter) |
| Visualisation | Looker Studio |
| Containerisation | Docker |

---

## Prerequisites

- GCP account with a project created
- Service account with roles: `Storage Admin`, `BigQuery Admin`
- Service account JSON key saved to `credentials/gcp-service-account.json` (gitignored)
- Docker and Docker Compose installed
- Python 3.10+ with packages: `requests`, `google-cloud-storage`, `google-cloud-bigquery`
- dbt Core with BigQuery adapter: `pip install dbt-bigquery`
- Terraform >= 1.3

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/valofils/de-zoomcamp-project.git
cd de-zoomcamp-project
```

### 2. Add your GCP credentials

```bash
mkdir -p credentials
cp /path/to/your-service-account-key.json credentials/gcp-service-account.json
```

### 3. Provision infrastructure with Terraform

```bash
cd project/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set your project_id
terraform init
terraform apply
```

This creates:
- GCS bucket: `fewsnet-raw-<project_id>`
- BigQuery datasets: `fewsnet_raw`, `fewsnet_dbt`

### 4. Run ingestion manually (optional — Kestra automates this)

```bash
export GCS_BUCKET=fewsnet-raw-<your-project-id>
export GCP_CREDENTIALS=../../credentials/gcp-service-account.json

# Fetch from API → GCS
python3 project/ingestion/fetch_fewsnet.py

# Load GCS → BigQuery
export BQ_PROJECT=<your-project-id>
python3 project/ingestion/load_to_bigquery.py
```

### 5. Run dbt transformations

```bash
cd project/dbt/fewsnet
export BQ_PROJECT=<your-project-id>
export GOOGLE_APPLICATION_CREDENTIALS=../../../credentials/gcp-service-account.json

dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### 6. Start Kestra (full orchestration)

```bash
cd project/kestra
docker compose up -d
```

Open the Kestra UI at http://localhost:8080, then:

1. Navigate to **Flows** → upload `flows/fewsnet_pipeline.yml`
2. Set environment variables in Kestra settings:
   - `GCS_BUCKET` = `fewsnet-raw-<project_id>`
   - `BQ_PROJECT` = `<your-project-id>`
3. **Execute** the flow manually, or let the monthly schedule run it

### 7. Dashboard

Connect Looker Studio to BigQuery:

1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. Add data source → BigQuery → project → `fewsnet_dbt`
3. Build two tiles:
   - **Tile 1** (categorical): Bar chart from `fct_food_insecurity` — latest period, population by IPC phase per country
   - **Tile 2** (temporal): Line chart from `dm_crisis_trends` — Phase 3+ trend 2017–present by country
4. Add filters: country selector, date range

**Dashboard link:** _(add after publishing)_

---

## BigQuery Table Design

### Partitioning and Clustering

Both raw tables use **monthly partitioning on `period_date`** and **clustering on `country_code`**:

```sql
-- Example: query only Ethiopia, last 2 years
-- Partition pruning eliminates ~90% of scanned data
SELECT *
FROM `fewsnet_raw.ipc_population`
WHERE country_code = 'ET'
  AND period_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
```

FEWS NET data is sparse (12 countries, ~3 periods/year) so clustering on `country_code` efficiently co-locates each country's rows, minimising bytes scanned in per-country dashboard queries.

---

## Project Structure

```
project/
├── terraform/
│   ├── main.tf                  # GCS bucket + BQ datasets
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── kestra/
│   ├── docker-compose.yml
│   └── flows/
│       └── fewsnet_pipeline.yml  # Full pipeline: ingest → load → dbt
├── ingestion/
│   ├── fetch_fewsnet.py          # API → GCS
│   └── load_to_bigquery.py       # GCS → BigQuery
└── dbt/
    └── fewsnet/
        ├── dbt_project.yml
        ├── profiles.yml
        ├── packages.yml
        ├── models/
        │   ├── staging/
        │   │   ├── sources.yml
        │   │   ├── schema.yml
        │   │   ├── stg_ipc_population.sql
        │   │   └── stg_ipc_phases.sql
        │   └── marts/
        │       ├── schema.yml
        │       ├── dim_countries.sql
        │       ├── fct_food_insecurity.sql
        │       └── dm_crisis_trends.sql
        └── tests/
            ├── assert_no_negative_population.sql
            └── assert_crisis_trends_phase_sum.sql
```

---

## Countries Covered

Ethiopia (ET), Madagascar (MG), Kenya (KE), Somalia (SO), Sudan (SD), South Sudan (SS), Mali (ML), Burkina Faso (BF), Niger (NE), Chad (TD), Mozambique (MZ), Malawi (MW)

---

## Data Source

[FEWS NET Data Warehouse (FDW) API](https://fdw.fews.net/api/) — public, no authentication required.

FEWS NET is funded by USAID and produces IPC-compatible food security analysis across ~35 countries.
