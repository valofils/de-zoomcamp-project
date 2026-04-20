#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

YEAR="${1:-2023}"
shift || true
MONTHS="${@:-1}"

echo "=== NYC Taxi Data Ingestion ==="
echo "Year: $YEAR  |  Months: $MONTHS"
echo ""

python "$ROOT_DIR/01-docker-terraform/ingest/ingest_data.py" \
    --year "$YEAR" \
    --months $MONTHS \
    --host     "${POSTGRES_HOST:-localhost}" \
    --port     "${POSTGRES_PORT:-5432}" \
    --db       "${POSTGRES_DB:-ny_taxi}" \
    --user     "${POSTGRES_USER:-root}" \
    --password "${POSTGRES_PASSWORD:-root}"