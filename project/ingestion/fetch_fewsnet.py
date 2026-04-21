"""
fetch_fewsnet.py
----------------
Fetches FEWS NET FDW API data (IPC population estimates + IPC phase
classifications) for target African countries and uploads raw CSVs
to a GCS bucket.

Usage:
    python3 fetch_fewsnet.py

Environment variables (required):
    GCS_BUCKET      — GCS bucket name, e.g. fewsnet-raw-<project_id>
    GCP_CREDENTIALS — Path to service account JSON (optional if ADC is set)

Optional overrides:
    START_DATE      — YYYY-MM-DD (default: 2017-01-01)
    END_DATE        — YYYY-MM-DD (default: today)
"""

import os
import io
import logging
from datetime import date, datetime

import requests
from google.cloud import storage
from google.oauth2 import service_account

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

FDW_BASE = "https://fdw.fews.net/api"

# Africa countries covered by FEWS NET
TARGET_COUNTRIES = [
    "ET",  # Ethiopia
    "MG",  # Madagascar
    "KE",  # Kenya
    "SO",  # Somalia
    "SD",  # Sudan
    "SS",  # South Sudan
    "ML",  # Mali
    "BF",  # Burkina Faso
    "NE",  # Niger
    "TD",  # Chad
    "MZ",  # Mozambique
    "MW",  # Malawi
]

COUNTRY_NAMES = {
    "ET": "Ethiopia", "MG": "Madagascar", "KE": "Kenya",
    "SO": "Somalia", "SD": "Sudan", "SS": "South Sudan",
    "ML": "Mali", "BF": "Burkina Faso", "NE": "Niger",
    "TD": "Chad", "MZ": "Mozambique", "MW": "Malawi",
}

ENDPOINTS = {
    "ipc_population": "ipcpopulationsize.csv",
    "ipc_phases":     "ipcphase.csv",
}

GCS_BUCKET  = os.environ["GCS_BUCKET"]
START_DATE  = os.environ.get("START_DATE", "2017-01-01")
END_DATE    = os.environ.get("END_DATE",   date.today().isoformat())
GCP_CREDS   = os.environ.get("GCP_CREDENTIALS")


# ---------------------------------------------------------------------------
# GCS client
# ---------------------------------------------------------------------------
def get_gcs_client() -> storage.Client:
    if GCP_CREDS:
        creds = service_account.Credentials.from_service_account_file(GCP_CREDS)
        return storage.Client(credentials=creds)
    return storage.Client()   # falls back to ADC / Workload Identity


# ---------------------------------------------------------------------------
# API fetch
# ---------------------------------------------------------------------------
def fetch_endpoint(endpoint: str, country_code: str,
                   start_date: str, end_date: str) -> bytes | None:
    """
    Fetch one country slice from a FEWS NET FDW endpoint.
    Returns raw CSV bytes or None on failure.
    """
    url = f"{FDW_BASE}/{endpoint}"
    params = {
        "country_code": country_code,
        "start_date":   start_date,
        "end_date":     end_date,
    }
    try:
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        if not resp.content.strip():
            log.warning("Empty response for %s / %s", endpoint, country_code)
            return None
        return resp.content
    except requests.RequestException as exc:
        log.error("Failed to fetch %s / %s: %s", endpoint, country_code, exc)
        return None


# ---------------------------------------------------------------------------
# GCS upload
# ---------------------------------------------------------------------------
def upload_to_gcs(client: storage.Client, data: bytes,
                  gcs_path: str, content_type: str = "text/csv") -> None:
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(gcs_path)
    blob.upload_from_file(io.BytesIO(data), content_type=content_type)
    log.info("Uploaded → gs://%s/%s (%d bytes)", GCS_BUCKET, gcs_path, len(data))


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_ingestion() -> None:
    log.info("=== FEWS NET ingestion START ===")
    log.info("Period: %s → %s", START_DATE, END_DATE)
    log.info("Countries: %s", ", ".join(TARGET_COUNTRIES))

    client = get_gcs_client()

    # Timestamp label for this run's folder
    run_ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    total_ok = 0
    total_skip = 0

    for dataset_key, endpoint in ENDPOINTS.items():
        log.info("--- Endpoint: %s ---", endpoint)
        for cc in TARGET_COUNTRIES:
            log.info("  Fetching %s / %s …", endpoint, cc)
            data = fetch_endpoint(endpoint, cc, START_DATE, END_DATE)

            if data is None:
                total_skip += 1
                continue

            # GCS path: raw/ipc_population/ET/2024XXXXXXT000000.csv
            gcs_path = f"raw/{dataset_key}/{cc}/{run_ts}.csv"
            upload_to_gcs(client, data, gcs_path)
            total_ok += 1

    log.info(
        "=== FEWS NET ingestion DONE | uploaded=%d skipped=%d ===",
        total_ok, total_skip,
    )


if __name__ == "__main__":
    run_ingestion()
