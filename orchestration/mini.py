
from dagster import Definitions, asset

@asset
def students():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bob"}]

@asset
def student_count(students):
    return len(students)

defs = Definitions(assets=[students, student_count])


from dagster import Definitions, asset, ConfigurableResource
import duckdb

class Database(ConfigurableResource):
    path: str                                      # config, declared once

    def query(self, sql):
        with duckdb.connect(self.path) as conn:
            return conn.execute(sql).fetchall()

@asset
def students(db: Database):                        # ← injected
    return db.query("select * from students")

defs = Definitions(
    assets=[students],
    resources={"db": Database(path="/tmp/lake.duckdb")},   # configured HERE, once
)