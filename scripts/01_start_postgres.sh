#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/01-docker-terraform/docker/docker-compose.yml"

if [[ -f "$ROOT_DIR/.env" ]]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

echo "=== Starting Postgres + pgAdmin ==="
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for Postgres to be ready..."
until docker compose -f "$COMPOSE_FILE" exec -T postgres \
    pg_isready -U "${POSTGRES_USER:-root}" -q 2>/dev/null; do
    sleep 2
    echo -n "."
done

echo ""
echo "✅ Postgres is ready!"
echo ""
echo "  Host:     localhost"
echo "  Port:     ${POSTGRES_PORT:-5432}"
echo "  DB:       ${POSTGRES_DB:-ny_taxi}"
echo "  User:     ${POSTGRES_USER:-root}"
echo "  Password: ${POSTGRES_PASSWORD:-root}"
echo ""
echo "pgAdmin: http://localhost:8080"
echo "  Email:    admin@admin.com"
echo "  Password: root"