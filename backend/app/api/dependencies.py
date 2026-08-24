from collections.abc import Generator

from sqlalchemy.orm import Session

from app.infrastructure.database.session import create_session


def get_db() -> Generator[Session, None, None]:
    session = create_session()

    try:
        yield session
    finally:
        session.close()
