"""Robust location/scale primitives shared by baselines and the evaluation harness."""

from collections.abc import Sequence

# Scales MAD to be a consistent estimator of the standard deviation for
# normally distributed data (Iglewicz & Hoaglin modified Z-score).
MAD_CONSISTENCY = 0.6745


def median_of(values: Sequence[float]) -> float:
    """Median of a non-empty sequence (sorts a copy)."""

    if not values:
        raise ValueError("median_of requires at least one value")
    return sorted_median(sorted(values))


def sorted_median(values: Sequence[float]) -> float:
    """Median of a non-empty, already sorted sequence."""

    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2.0


def median_absolute_deviation(values: Sequence[float], *, center: float) -> float:
    """Unscaled MAD: median distance of ``values`` from ``center``."""

    return median_of([abs(value - center) for value in values])


def modified_z_score(value: float, *, center: float, scale: float) -> float:
    """Iglewicz-Hoaglin modified Z-score; ``scale`` must already be floored (> 0)."""

    if scale <= 0:
        raise ValueError("scale must be positive; apply the configured floor first")
    return MAD_CONSISTENCY * (value - center) / scale
