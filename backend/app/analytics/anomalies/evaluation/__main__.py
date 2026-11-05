"""Run the Story 5.1 detector evaluation.

Examples::

    python -m app.analytics.anomalies.evaluation --source synthetic
    python -m app.analytics.anomalies.evaluation --source database --metric snr_avg_db
    python -m app.analytics.anomalies.evaluation --source csv \\
        --points-csv band_hourly.csv --events-csv events.csv --out report.md
"""

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import cast

from app.analytics.anomalies.evaluation.detectors import default_detectors
from app.analytics.anomalies.evaluation.evaluation import default_split, evaluate
from app.analytics.anomalies.evaluation.models import EvaluationDataset, Metric
from app.analytics.anomalies.evaluation.report import render_markdown
from app.analytics.anomalies.evaluation.sources import load_events_csv, load_points_csv
from app.analytics.anomalies.evaluation.synthetic import generate_synthetic_dataset


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    metric = cast(Metric, args.metric)

    dataset = _load(args, metric)
    if not dataset.points:
        print("No rollup points found for the requested range.", file=sys.stderr)
        return 1

    split_at = args.split_at or default_split(dataset.points)
    report = evaluate(
        dataset,
        default_detectors(),
        split_at=split_at,
        target_flag_rate=args.target_flag_rate,
    )
    markdown = render_markdown(report)

    if args.out:
        args.out.write_text(markdown)
    print(markdown)
    return 0


def _load(args: argparse.Namespace, metric: Metric) -> EvaluationDataset:
    if args.source == "synthetic":
        return generate_synthetic_dataset(days=args.synthetic_days, seed=args.seed)

    if args.source == "csv":
        if args.points_csv is None:
            raise SystemExit("--points-csv is required with --source csv")
        events = load_events_csv(args.events_csv) if args.events_csv else ()
        return EvaluationDataset(
            points=load_points_csv(args.points_csv, metric=metric),
            events=events,
            metric=metric,
            source=f"csv:{args.points_csv.name}",
        )

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.analytics.anomalies.evaluation.sources import load_from_database
    from app.config import Settings

    engine = create_engine(args.database_url or Settings().radio_atlas_database_url)
    try:
        with Session(engine) as session:
            session.connection(execution_options={"postgresql_readonly": True})
            dataset = load_from_database(session, metric=metric, start=args.start, end=args.end)
    finally:
        engine.dispose()
    if args.events_csv:
        dataset = EvaluationDataset(
            points=dataset.points,
            events=dataset.events + load_events_csv(args.events_csv),
            metric=dataset.metric,
            source=dataset.source,
        )
    return dataset


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--source", choices=["database", "csv", "synthetic"], default="database")
    parser.add_argument(
        "--metric", choices=["observation_count", "snr_avg_db"], default="observation_count"
    )
    parser.add_argument("--database-url", help="Defaults to RADIO_ATLAS_DATABASE_URL.")
    parser.add_argument("--points-csv", type=Path)
    parser.add_argument("--events-csv", type=Path)
    parser.add_argument("--start", type=datetime.fromisoformat)
    parser.add_argument("--end", type=datetime.fromisoformat)
    parser.add_argument(
        "--split-at",
        type=datetime.fromisoformat,
        help="Holdout start (UTC). Defaults to 70%% of the observed hours.",
    )
    parser.add_argument("--target-flag-rate", type=float, default=0.005)
    parser.add_argument("--synthetic-days", type=int, default=84)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
