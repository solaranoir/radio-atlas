from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.replay.session.expiry import cleanup_expired_replay_sessions


def test_cleanup_uses_ttl_to_calculate_cutoff() -> None:
    db = Mock(spec=Session)
    now = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)

    with pytest.MonkeyPatch.context() as monkeypatch:
        delete_mock = Mock(return_value=3)
        monkeypatch.setattr(
            "app.replay.session.expiry.delete_replay_sessions_updated_before",
            delete_mock,
        )

        deleted_count = cleanup_expired_replay_sessions(
            db,
            now=now,
            ttl_seconds=3600,
        )

    cutoff = datetime(2026, 9, 29, 11, 0, tzinfo=UTC)

    delete_mock.assert_called_once_with(db, cutoff)
    assert deleted_count == 3


@pytest.mark.parametrize("ttl_seconds", [0, -1])
def test_cleanup_rejects_non_positive_ttl(ttl_seconds: int) -> None:
    db = Mock(spec=Session)
    now = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="replay session TTL must be greater than zero",
    ):
        cleanup_expired_replay_sessions(
            db,
            now=now,
            ttl_seconds=ttl_seconds,
        )
