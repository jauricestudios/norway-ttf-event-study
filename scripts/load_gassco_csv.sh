#!/usr/bin/env bash
# Deliberately safe for disposable *_test PostgreSQL databases ONLY.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DB_NAME="${1:-}"
CSV_PATH="$ROOT/data/staging/gassco_umm_import.csv"

if [[ ! "$DB_NAME" =~ ^[A-Za-z][A-Za-z0-9_]*_test$ ]]; then
  echo "Refusing database '${DB_NAME}': pass a disposable database name ending in _test." >&2
  exit 2
fi
for bin in python3 psql; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Missing dependency: $bin" >&2; exit 2; }
done
python3 "$ROOT/scripts/check_gassco_csv.py" "$CSV_PATH"

# PSQL meta-command \\copy is client-side and does not substitute -v variables.
# Quote the known local input path for the \\copy parser. No SQL is built from DB_NAME.
CSV_ESCAPED="${CSV_PATH//\'/\'\'}"

# Each input is checked while holding an exclusive lock in one transaction.
# ON_ERROR_STOP plus transaction guarantees that malformed loads are rolled back.
{
  printf '%s\n' \
    'BEGIN;' \
    'LOCK TABLE raw.gassco_umm_import IN ACCESS EXCLUSIVE MODE;' \
    "DO \$\$ BEGIN IF EXISTS (SELECT 1 FROM raw.gassco_umm_import LIMIT 1) THEN RAISE EXCEPTION 'Target table is not empty'; END IF; END \$\$;" \
    "\\copy raw.gassco_umm_import (message_id,asset,event_status,unavailability_type,event_type,publication_time,event_start,event_stop,unit,technical_capacity,available_capacity,unavailable_capacity,reason,remarks,balancing_zone,market_participant,market_participant_code,asset_eic_code,source_year,source_file,source_excel_row) FROM '$CSV_ESCAPED' WITH (FORMAT csv, HEADER true)"
  printf '%s\n' \
    'SELECT COUNT(*) AS raw_messages FROM raw.gassco_umm_import;' \
    'SELECT COUNT(*) AS eligible_reductions FROM mart.gassco_primary_reduction_events;' \
    'COMMIT;'
} | psql -X -v ON_ERROR_STOP=1 -d "$DB_NAME"
