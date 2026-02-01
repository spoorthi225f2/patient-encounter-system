from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for MySQL/PyMySQL
DATABASE_URL = "mysql+pymysql://mongouhd_evernorth:U*dgQkKRuEHe@cp-15.webhostbox.net:3306/mongouhd_evernorth"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Naming convention for tables
metadata = MetaData(
    naming_convention={
        "ix": "ix_spoorthi_%(column_0_label)s",
        "uq": "uq_spoorthi_%(table_name)s_%(column_0_name)s",
        "ck": "ck_spoorthi_%(table_name)s_%(constraint_name)s",
        "fk": "fk_spoorthi_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_spoorthi_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
