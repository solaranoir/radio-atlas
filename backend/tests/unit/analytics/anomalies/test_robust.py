import pytest

from app.analytics.anomalies.robust import (
    MAD_CONSISTENCY,
    median_absolute_deviation,
    median_of,
    modified_z_score,
)


def test_median_absolute_deviation_ignores_a_single_outlier() -> None:
    values = [10.0, 11.0, 9.0, 10.0, 1_000.0]

    center = median_of(values)

    assert center == 10.0
    assert median_absolute_deviation(values, center=center) == 1.0


def test_modified_z_score_scales_by_consistency_constant() -> None:
    assert modified_z_score(14.0, center=10.0, scale=2.0) == pytest.approx(MAD_CONSISTENCY * 2)
    assert modified_z_score(6.0, center=10.0, scale=2.0) < 0


def test_guards_reject_empty_input_and_zero_scale() -> None:
    with pytest.raises(ValueError):
        median_of([])
    with pytest.raises(ValueError):
        modified_z_score(1.0, center=0.0, scale=0.0)
