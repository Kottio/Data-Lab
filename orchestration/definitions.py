"""Dagster definitions — the dbt models as software-defined assets.

Phase 4, step 1: dbt only. dlt ingestion comes next, upstream of these.

Run it:  just dagster   (the justfile's `set dotenv-load` supplies
                         LAKE_CATALOG / LAKE_SCRATCH, which profiles.yml reads)
"""
import os
from pathlib import Path
from dagster import Definitions
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
# from dotenv import load_dotenv
from dagster_dlt import DagsterDltResource, dlt_assets
from ingestion.postgres_dlt import build_pipeline,build_source
from dagster import AssetSelection, DefaultScheduleStatus, ScheduleDefinition, define_asset_job



# ── dlt: raw ingestion (Neon → lake), upstream of dbt ──────────────
@dlt_assets(
    dlt_source=build_source(),
    dlt_pipeline=build_pipeline(),
    name="dba_ingest",
    group_name="ingestion"
)

def ingest_assest(context, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

# REPO_ROOT = Path(__file__).parent.parent
# load_dotenv()

dbt_project = DbtProject(
    project_dir=os.getenv('DBT_PROJECT_PATH'),
    profiles_dir=os.getenv('DBT_PROFILE_PATH'),
)

@dbt_assets( manifest=dbt_project.manifest_path)


def transform_assets(context, dbt: DbtCliResource):
    """One Dagster asset per dbt model, dependencies read from manifest.json."""
    yield from dbt.cli(["build"], context=context).stream()


daily_job = define_asset_job(
    "daily_pipeline",
    selection=AssetSelection.all(),   # dlt + dbt; order comes from the graph, as always
)

daily_schedule = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 6 * * *",            # every day 06:00
    execution_timezone="Europe/Paris",    # otherwise cron is interpreted in UTC
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    assets=[ingest_assest,transform_assets],
    jobs=[daily_job],
    schedules=[daily_schedule],
    resources={
        "dbt": DbtCliResource(
        project_dir=dbt_project,
        dbt_executable=os.getenv("DBT_EXECUTABLE", "dbt")),
        "dlt": DagsterDltResource()
               },
)

