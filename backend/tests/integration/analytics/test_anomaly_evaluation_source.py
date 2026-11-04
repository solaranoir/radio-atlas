from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from app.analytics.anomalies.evaluation.__main__ import main
from app.analytics.anomalies.evaluation.models import SeriesKey
from app.analytics.anomalies.evaluation.sources import load_from_database
from app.config import Settings
from app.infrastructure.database.models import AnalyticsBandHourly, Provider, SolarCondition

# A far-future window keeps this test isolated from any other rows.
START = datetime(2031, 3, 1, tzinfo=UTC)
END = START + timedelta(days=1)


def test_load_from_database_reads_rollups_and_kp_storms(db_session: Session) -> None:
    provider = Provider(
        name="anomaly_eval_provider",
        display_name="Anomaly Eval Provider",
        provider_type="solar",
    )
    db_session.add(provider)
    db_session.flush()

    db_session.add_all(
        [
            AnalyticsBandHourly(
                bucket_start=START + timedelta(hours=hour),
                band="20m",
                mode="FT8",
                observation_count=10 + hour,
                unique_sender_count=1,
                unique_receiver_count=1,
                snr_sample_count=1 if hour else 0,
                snr_min_db=-10 if hour else None,
                snr_max_db=-10 if hour else None,
                snr_avg_db=-10.0 if hour else None,
            )
            for hour in range(3)
        ]
        + [
            SolarCondition(
                provider_id=provider.id,
                observation_type="kp_index",
                observed_at=START + timedelta(hours=1),
                value=6.0,
                unit="kp",
            ),
            SolarCondition(
                provider_id=provider.id,
                observation_type="kp_index",
                observed_at=START + timedelta(hours=2),
                value=2.0,
                unit="kp",
            ),
            AnalyticsBandHourly(
                bucket_start=END,
                band="20m",
                mode="FT8",
                observation_count=99,
                unique_sender_count=1,
                unique_receiver_count=1,
                snr_sample_count=0,
            ),
        ]
    )
    db_session.flush()

    counts = load_from_database(db_session, metric="observation_count", start=START, end=END)
    snr = load_from_database(db_session, metric="snr_avg_db", start=START, end=END)

    assert [p.value for p in counts.points] == [10.0, 11.0, 12.0]
    assert {p.key for p in counts.points} == {SeriesKey("20m", "FT8")}
    assert [p.value for p in snr.points] == [None, -10.0, -10.0]
    assert len(counts.events) == 1
    assert counts.events[0].start == START + timedelta(hours=1)
    assert counts.events[0].end == START + timedelta(hours=4)


def test_cli_database_source_reports_on_committed_rows(tmp_path: Path) -> None:
    settings = Settings()
    engine = create_engine(settings.radio_atlas_database_url)
    window_start = START + timedelta(days=30)
    rows = [
        AnalyticsBandHourly(
            bucket_start=window_start + timedelta(hours=hour),
            band="cli-test",
            mode="FT8",
            observation_count=5 + hour % 24,
            unique_sender_count=1,
            unique_receiver_count=1,
            snr_sample_count=0,
        )
        for hour in range(24 * 12)
    ]
    try:
        with Session(engine) as session:
            session.add_all(rows)
            session.commit()

        out = tmp_path / "report.md"
        exit_code = main(
            [
                "--source",
                "database",
                "--start",
                window_start.isoformat(),
                "--end",
                (window_start + timedelta(days=12)).isoformat(),
                "--out",
                str(out),
            ]
        )

        assert exit_code == 0
        assert "database:analytics_band_hourly" in out.read_text()
    finally:
        with Session(engine) as session:
            session.execute(
                delete(AnalyticsBandHourly).where(AnalyticsBandHourly.band == "cli-test")
            )
            session.commit()
        engine.dispose()


def test_cli_database_source_with_no_rows_returns_error() -> None:
    far = START + timedelta(days=400)
    assert (
        main(
            [
                "--source",
                "database",
                "--start",
                far.isoformat(),
                "--end",
                (far + timedelta(days=1)).isoformat(),
            ]
        )
        == 1
    )
