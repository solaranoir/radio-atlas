from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.analytics.anomalies.evaluation.__main__ import main
from app.analytics.anomalies.evaluation.models import KnownEvent, SeriesKey
from app.analytics.anomalies.evaluation.sources import (
    kp_storm_events,
    load_events_csv,
    load_points_csv,
)

START = datetime(2026, 6, 1, tzinfo=UTC)


def test_kp_storm_events_merge_touching_windows() -> None:
    readings = [
        START + timedelta(hours=3),
        START,
        START + timedelta(hours=1),
        START + timedelta(hours=12),
    ]

    events = kp_storm_events(readings, threshold=5.0)

    assert events == [
        KnownEvent(start=START, end=START + timedelta(hours=6), label="kp>=5"),
        KnownEvent(
            start=START + timedelta(hours=12),
            end=START + timedelta(hours=15),
            label="kp>=5",
        ),
    ]
    assert kp_storm_events([]) == []


def test_load_points_csv_selects_metric(tmp_path: Path) -> None:
    path = tmp_path / "points.csv"
    path.write_text(
        "bucket_start,band,mode,observation_count,snr_avg_db\n"
        "2026-06-01T00:00:00Z,20m,FT8,42,-11.5\n"
        "2026-06-01T01:00:00+00:00,40m,CW,3,\n"
    )

    counts = load_points_csv(path, metric="observation_count")
    snr = load_points_csv(path, metric="snr_avg_db")

    assert counts[0].key == SeriesKey("20m", "FT8")
    assert counts[0].bucket_start == START
    assert [p.value for p in counts] == [42.0, 3.0]
    assert [p.value for p in snr] == [-11.5, None]


def test_load_points_csv_requires_utc_offset(tmp_path: Path) -> None:
    path = tmp_path / "points.csv"
    path.write_text(
        "bucket_start,band,mode,observation_count,snr_avg_db\n2026-06-01T00:00:00,20m,FT8,1,\n"
    )

    with pytest.raises(ValueError, match="UTC offset"):
        load_points_csv(path, metric="observation_count")


def test_load_events_csv_with_optional_band(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    path.write_text(
        "start,end,label,band\n"
        "2026-06-01T00:00:00Z,2026-06-01T03:00:00Z,flare,\n"
        "2026-06-02T00:00:00Z,2026-06-02T02:00:00Z,opening,10m\n"
    )

    events = load_events_csv(path)

    assert events[0].band is None
    assert events[1].band == "10m"
    assert events[1].end - events[1].start == timedelta(hours=2)


def test_cli_synthetic_writes_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "report.md"

    exit_code = main(["--source", "synthetic", "--synthetic-days", "21", "--out", str(out)])

    assert exit_code == 0
    assert "seasonal-mad" in out.read_text()
    assert "Anomaly Detector Evaluation" in capsys.readouterr().out


def test_cli_csv_source(tmp_path: Path) -> None:
    rows = ["bucket_start,band,mode,observation_count,snr_avg_db"]
    for hour in range(24 * 15):
        at = (START + timedelta(hours=hour)).isoformat()
        rows.append(f"{at},20m,FT8,{10 + hour % 24},-10")
    points = tmp_path / "points.csv"
    points.write_text("\n".join(rows) + "\n")
    out = tmp_path / "report.md"

    exit_code = main(["--source", "csv", "--points-csv", str(points), "--out", str(out)])

    assert exit_code == 0
    assert "csv:points.csv" in out.read_text()


def test_cli_csv_requires_points_path() -> None:
    with pytest.raises(SystemExit):
        main(["--source", "csv"])
