"""
Database connection and session management.
"""

from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.config import config


def get_engine():
    """Create and return a SQLAlchemy engine."""
    db = config.db
    password = quote_plus(db.password)
    url = f"postgresql://{db.user}:{password}@{db.host}:{db.port}/{db.name}"
    return create_engine(url, pool_size=5, max_overflow=10)


def get_session():
    """Create and return a new database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


# Singleton engine
_engine = None


def get_shared_engine():
    """Return a shared engine instance (singleton)."""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine
