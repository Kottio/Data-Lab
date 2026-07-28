#!/usr/bin/env bash
set -euo pipefail

# The shop window.
# Evidence's DuckDB connector autoloads only *default* DuckDB extensions; `ducklake`
# is not one of them, so Evidence cannot ATTACH the lake itself.
# We therefore copy the marts (and only the marts) into a plain DuckDB file.
# Consequence to own: the dashboard reads a SNAPSHOT — `just publish` is the refresh.

OUT="dashboard/sources/lake/dashboard.duckdb"
mkdir -p "$(dirname "$OUT")"

duckdb -c "
ATTACH 'ducklake:$LAKE_CATALOG' AS lake;
ATTACH '$OUT' AS pub;
CREATE OR REPLACE TABLE pub.mart_kpis_weekly        AS FROM lake.marts.mart_kpis_weekly;
CREATE OR REPLACE TABLE pub.mart_conversion_drivers AS FROM lake.marts.mart_conversion_drivers;
CREATE OR REPLACE TABLE pub.mart_revenue_weekly     AS FROM lake.marts.mart_revenue_weekly;
"

echo "Published -> $OUT"
duckdb "$OUT" -c "SHOW TABLES;"
