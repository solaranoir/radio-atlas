from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.api.dependencies import get_db


def test_get_db_yields_created_session() -> None:
    session = MagicMock(spec=Session)

    with patch(
        "app.api.dependencies.create_session",
        return_value=session,
    ):
        dependency = get_db()

        yielded = next(dependency)

        assert yielded is session

        dependency.close()


def test_get_db_closes_session_after_use() -> None:
    session = MagicMock(spec=Session)

    with patch(
        "app.api.dependencies.create_session",
        return_value=session,
    ):
        dependency = get_db()

        next(dependency)

        dependency.close()

    session.close.assert_called_once_with()


def test_get_db_closes_session_when_consumer_raises() -> None:
    session = MagicMock(spec=Session)

    with patch(
        "app.api.dependencies.create_session",
        return_value=session,
    ):
        dependency = get_db()

        next(dependency)

        with pytest.raises(
            RuntimeError,
            match="request failed",
        ):
            dependency.throw(RuntimeError("request failed"))

    session.close.assert_called_once_with()
