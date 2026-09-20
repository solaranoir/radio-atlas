from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Double,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base

Index(
    "uq_spots_fallback_identity",
    "provider_id",
    "observed_at",
    "sender_callsign",
    "receiver_callsign",
    "frequency_hz",
    "mode",
    unique=True,
    postgresql_where=text("sequence_number IS NULL"),
    postgresql_nulls_not_distinct=True,
)


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    provider_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
    )
    callsign: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    callsign: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
    )
    grid_square: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    latitude: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    longitude: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    provider_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("providers.id"),
        nullable=False,
    )
    sequence_number: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    sender_station_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stations.id"),
        nullable=True,
    )
    receiver_station_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stations.id"),
        nullable=True,
    )
    sender_callsign: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    receiver_callsign: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    sender_grid: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    receiver_grid: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    frequency_hz: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    band: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    snr_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    transmitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sender_entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    receiver_entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        Index(
            "uq_spots_provider_sequence",
            "provider_id",
            "sequence_number",
            unique=True,
            postgresql_where=text("sequence_number IS NOT NULL"),
        ),
        Index(
            "uq_spots_fallback_identity",
            "provider_id",
            "observed_at",
            "sender_callsign",
            "receiver_callsign",
            "frequency_hz",
            "mode",
            unique=True,
            postgresql_where=text("sequence_number IS NULL"),
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_spots_observed_at", "observed_at"),
        Index("ix_spots_band", "band"),
        Index("ix_spots_band_observed_at", "band", "observed_at"),
        Index("ix_spots_sender_station_id", "sender_station_id"),
        Index("ix_spots_receiver_station_id", "receiver_station_id"),
        Index("ix_spots_sender_callsign", "sender_callsign"),
        Index("ix_spots_receiver_callsign", "receiver_callsign"),
    )


class SolarCondition(Base):
    __tablename__ = "solar_conditions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    provider_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("providers.id"),
        nullable=False,
    )
    observation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    value: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    unit: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "observation_type",
            "observed_at",
            name="uq_solar_conditions_provider_type_observed",
        ),
        Index(
            "ix_solar_conditions_observed_at",
            "observed_at",
        ),
        Index(
            "ix_solar_conditions_observation_type",
            "observation_type",
        ),
        Index(
            "ix_solar_conditions_type_observed_at",
            "observation_type",
            "observed_at",
        ),
    )


class AnalyticsBandHourly(Base):
    __tablename__ = "analytics_band_hourly"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    bucket_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    band: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    observation_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_sender_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_receiver_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_sample_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_min_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_max_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_avg_db: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "bucket_start",
            "band",
            "mode",
            name="uq_analytics_band_hourly_bucket_band_mode",
        ),
        Index(
            "ix_analytics_band_hourly_bucket_start",
            "bucket_start",
        ),
        Index(
            "ix_analytics_band_hourly_band_mode_bucket",
            "band",
            "mode",
            "bucket_start",
        ),
    )


class AnalyticsBandDaily(Base):
    __tablename__ = "analytics_band_daily"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    bucket_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    band: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    observation_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_sender_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_receiver_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_sample_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_min_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_max_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_avg_db: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "bucket_start",
            "band",
            "mode",
            name="uq_analytics_band_daily_bucket_band_mode",
        ),
        Index(
            "ix_analytics_band_daily_bucket_start",
            "bucket_start",
        ),
        Index(
            "ix_analytics_band_daily_band_mode_bucket",
            "band",
            "mode",
            "bucket_start",
        ),
    )


class AnalyticsStationHourly(Base):
    __tablename__ = "analytics_station_hourly"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    bucket_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    station_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stations.id"),
        nullable=True,
    )
    callsign: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    observation_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_counterparty_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_sample_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_min_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_max_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_avg_db: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "bucket_start",
            "callsign",
            "direction",
            name="uq_analytics_station_hourly_bucket_callsign_direction",
        ),
        Index(
            "ix_analytics_station_hourly_bucket_start",
            "bucket_start",
        ),
        Index(
            "ix_analytics_station_hourly_callsign_direction_bucket",
            "callsign",
            "direction",
            "bucket_start",
        ),
        Index(
            "ix_analytics_station_hourly_station_id",
            "station_id",
        ),
    )


class AnalyticsStationDaily(Base):
    __tablename__ = "analytics_station_daily"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    bucket_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    station_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stations.id"),
        nullable=True,
    )
    callsign: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    observation_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    unique_counterparty_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_sample_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    snr_min_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_max_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    snr_avg_db: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "bucket_start",
            "callsign",
            "direction",
            name="uq_analytics_station_daily_bucket_callsign_direction",
        ),
        Index(
            "ix_analytics_station_daily_bucket_start",
            "bucket_start",
        ),
        Index(
            "ix_analytics_station_daily_callsign_direction_bucket",
            "callsign",
            "direction",
            "bucket_start",
        ),
        Index(
            "ix_analytics_station_daily_station_id",
            "station_id",
        ),
    )
