from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_schema(engine: Engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "tasks" not in tables:
        return

    task_columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "updated_by" not in task_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE tasks ADD COLUMN updated_by INTEGER"))

    if "users" in tables:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        missing_user_columns = {
            "refresh_token_hash": "VARCHAR",
            "refresh_token_expires_at": "TIMESTAMP",
            "password_reset_token_hash": "VARCHAR",
            "password_reset_expires_at": "TIMESTAMP",
            "tenant_id": "INTEGER",
        }
        with engine.begin() as connection:
            for column_name, column_type in missing_user_columns.items():
                if column_name not in user_columns:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))

    # Subscriptions table enhancements
    if "subscriptions" in tables:
        sub_columns = {column["name"] for column in inspector.get_columns("subscriptions")}
        missing_sub_columns = {
            "billing_cycle_start": "TIMESTAMP",
            "billing_cycle_end": "TIMESTAMP",
            "is_active": "BOOLEAN",
            "updated_at": "TIMESTAMP",
        }
        with engine.begin() as connection:
            for column_name, column_type in missing_sub_columns.items():
                if column_name not in sub_columns:
                    connection.execute(text(f"ALTER TABLE subscriptions ADD COLUMN {column_name} {column_type}"))
