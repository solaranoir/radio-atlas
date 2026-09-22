from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    settings = Settings()

    engine = create_engine(settings.radio_atlas_database_url)

    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()
        engine.dispose()
