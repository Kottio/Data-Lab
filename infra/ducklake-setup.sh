#!/usr/bin/env bash
set -euo pipefail   # stop on any error

# Birth certificate of the lake. Idempotent — safe to re-run.
# so every client (dlt, dbt, CLI) can announce the identical string. (See Knowledge Center note.)

mkdir -p data

duckdb -c "INSTALL ducklake;"
duckdb -c "ATTACH 'ducklake:data/lake_catalog.ducklake' AS lake (DATA_PATH '$(pwd)/data/lake_files/');"
#duckdb -c "ATTACH 'ducklake:$LAKE_CATALOG' AS lake (DATA_PATH '$(pwd)/data/lake_files/');"

echo "Lake ready:"
duckdb $LAKE_CATALOG -c "SELECT key, value FROM ducklake_metadata WHERE key='data_path';"
