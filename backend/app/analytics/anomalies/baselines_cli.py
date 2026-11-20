"""Compute baselines for any cut-off and report coverage.

Dry run by default (read-only; safe against a read-only role):

    python -m app.analytics.anomalies.baselines_cli --as-of 2026-11-20

Store the result as the current baseline set (backfill / manual refresh):

    python -m app.analytics.anomalies.baselines_cli --as-of 2026-11-20 --write

``--no-stations`` skips station baselines (for roles without access to the
station rollup tables).
"""

import argparse
from collections.abc import Sequence
from datetime import UTC, datetime

from app.analytics.aggregation.jobs import floor_to_day
from app.analytics.anomalies.config import DEFAULT_BASELINE_CONFIG
from app.analytics.anomalies.persistence import (
    CoverageKey,
    prune_other_versions,
    replace_baselines,
)
from app.analytics.anomalies.service import compute_baselines, summarize_coverage
from app.infrastructure.database.session import create_session


def _parse_day(value: str) -> datetime:
    return floor_to_day(datetime.fromisoformat(value).replace(tzinfo=UTC))


def format_coverage(coverage: dict[CoverageKey, int]) -> str:
    lines = [
        "| Dimension | Resolution | Metric | Quality | Snapshots |",
        "| --- | --- | --- | --- | ---: |",
    ]
    lines += [f"| {d} | {r} | {m} | {q} | {n} |" for (d, r, m, q), n in coverage.items()]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--as-of",
        type=_parse_day,
        default=floor_to_day(datetime.now(UTC)),
        help="UTC day (YYYY-MM-DD); only data before its midnight is used",
    )
    parser.add_argument("--write", action="store_true", help="store as the current set")
    parser.add_argument("--no-stations", action="store_true", help="band baselines only")
    args = parser.parse_args(argv)

    config = DEFAULT_BASELINE_CONFIG
    with create_session() as session:
        snapshots = compute_baselines(
            session,
            as_of=args.as_of,
            config=config,
            include_stations=not args.no_stations,
        )
        if args.write:
            replace_baselines(session, baseline_version=config.version, snapshots=snapshots)
            prune_other_versions(session, keep_version=config.version)
            session.commit()

    action = "stored" if args.write else "computed (dry run)"
    print(f"Baseline {config.version} as of {args.as_of.isoformat()}: {len(snapshots)} {action}")
    print(format_coverage(summarize_coverage(snapshots)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
