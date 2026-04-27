import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _get_postgres_driver() -> str:
    try:
        import psycopg  # noqa: F401

        return "postgresql+psycopg"
    except ModuleNotFoundError:
        try:
            import psycopg2  # noqa: F401

            return "postgresql+psycopg2"
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PostgreSQL driver not installed. Install `psycopg[binary]` "
                "or `psycopg2-binary`, or run the app with this project's "
                "virtual environment where the driver is already available."
            ) from exc


DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    drivername=_get_postgres_driver(),
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "Bala@1612"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "enterprisecollab"),
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
