from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.analytics.aggregation.runtime import run_daily_job
from app.analytics.anomalies.baselines_cli import format_coverage, main
from app.analytics.anomalies.runtime import run_baseline_refresh
from app.analytics.anomalies.service import BaselineRefreshResult


def _factory(session: MagicMock) -> MagicMock:
    factory = MagicMock()
    factory.return_value.__enter__.return_value = session
    return factory


def _result() -> BaselineRefreshResult:
    return BaselineRefreshResult(
        baseline_version="v",
        as_of=datetime(2026, 11, 20, tzinfo=UTC),
        snapshot_count=2,
        band_dimensions=1,
        station_dimensions=0,
        coverage={("band", "hour", "observation_count", "sufficient"): 2},
        pruned_rows=0,
    )


def test_refresh_uses_start_of_utc_day_and_commits() -> None:
    session = MagicMock(spec=Session)
    with patch(
        "app.analytics.anomalies.runtime.refresh_baselines", return_value=_result()
    ) as refresh:
        run_baseline_refresh(
            now=datetime(2026, 11, 20, 17, 42, tzinfo=UTC), session_factory=_factory(session)
        )

    assert refresh.call_args.kwargs["as_of"] == datetime(2026, 11, 20, tzinfo=UTC)
    session.commit.assert_called_once_with()


def test_refresh_failure_is_logged_not_raised() -> None:
    session = MagicMock(spec=Session)
    with patch(
        "app.analytics.anomalies.runtime.refresh_baselines", side_effect=RuntimeError("boom")
    ):
        run_baseline_refresh(session_factory=_factory(session))

    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [True, False])
async def test_daily_job_refreshes_baselines_only_when_enabled(enabled: bool) -> None:
    settings = MagicMock(radio_atlas_baselines_enabled=enabled)
    with (
        patch("app.analytics.aggregation.runtime._run_refresh"),
        patch("app.analytics.aggregation.runtime.get_settings", return_value=settings),
        patch("app.analytics.aggregation.runtime.run_baseline_refresh") as refresh,
    ):
        await run_daily_job()

    assert refresh.called is enabled


def test_cli_dry_run_does_not_write(capsys: pytest.CaptureFixture[str]) -> None:
    session = MagicMock(spec=Session)
    with (
        patch("app.analytics.anomalies.baselines_cli.create_session", _factory(session)),
        patch("app.analytics.anomalies.baselines_cli.compute_baselines", return_value=[]) as comp,
        patch("app.analytics.anomalies.baselines_cli.replace_baselines") as replace_,
    ):
        assert main(["--as-of", "2026-11-20", "--no-stations"]) == 0

    assert comp.call_args.kwargs["as_of"] == datetime(2026, 11, 20, tzinfo=UTC)
    assert comp.call_args.kwargs["include_stations"] is False
    replace_.assert_not_called()
    session.commit.assert_not_called()
    assert "dry run" in capsys.readouterr().out


def test_cli_write_replaces_and_commits() -> None:
    session = MagicMock(spec=Session)
    with (
        patch("app.analytics.anomalies.baselines_cli.create_session", _factory(session)),
        patch("app.analytics.anomalies.baselines_cli.compute_baselines", return_value=[]),
        patch("app.analytics.anomalies.baselines_cli.replace_baselines") as replace_,
        patch("app.analytics.anomalies.baselines_cli.prune_other_versions") as prune,
    ):
        assert main(["--as-of", "2026-11-20", "--write"]) == 0

    replace_.assert_called_once()
    prune.assert_called_once()
    session.commit.assert_called_once_with()


def test_format_coverage_renders_markdown_rows() -> None:
    table = format_coverage(_result().coverage)

    assert "| band | hour | observation_count | sufficient | 2 |" in table


def test_quality_totals_include_every_quality() -> None:
    assert _result().quality_totals() == {
        "sufficient": 2,
        "sparse": 0,
        "degenerate": 0,
        "insufficient": 0,
    }
