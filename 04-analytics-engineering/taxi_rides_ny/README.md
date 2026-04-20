# Module 4 — Analytics Engineering (dbt)

## Project: `taxi_rides_ny`

Transforms raw NYC Yellow Taxi data in BigQuery using dbt.

## DAG

```
taxi_zone_lookup (seed CSV)
       │
       ▼
  dim_zones  ◄────────────────────────────────────────────────┐
                                                               │
yellow_tripdata (BQ raw)                                       │
       │                                                       │
       ▼                                                       │
stg_yellow_tripdata (view)                                     │
       │                                                       │
       ▼                                                       │
  fact_trips (table, partitioned+clustered) ──► dm_monthly_zone_revenue (table)
```

## Setup

### 1. Install dbt

```bash
pip install dbt-bigquery==1.8.2
```

### 2. Place profiles.yml

Copy `profiles.yml` to `~/.dbt/profiles.yml` OR use `--profiles-dir .` flag.

```bash
mkdir -p ~/.dbt
cp profiles.yml ~/.dbt/profiles.yml
```

### 3. Install packages

```bash
cd 04-analytics-engineering/taxi_rides_ny
dbt deps
```

### 4. Seed the taxi zone lookup

```bash
dbt seed
```

This loads `seeds/taxi_zone_lookup.csv` into `food-security-pipeline.ny_taxi_staging.taxi_zone_lookup`.

### 5. Run all models

```bash
dbt run
```

### 6. Run tests

```bash
dbt test
```

### 7. Generate and serve docs

```bash
dbt docs generate
dbt docs serve --port 8081
```
(In Codespaces, forward port 8081 and open in browser)

## Models

| Model | Schema | Type | Description |
|-------|--------|------|-------------|
| `stg_yellow_tripdata` | `ny_taxi_staging` | View | Cleaned + cast raw yellow taxi data |
| `dim_zones` | `ny_taxi_core` | Table | TLC Taxi Zone dimension from seed |
| `fact_trips` | `ny_taxi_core` | Table (partitioned) | Core fact table with zone enrichment |
| `dm_monthly_zone_revenue` | `ny_taxi_core` | Table | Monthly revenue rollup by zone |

## BigQuery Output Schemas

dbt appends `_<schema_name>` to the dataset by default:
- Staging views → `ny_taxi_staging`
- Core tables  → `ny_taxi_core`

To use a single dataset, set `+schema:` to empty in `dbt_project.yml` or override in `profiles.yml`.

## Useful Commands

```bash
# Run only staging
dbt run --select staging

# Run only core
dbt run --select core

# Run a single model
dbt run --select fact_trips

# Run + test together
dbt build

# Check compiled SQL without running
dbt compile --select fact_trips
cat target/compiled/taxi_rides_ny/models/core/fact_trips.sql
```
