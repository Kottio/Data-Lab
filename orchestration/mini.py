
from dagster import Definitions, asset

@asset
def students():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bob"}]

@asset
def student_count(students):
    return len(students)

defs = Definitions(assets=[students, student_count])

