"""SQLAlchemy database engine, session, and base-model configuration."""

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker , Session

from backend.core.config import get_settings


settings = get_settings()

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False , 
    bind=engine
    )

class Base(DeclarativeBase):
    """Provide the declarative base class for all ORM models."""

    pass

def get_db():
    """Provide one database session per request and close it afterwards.

    Yields:
        Session: An active SQLAlchemy database session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
