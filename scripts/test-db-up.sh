#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT/docker-compose.yml"
SERVICE="postgres"
DB_HOST="localhost"
DB_PORT="55432"
DB_SUPERUSER="postgres"
DB_PASSWORD="postgres"
DB_NAME="eventsaas"
DB_SCHEMA="seriema"
DATABASE_URL="postgresql://postgres:postgres@localhost:55432/eventsaas"

export PATH="/home/node/.openclaw/workspace/bin:$PATH"

if command -v docker >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "Erro: docker compose não encontrado no PATH." >&2
  exit 1
fi

cd "$ROOT"

"${COMPOSE[@]}" -f "$COMPOSE_FILE" up -d "$SERVICE"

if ! command -v psql >/dev/null 2>&1; then
  echo "Postgres solicitado. Valide manualmente com o cliente Postgres de sua preferência." >&2
  exit 0
fi

until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c 'select 1' >/dev/null 2>&1; do
  echo "Aguardando Postgres local em ${DB_HOST}:${DB_PORT}..."
  sleep 2
done

if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
  PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_SUPERUSER\";"
fi

PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -c "CREATE SCHEMA IF NOT EXISTS \"$DB_SCHEMA\" AUTHORIZATION \"$DB_SUPERUSER\";"

echo 'Postgres de teste pronto:'
echo "  DATABASE_URL=$DATABASE_URL"
echo "  SERIEMA_DB_SCHEMA=$DB_SCHEMA"
