"""Dagster definitions — the dbt models as software-defined assets.

Phase 4, step 1: dbt only. dlt ingestion comes next, upstream of these.

Run it:  just dagster   (the justfile's `set dotenv-load` supplies
                         LAKE_CATALOG / LAKE_SCRATCH, which profiles.yml reads)
"""

from pathlib import Path

from dagster import Definitions
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

REPO_ROOT = Path(__file__).parent.parent

# profiles.yml lives at the repo root, not inside transform/ — hence profiles_dir.
dbt_project = DbtProject(
    project_dir=REPO_ROOT / "transform",
    profiles_dir=REPO_ROOT,
)


@dbt_assets(manifest=dbt_project.manifest_path)
def transform_assets(context, dbt: DbtCliResource):
    """One Dagster asset per dbt model, dependencies read from manifest.json."""
    yield from dbt.cli(["build"], context=context).stream()


defs = Definitions(
    assets=[transform_assets],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
)
