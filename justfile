# DBuilders Pipeline

set dotenv-load

# Birth the lake (idempotent; absolute DATA_PATH — see infra/ducklake-setup.sh)
init-lake:
    ./infra/ducklake-setup.sh

# Open a SQL session on the lake (close it before running pipelines — file lock!)
lakehouse:
    duckdb -cmd "ATTACH 'ducklake:$LAKE_CATALOG' AS lake; USE lake;"

# List everything in the lake
tables:
    duckdb -c "ATTACH 'ducklake:$LAKE_CATALOG' AS lake; SHOW ALL TABLES;"

# X-ray the catalog's bookkeeping (recorded data_path etc.)
xray:
    duckdb $LAKE_CATALOG -c "SELECT key, value FROM ducklake_metadata;"

# Run ingestion (Neon -> lake; credentials & catalog from .env)
ingest:
    uv run python ingestion/postgres_dlt.py

# Publish marts -> plain duckdb file for Evidence (the "shop window")
publish:
    ./infra/publish-for-dash.sh

# Run the Evidence dev server (after: just publish)
dashboard:
    cd dashboard && npm run sources && npm run dev
    
transform: 
        dbt run --project-dir transform

transform-debug: 
    dbt debug --project-dir transform

dagster: 
    uv run dagster dev -f orchestration/definitions.py

# Full rebuild: nuke lake, reset cursors, re-ingest from Neon (PII policy changes require this)
rebuild:
    rm -rf data
    ./infra/ducklake-setup.sh
    uv run dlt pipeline dba_ingest drop
    uv run python ingestion/postgres_dlt.py