# flake8: noqa
import humanize
from typing import Any

import dlt
from dlt.sources.sql_database import sql_database

def load_select_tables_from_database() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="dba_ingest", 
        destination='ducklake', 
        dataset_name="raw")
    
    source = sql_database().with_resources("students", "event", "progress", "enrollments", "payments" )

    source.students.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
        write_disposition='merge'
    )
    source.event.apply_hints(
        incremental=dlt.sources.incremental("created_at"),
        write_disposition='append')
    
    source.progress.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
        write_disposition='merge'
    )
    
    source.enrollments.apply_hints(
        incremental=dlt.sources.incremental("updated_at"),
        write_disposition='merge'
    )
    
    source.payments.apply_hints(
        incremental=dlt.sources.incremental("created_at"),
        write_disposition='append'
    )

    info = pipeline.run(source) 
    print(info)


if __name__ == "__main__":
    load_select_tables_from_database()