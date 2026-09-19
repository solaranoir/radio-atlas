from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BandAggregate:
    bucket_start: datetime
    band: str
    mode: str
    observation_count: int
    unique_sender_count: int
    unique_receiver_count: int
    snr_sample_count: int
    snr_min_db: int | None
    snr_max_db: int | None
    snr_avg_db: float | None


@dataclass(frozen=True)
class StationAggregate:
    bucket_start: datetime
    station_id: int | None
    callsign: str
    direction: str
    observation_count: int
    unique_counterparty_count: int
    snr_sample_count: int
    snr_min_db: int | None
    snr_max_db: int | None
    snr_avg_db: float | None
