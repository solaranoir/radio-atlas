from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain import (
    SpotObservation,
    StationObservation,
)
from app.domain.observations import _validate_callsign


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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("kk7qea", "KK7QEA"),
        ("  kk7qea  ", "KK7QEA"),
        ("v2/kk7qea", "V2/KK7QEA"),
        ("ea8/kk7qea/p", "EA8/KK7QEA/P"),
        ("kk7qea/mm", "KK7QEA/MM"),
        ("ve7abc/k7", "VE7ABC/K7"),
    ],
)
def test_validate_callsign_normalizes_valid_callsigns(
    raw: str,
    expected: str,
) -> None:
    assert _validate_callsign(raw) == expected


@pytest.mark.parametrize(
    "callsign",
    [
        "",
        "   ",
    ],
)
def test_validate_callsign_rejects_empty_callsign(
    callsign: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="callsign must not be empty",
    ):
        _validate_callsign(callsign)


def test_validate_callsign_accepts_maximum_length() -> None:
    callsign = "A" * 32

    assert _validate_callsign(callsign) == callsign


def test_validate_callsign_rejects_callsign_over_maximum_length() -> None:
    with pytest.raises(
        ValueError,
        match="callsign is too long",
    ):
        _validate_callsign("A" * 33)


@pytest.mark.parametrize(
    "callsign",
    [
        "/KK7QEA",
        "KK7QEA/",
        "/V2/KK7QEA",
        "EA8/KK7QEA/P/",
    ],
)
def test_validate_callsign_rejects_leading_or_trailing_slash(
    callsign: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="callsign contains invalid separator placement",
    ):
        _validate_callsign(callsign)


@pytest.mark.parametrize(
    "callsign",
    [
        "KK7QEA//P",
        "EA8//KK7QEA",
        "EA8/KK7QEA//P",
    ],
)
def test_validate_callsign_rejects_double_slash(
    callsign: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="callsign contains invalid separator placement",
    ):
        _validate_callsign(callsign)


@pytest.mark.parametrize(
    "callsign",
    [
        "KK7QEA",
        "V2/KK7QEA",
        "KK7QEA/P",
        "EA8/KK7QEA/P",
        "SWL-EL98GK",
    ],
)
def test_validate_callsign_accepts_valid_station_identifiers(
    callsign: str,
) -> None:
    assert _validate_callsign(callsign) == callsign


@pytest.mark.parametrize(
    "callsign",
    [
        "/KK7QEA",
        "KK7QEA/",
        "-SWL",
        "SWL-",
        "KK7QEA//P",
        "SWL--EL98GK",
        "KK7 QEA",
        "KK7QEA!",
    ],
)
def test_validate_callsign_rejects_invalid_station_identifiers(
    callsign: str,
) -> None:
    with pytest.raises(ValueError):
        _validate_callsign(callsign)


@pytest.mark.parametrize(
    "callsign",
    [
        "/KK7QEA",
        "KK7QEA/",
        "-SWL",
        "SWL-",
        "KK7QEA//P",
        "SWL--EL98GK",
    ],
)
def test_validate_callsign_rejects_invalid_separator_placement(
    callsign: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="callsign contains invalid separator placement",
    ):
        _validate_callsign(callsign)


@pytest.mark.parametrize(
    "callsign",
    [
        "KK7 QEA",
        "KK7QEA!",
        "KK7QEA@",
        "KK7_QEA",
    ],
)
def test_validate_callsign_rejects_invalid_characters(
    callsign: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="callsign contains invalid characters",
    ):
        _validate_callsign(callsign)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("kk7qea", "KK7QEA"),
        ("  v2/kk7qea  ", "V2/KK7QEA"),
        ("swl-el98gk", "SWL-EL98GK"),
    ],
)
def test_validate_callsign_normalizes_case_and_whitespace(
    raw: str,
    expected: str,
) -> None:
    assert _validate_callsign(raw) == expected
