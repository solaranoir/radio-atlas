from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@lru_cache
def get_engine() -> Engine:
    settings = Settings()

    return create_engine(
        settings.radio_atlas_database_url,
    )


def create_session() -> Session:
    session_factory = sessionmaker(
        bind=get_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )

    return session_factory()
