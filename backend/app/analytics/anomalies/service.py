"""Baseline orchestration: read rollups, compute snapshots, store them.

``compute_baselines`` is read-only and works for any ``as_of``, which is how
historical backfills and the Story 5.3 scorer obtain point-in-time
baselines. ``refresh_baselines`` additionally replaces the stored set.
"""

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.analytics.anomalies.baseline import build_metric_series, compute_snapshots
from app.analytics.anomalies.config import DEFAULT_BASELINE_CONFIG, BaselineConfig
from app.analytics.anomalies.models import (
    BaselineQuality,
    BaselineSnapshot,
    DimensionKey,
    Resolution,
)
from app.analytics.anomalies.persistence import (
    CoverageKey,
    prune_other_versions,
    replace_baselines,
)
from app.analytics.anomalies.queries import (
    load_active_buckets,
    load_band_rollups,
    load_station_rollups,
    select_top_stations,
)

RESOLUTIONS: tuple[Resolution, ...] = ("hour", "day")


@dataclass(frozen=True)
class BaselineRefreshResult:
    baseline_version: str
    as_of: datetime
    snapshot_count: int
    band_dimensions: int
    station_dimensions: int
    coverage: dict[CoverageKey, int]
    pruned_rows: int

    def quality_totals(self) -> dict[str, int]:
        totals: Counter[str] = Counter()
        for (_, _, _, quality), count in self.coverage.items():
            totals[quality] += count
        return {quality.value: totals.get(quality.value, 0) for quality in BaselineQuality}


def summarize_coverage(snapshots: Iterable[BaselineSnapshot]) -> dict[CoverageKey, int]:
    counts: Counter[CoverageKey] = Counter(
        (s.dimension.dimension_type, s.resolution, s.metric, s.quality.value) for s in snapshots
    )
    return dict(sorted(counts.items()))


def compute_baselines(
    session: Session,
    *,
    as_of: datetime,
    config: BaselineConfig = DEFAULT_BASELINE_CONFIG,
    include_stations: bool = True,
) -> list[BaselineSnapshot]:
    stations: list[DimensionKey] = []
    if include_stations:
        stations = select_top_stations(
            session,
            start=as_of - config.station_selection_lookback,
            end=as_of,
            limit=config.station_limit,
        )

    snapshots: list[BaselineSnapshot] = []
    for resolution in RESOLUTIONS:
        cohort = config.cohort(resolution)
        start = as_of - max(cohort.seasonal_lookback, cohort.fallback_lookback)
        active = load_active_buckets(session, resolution=resolution, start=start, end=as_of)

        band_rows = load_band_rollups(session, resolution=resolution, start=start, end=as_of)
        snapshots.extend(
            _snapshots_for(band_rows, resolution, as_of, active, config, dimension_type="band")
        )

        if stations:
            station_rows = load_station_rollups(
                session, resolution=resolution, start=start, end=as_of, stations=stations
            )
            snapshots.extend(
                _snapshots_for(
                    station_rows, resolution, as_of, active, config, dimension_type="station"
                )
            )
    return snapshots


def refresh_baselines(
    session: Session,
    *,
    as_of: datetime,
    config: BaselineConfig = DEFAULT_BASELINE_CONFIG,
    include_stations: bool = True,
) -> BaselineRefreshResult:
    """Recompute and store the current baseline set. The caller commits."""

    snapshots = compute_baselines(
        session, as_of=as_of, config=config, include_stations=include_stations
    )
    replace_baselines(session, baseline_version=config.version, snapshots=snapshots)
    pruned = prune_other_versions(session, keep_version=config.version)

    dimensions = {s.dimension for s in snapshots}
    return BaselineRefreshResult(
        baseline_version=config.version,
        as_of=as_of,
        snapshot_count=len(snapshots),
        band_dimensions=sum(1 for d in dimensions if d.dimension_type == "band"),
        station_dimensions=sum(1 for d in dimensions if d.dimension_type == "station"),
        coverage=summarize_coverage(snapshots),
        pruned_rows=pruned,
    )


def _snapshots_for(
    rows_by_dimension: Mapping[DimensionKey, Sequence[Mapping[str, Any]]],
    resolution: Resolution,
    as_of: datetime,
    active: Sequence[datetime],
    config: BaselineConfig,
    *,
    dimension_type: str,
) -> list[BaselineSnapshot]:
    snapshots: list[BaselineSnapshot] = []
    for dimension in sorted(rows_by_dimension):
        rows = rows_by_dimension[dimension]
        for spec in config.metrics_for(dimension_type):
            series = build_metric_series(rows, spec=spec, active_buckets=active)
            snapshots.extend(
                compute_snapshots(
                    dimension=dimension,
                    spec=spec,
                    resolution=resolution,
                    as_of=as_of,
                    series=series,
                    config=config,
                )
            )
    return snapshots
