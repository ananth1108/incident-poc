from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

engine = None
SessionLocal = None


def _init_engine():
    global engine, SessionLocal
    # recreate if url changed
    if engine is None or str(engine.url) != settings.db_url:
        kwargs = {}
        if settings.db_url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        engine = create_engine(settings.db_url, **kwargs)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def init_db():
    eng = _init_engine()
    from .models import Base
    Base.metadata.create_all(bind=eng)
