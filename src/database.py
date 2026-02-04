import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables (.env for local)
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Database URL
# - Local: MySQL from .env
# - CI/Test: SQLite in-memory fallback
# -------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+pysqlite:///./test.db"  # fallback for CI / tests
)

# -------------------------------------------------
# SQLAlchemy Engine
# -------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# -------------------------------------------------
# Session factory
# -------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -------------------------------------------------
# Naming convention (production-grade)
# -------------------------------------------------
metadata = MetaData(
    naming_convention={
        "ix": "ix_spoorthi_%(column_0_label)s",
        "uq": "uq_spoorthi_%(table_name)s_%(column_0_name)s",
        "ck": "ck_spoorthi_%(table_name)s_%(constraint_name)s",
        "fk": "fk_spoorthi_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_spoorthi_%(table_name)s",
    }
)

# -------------------------------------------------
# Declarative Base (SQLAlchemy 2.0 compatible)
# -------------------------------------------------
Base = declarative_base(metadata=metadata)


# -------------------------------------------------
# Dependency for FastAPI
# -------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
