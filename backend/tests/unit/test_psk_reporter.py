from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.psk_reporter import (
    Band,
    Callsign,
    Coordinate,
    Frequency,
    GridSquare,
    NormalizedPSKSpot,
    OperatingMode,
    PSKReporterSpot,
)


def test_callsign_normalizes_case_and_whitespace() -> None:
    callsign = Callsign(value="  er1wk/qrp  ")

    assert callsign.value == "ER1WK/QRP"


def test_callsign_rejects_empty_value() -> None:
    with pytest.raises(ValidationError):
        Callsign(value="   ")


def test_frequency_exposes_mhz() -> None:
    frequency = Frequency(hz=14_075_361)

    assert frequency.hz == 14_075_361
    assert frequency.mhz == 14.075361


def test_frequency_rejects_non_positive_value() -> None:
    with pytest.raises(ValidationError):
        Frequency(hz=0)


def test_band_normalizes_case_and_whitespace() -> None:
    band = Band(value=" 20M ")

    assert band.value == "20m"


def test_operating_mode_normalizes_case_and_whitespace() -> None:
    mode = OperatingMode(value=" ft8 ")

    assert mode.value == "FT8"


def test_grid_square_normalizes_case() -> None:
    grid = GridSquare(value="jn39lh")

    assert grid.value == "JN39LH"


def test_grid_square_accepts_variable_precision() -> None:
    assert GridSquare(value="JO42").value == "JO42"
    assert GridSquare(value="CN87wq78").value == "CN87WQ78"
    assert GridSquare(value="DM43ah94kc").value == "DM43AH94KC"


def test_grid_square_rejects_too_short_value() -> None:
    with pytest.raises(ValidationError):
        GridSquare(value="JO")


def test_grid_square_rejects_odd_length() -> None:
    with pytest.raises(ValidationError):
        GridSquare(value="JN39L")


def test_coordinate_accepts_valid_latitude_and_longitude() -> None:
    coordinate = Coordinate(
        latitude=36.1699,
        longitude=-115.1398,
    )
    assert coordinate.latitude == 36.1699
    assert coordinate.longitude == -115.1398


def test_coordinate_rejects_invalid_latitude() -> None:
    with pytest.raises(ValidationError):
        Coordinate(
            latitude=91,
            longitude=0,
        )


def test_psk_reporter_spot_from_mqtt_payload() -> None:
    payload = {
        "sq": 71869170759,
        "f": 14075361,
        "md": "FT8",
        "rp": -5,
        "t": 1787168040,
        "t_tx": 1787168025,
        "sc": "EA5JLN",
        "sl": "IM99TN",
        "rc": "DL4JC",
        "rl": "JN39lh",
        "sa": 281,
        "ra": 230,
        "b": "20m",
    }

    spot = PSKReporterSpot.from_mqtt_payload(payload)

    assert spot.sequence_number == 71869170759
    assert spot.frequency_hz == 14075361
    assert spot.mode == "FT8"
    assert spot.snr_db == -5
    assert spot.observed_at == 1787168040
    assert spot.transmitted_at == 1787168025
    assert spot.sender_callsign == "EA5JLN"
    assert spot.sender_locator == "IM99TN"
    assert spot.receiver_callsign == "DL4JC"
    assert spot.receiver_locator == "JN39lh"
    assert spot.sender_entity_id == 281
    assert spot.receiver_entity_id == 230
    assert spot.band == "20m"


def test_psk_reporter_spot_accepts_optional_fields_missing() -> None:
    payload = {
        "sq": 71869170759,
        "md": "FT8",
        "t": 1787168040,
        "sc": "EA5JLN",
        "rc": "DL4JC",
    }

    spot = PSKReporterSpot.from_mqtt_payload(payload)

    assert spot.frequency_hz is None
    assert spot.snr_db is None
    assert spot.transmitted_at is None
    assert spot.sender_locator is None
    assert spot.receiver_locator is None
    assert spot.band is None


def test_psk_reporter_spot_normalizes() -> None:
    spot = PSKReporterSpot(
        sequence_number=71869170759,
        frequency_hz=14075361,
        mode="ft8",
        snr_db=-5,
        observed_at=1787168040,
        transmitted_at=1787168025,
        sender_callsign="ea5jln",
        sender_locator="im99tn",
        receiver_callsign="dl4jc",
        receiver_locator="jn39lh",
        sender_entity_id=281,
        receiver_entity_id=230,
        band="20M",
    )

    normalized = spot.normalize()

    assert isinstance(normalized, NormalizedPSKSpot)

    assert normalized.sender_callsign.value == "EA5JLN"
    assert normalized.receiver_callsign.value == "DL4JC"

    assert normalized.sender_grid is not None
    assert normalized.sender_grid.value == "IM99TN"

    assert normalized.receiver_grid is not None
    assert normalized.receiver_grid.value == "JN39LH"

    assert normalized.frequency is not None
    assert normalized.frequency.hz == 14075361
    assert normalized.frequency.mhz == 14.075361

    assert normalized.band is not None
    assert normalized.band.value == "20m"

    assert normalized.mode.value == "FT8"

    assert normalized.observed_at == datetime.fromtimestamp(
        1787168040,
        tz=UTC,
    )

    assert normalized.transmitted_at == datetime.fromtimestamp(
        1787168025,
        tz=UTC,
    )

    assert normalized.snr_db == -5
    assert normalized.sender_entity_id == 281
    assert normalized.receiver_entity_id == 230


def test_callsign_strips_ssid_suffix() -> None:
    assert Callsign(value="KM3T-3").value == "KM3T"


def test_callsign_strips_two_digit_ssid_suffix() -> None:
    assert Callsign(value="W1ABC-12").value == "W1ABC"


def test_callsign_preserves_base_callsign() -> None:
    assert Callsign(value="kk7qea").value == "KK7QEA"


def test_callsign_does_not_strip_invalid_large_suffix() -> None:
    assert Callsign(value="W1ABC-99").value == "W1ABC-99"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("V2/KK7QEA", "V2/KK7QEA"),
        ("KK7QEA/P", "KK7QEA/P"),
        ("EA8/KK7QEA/P", "EA8/KK7QEA/P"),
        ("V2/KK7QEA-3", "V2/KK7QEA"),
    ],
)
def test_callsign_preserves_slash_forms_and_strips_ssid(
    raw: str,
    expected: str,
) -> None:
    assert Callsign(value=raw).value == expected


def test_psk_spot_normalizes_receiver_ssid_suffix() -> None:
    spot = PSKReporterSpot(
        sequence_number=71869170759,
        frequency_hz=14075361,
        mode="ft8",
        snr_db=-5,
        observed_at=1787168040,
        transmitted_at=1787168025,
        sender_callsign="ea5jln",
        sender_locator="im99tn",
        receiver_callsign="KM3T-3",
        receiver_locator="jn39lh",
        sender_entity_id=281,
        receiver_entity_id=230,
        band="20M",
    )

    normalized = spot.normalize()

    assert normalized.receiver_callsign.value == "KM3T"
