"""
load_to_bigquery.py
-------------------
Loads the latest raw CSVs from GCS into BigQuery partitioned/clustered tables.

Reads from:
    gs://<GCS_BUCKET>/raw/ipc_population/<COUNTRY>/<timestamp>.csv
    gs://<GCS_BUCKET>/raw/ipc_phases/<COUNTRY>/<timestamp>.csv

Loads into:
    fewsnet_raw.ipc_population   — partitioned by period_date, clustered by country_code
    fewsnet_raw.ipc_phases       — partitioned by period_date, clustered by country_code

Environment variables (required):
    GCS_BUCKET       — e.g. fewsnet-raw-<project_id>
    BQ_PROJECT       — GCP project ID
    GCP_CREDENTIALS  — path to service account JSON (optional if ADC)
"""

import os
import logging
from google.cloud import bigquery, storage
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

GCS_BUCKET      = os.environ["GCS_BUCKET"]
BQ_PROJECT      = os.environ["BQ_PROJECT"]
BQ_RAW_DATASET  = os.environ.get("BQ_RAW_DATASET", "fewsnet_raw")
GCP_CREDS       = os.environ.get("GCP_CREDENTIALS")

# Map: GCS prefix → (BQ table, partition field, cluster fields)
TABLE_CONFIG = {
    "raw/ipc_population": (
        "ipc_population",
        "projection_start",
        ["country_code", "scenario"],
    ),
    "raw/ipc_phases": (
        "ipc_phases",
        "projection_start",
        ["country_code", "scenario"],
    ),
}


def get_clients():
    if GCP_CREDS:
        creds = service_account.Credentials.from_service_account_file(GCP_CREDS)
        bq  = bigquery.Client(project=BQ_PROJECT, credentials=creds)
        gcs = storage.Client(credentials=creds)
    else:
        bq  = bigquery.Client(project=BQ_PROJECT)
        gcs = storage.Client()
    return bq, gcs


def get_latest_blobs(gcs_client: storage.Client, prefix: str) -> dict[str, str]:
    """
    For each country subfolder under prefix, find the newest blob.
    Returns dict: country_code → gs:// URI
    """
    bucket = gcs_client.bucket(GCS_BUCKET)
    blobs  = list(bucket.list_blobs(prefix=prefix + "/"))

    country_latest: dict[str, tuple] = {}
    for blob in blobs:
        if not blob.name.endswith(".csv"):
            continue
        # path: raw/ipc_population/ET/20240101T000000.csv
        parts = blob.name.split("/")
        if len(parts) < 4:
            continue
        cc = parts[2]
        if cc not in country_latest or blob.updated > country_latest[cc][0]:
            country_latest[cc] = (blob.updated, f"gs://{GCS_BUCKET}/{blob.name}")

    return {cc: v[1] for cc, v in country_latest.items()}


def load_table(bq_client: bigquery.Client, uris: list[str],
               table_name: str, partition_field: str,
               cluster_fields: list[str]) -> None:
    table_ref = f"{BQ_PROJECT}.{BQ_RAW_DATASET}.{table_name}"
    log.info("Loading %d URIs → %s", len(uris), table_ref)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_jagged_rows=True,
        allow_quoted_newlines=True,
        max_bad_records=100,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.MONTH,
            field=partition_field,
        ),
        clustering_fields=cluster_fields,
    )

    job = bq_client.load_table_from_uri(uris, table_ref, job_config=job_config)
    job.result()  # wait
    table = bq_client.get_table(table_ref)
    log.info("Loaded → %s (%d rows)", table_ref, table.num_rows)


def run_load() -> None:
    log.info("=== BQ load START ===")
    bq, gcs = get_clients()

    for gcs_prefix, (table_name, partition_field, cluster_fields) in TABLE_CONFIG.items():
        country_uris = get_latest_blobs(gcs, gcs_prefix)
        if not country_uris:
            log.warning("No blobs found under %s — skipping", gcs_prefix)
            continue

        uris = list(country_uris.values())
        log.info("%s: found %d country slices", gcs_prefix, len(uris))
        load_table(bq, uris, table_name, partition_field, cluster_fields)

    log.info("=== BQ load DONE ===")


if __name__ == "__main__":
    run_load()
