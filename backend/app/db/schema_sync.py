from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_schema(engine: Engine):
    inspector = inspect(engine)
    if "tasks" not in inspector.get_table_names():
        return

    task_columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "updated_by" not in task_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE tasks ADD COLUMN updated_by INTEGER"))
            connection.execute(
                text(
                    "ALTER TABLE tasks "
                    "ADD CONSTRAINT tasks_updated_by_fkey "
                    "FOREIGN KEY (updated_by) REFERENCES users(id)"
                )
            )
