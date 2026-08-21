from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain import (
    SpotObservation,
    StationObservation,
)


def test_rejects_naive_observed_at() -> None:
    with pytest.raises(ValidationError):
        SpotObservation(
            provider="psk_reporter",
            observed_at=datetime(2026, 8, 21, 12, 0),
            sender_callsign="EA5JLN",
            receiver_callsign="DL4JC",
            mode="FT8",
        )


def test_rejects_naive_transmitted_at() -> None:
    with pytest.raises(ValidationError):
        SpotObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            transmitted_at=datetime(2026, 8, 21, 11, 59),
            sender_callsign="EA5JLN",
            receiver_callsign="DL4JC",
            mode="FT8",
        )


def test_rejects_invalid_latitude() -> None:
    with pytest.raises(ValidationError):
        StationObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            callsign="EA5JLN",
            latitude=91,
        )


def test_rejects_invalid_longitude() -> None:
    with pytest.raises(ValidationError):
        StationObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            callsign="EA5JLN",
            longitude=181,
        )


def test_rejects_non_positive_frequency() -> None:
    with pytest.raises(ValidationError):
        SpotObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            sender_callsign="EA5JLN",
            receiver_callsign="DL4JC",
            mode="FT8",
            frequency_hz=0,
        )


def test_normalizes_band() -> None:
    observation = SpotObservation(
        provider="psk_reporter",
        observed_at="2026-08-21T12:00:00Z",
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        mode="FT8",
        band=" 20M ",
    )

    assert observation.band == "20m"


def test_rejects_empty_band() -> None:
    with pytest.raises(ValidationError):
        SpotObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            sender_callsign="EA5JLN",
            receiver_callsign="DL4JC",
            mode="FT8",
            band="   ",
        )


def test_normalizes_callsign() -> None:
    observation = SpotObservation(
        provider="psk_reporter",
        observed_at="2026-08-21T12:00:00Z",
        sender_callsign=" er1wk/qrp ",
        receiver_callsign="dl4jc",
        mode="FT8",
    )

    assert observation.sender_callsign == "ER1WK/QRP"
    assert observation.receiver_callsign == "DL4JC"


def test_rejects_invalid_callsign_characters() -> None:
    with pytest.raises(ValidationError):
        StationObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            callsign="BAD@CALL",
        )


def test_normalizes_grid_square() -> None:
    observation = SpotObservation(
        provider="psk_reporter",
        observed_at="2026-08-21T12:00:00Z",
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        sender_grid="jn39lh",
        mode="FT8",
    )

    assert observation.sender_grid == "JN39LH"


@pytest.mark.parametrize(
    "grid",
    [
        "ZZ99",
        "JN3",
        "JN39L",
        "12AB34",
    ],
)
def test_rejects_invalid_grid_square(grid: str) -> None:
    with pytest.raises(ValidationError):
        StationObservation(
            provider="psk_reporter",
            observed_at="2026-08-21T12:00:00Z",
            callsign="EA5JLN",
            grid_square=grid,
        )


def test_accepts_extended_grid_precision() -> None:
    observation = StationObservation(
        provider="psk_reporter",
        observed_at="2026-08-21T12:00:00Z",
        callsign="EA5JLN",
        grid_square="DM43AH94KC",
    )

    assert observation.grid_square == "DM43AH94KC"
