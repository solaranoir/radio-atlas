from app.analytics.anomalies.evaluation.evaluation import EvaluationReport


def render_markdown(report: EvaluationReport) -> str:
    lines = [
        "# Anomaly Detector Evaluation",
        "",
        f"- Source: `{report.source}`",
        f"- Metric: `{report.metric}`",
        f"- Range: {report.start.isoformat()} to {report.end.isoformat()}",
        f"- Train/holdout split: {report.split_at.isoformat()}",
        f"- Series: {report.series_count} ({report.sparse_series_count} sparse)",
        f"- Alert budget: each detector calibrated to flag "
        f"{report.target_flag_rate:.2%} of training buckets",
        "",
        "| Detector | Threshold | Holdout coverage | Holdout flag rate | Flags/day "
        "| Non-event flags/day | Diurnal skew | Sparse flag share | Event recall | Event score pct "
        "| Flags in events | Deterministic |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |",
    ]
    for r in report.results:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{r.detector}`",
                    _num(r.threshold),
                    f"{r.holdout_coverage:.1%}",
                    f"{r.holdout_flag_rate:.2%}",
                    f"{r.holdout_flags_per_day:.1f}",
                    f"{r.non_event_flags_per_day:.1f}",
                    _num(r.diurnal_skew),
                    _pct(r.sparse_flag_share),
                    _pct(r.event_recall),
                    _num(r.event_score_percentile),
                    _pct(r.in_event_flag_share),
                    "yes" if r.deterministic else "**no**",
                ]
            )
            + " |"
        )
    events = report.results[0].holdout_events if report.results else 0
    lines += [
        "",
        f"Holdout reference events: {events}.",
        "",
        "Column guide: *non-event flags/day* counts flags outside every reference event "
        "(false alarms when the reference set is complete, as with synthetic data). "
        "*Diurnal skew* is the total-variation distance between the hours non-event flags "
        "land in and the hours that were scoreable (0 = no time-of-day bias). "
        "*Sparse flag share* is the share of flags raised on sparse series. *Event score "
        "pct* is the median holdout percentile of |score| inside reference events "
        "(0.5 = uninformative). *Flags in events* is the share of flags inside any "
        "reference event, a precision proxy that is only meaningful when the reference "
        "set is complete (synthetic data).",
        "",
    ]
    return "\n".join(lines)


def _num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.0%}"
