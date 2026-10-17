from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from app.config import get_settings

settings = get_settings()

# Ensure we use postgresql+psycopg2 dialect if provided as postgresql://
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Connection engine tuned for Neon Cloud Serverless PostgreSQL with pooling
engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,      # Tests connection liveness before checkout
    pool_recycle=300,        # Recycles connections every 5 mins to prevent stale sockets
    connect_args={
        "sslmode": "require"
    } if "neon.tech" in db_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session per request.
    Guarantees session cleanup upon completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes database tables defined in SQLAlchemy models.
    Safe to execute on application startup.
    """
    # Import models here to ensure they are registered with Base metadata
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)
