"""Baseline snapshot storage: replace-per-version, plus coverage reads."""

from collections.abc import Iterator, Sequence
from typing import Any, cast

from sqlalchemy import CursorResult, delete, func, insert, select
from sqlalchemy.orm import Session

from app.analytics.aggregation.persistence import MAX_BIND_PARAMETERS
from app.analytics.anomalies.models import BaselineSnapshot
from app.infrastructure.database.models import AnomalyBaseline

CoverageKey = tuple[str, str, str, str]  # dimension_type, resolution, metric, quality


def _row(snapshot: BaselineSnapshot) -> dict[str, Any]:
    return {
        "baseline_version": snapshot.baseline_version,
        "dimension_type": snapshot.dimension.dimension_type,
        "dimension_key": snapshot.dimension.serialize(),
        "metric": snapshot.metric,
        "resolution": snapshot.resolution,
        "slot": snapshot.slot,
        "as_of": snapshot.as_of,
        "method": snapshot.method.value,
        "quality": snapshot.quality.value,
        "sample_count": snapshot.sample_count,
        "transform": snapshot.transform,
        "center": snapshot.center,
        "scale": snapshot.scale,
        "mad": snapshot.mad,
        "expected_value": snapshot.expected_value,
        "cohort_start": snapshot.cohort_start,
        "cohort_end": snapshot.cohort_end,
    }


def _chunks(rows: list[dict[str, Any]]) -> Iterator[list[dict[str, Any]]]:
    per_statement = max(MAX_BIND_PARAMETERS // max(len(rows[0]), 1), 1)
    for start in range(0, len(rows), per_statement):
        yield rows[start : start + per_statement]


def replace_baselines(
    session: Session,
    *,
    baseline_version: str,
    snapshots: Sequence[BaselineSnapshot],
) -> None:
    """Make ``snapshots`` the complete stored set for ``baseline_version``.

    Delete-then-insert in the caller's transaction: readers see either the
    previous set or the new one, and dimensions that dropped out (for example
    a station no longer in the top N) disappear instead of going stale.
    """

    if any(s.baseline_version != baseline_version for s in snapshots):
        raise ValueError("All snapshots must belong to the version being replaced")

    session.execute(
        delete(AnomalyBaseline).where(AnomalyBaseline.baseline_version == baseline_version)
    )
    rows = [_row(snapshot) for snapshot in snapshots]
    if rows:
        for chunk in _chunks(rows):
            session.execute(insert(AnomalyBaseline), chunk)


def prune_other_versions(session: Session, *, keep_version: str) -> int:
    """Delete snapshots from superseded configurations; returns rows removed."""

    result = cast(
        CursorResult[Any],
        session.execute(
            delete(AnomalyBaseline).where(AnomalyBaseline.baseline_version != keep_version)
        ),
    )
    return result.rowcount


def load_coverage(session: Session, *, baseline_version: str) -> dict[CoverageKey, int]:
    """Stored snapshot counts by dimension type, resolution, metric and quality."""

    rows = session.execute(
        select(
            AnomalyBaseline.dimension_type,
            AnomalyBaseline.resolution,
            AnomalyBaseline.metric,
            AnomalyBaseline.quality,
            func.count(),
        )
        .where(AnomalyBaseline.baseline_version == baseline_version)
        .group_by(
            AnomalyBaseline.dimension_type,
            AnomalyBaseline.resolution,
            AnomalyBaseline.metric,
            AnomalyBaseline.quality,
        )
    )
    return {(d, r, m, q): count for d, r, m, q, count in rows}
