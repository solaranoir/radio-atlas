"""add analytics aggregation tables

Revision ID: 9601bd15dc66
Revises: f4d2f0efb1ba
Create Date: 2026-09-20 09:08:58.664213

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9601bd15dc66"
down_revision: str | Sequence[str] | None = "f4d2f0efb1ba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "analytics_band_hourly",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("band", sa.String(length=20), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("observation_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_sender_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_receiver_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_sample_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_min_db", sa.Integer(), nullable=True),
        sa.Column("snr_max_db", sa.Integer(), nullable=True),
        sa.Column("snr_avg_db", sa.Double(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "bucket_start",
            "band",
            "mode",
            name="uq_analytics_band_hourly_bucket_band_mode",
        ),
    )
    op.create_index(
        "ix_analytics_band_hourly_bucket_start",
        "analytics_band_hourly",
        ["bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_band_hourly_band_mode_bucket",
        "analytics_band_hourly",
        ["band", "mode", "bucket_start"],
        unique=False,
    )
    op.create_table(
        "analytics_band_daily",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("band", sa.String(length=20), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("observation_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_sender_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_receiver_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_sample_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_min_db", sa.Integer(), nullable=True),
        sa.Column("snr_max_db", sa.Integer(), nullable=True),
        sa.Column("snr_avg_db", sa.Double(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "bucket_start",
            "band",
            "mode",
            name="uq_analytics_band_daily_bucket_band_mode",
        ),
    )
    op.create_index(
        "ix_analytics_band_daily_bucket_start",
        "analytics_band_daily",
        ["bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_band_daily_band_mode_bucket",
        "analytics_band_daily",
        ["band", "mode", "bucket_start"],
        unique=False,
    )
    op.create_table(
        "analytics_station_hourly",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("station_id", sa.BigInteger(), nullable=True),
        sa.Column("callsign", sa.String(length=32), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("observation_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_counterparty_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_sample_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_min_db", sa.Integer(), nullable=True),
        sa.Column("snr_max_db", sa.Integer(), nullable=True),
        sa.Column("snr_avg_db", sa.Double(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "bucket_start",
            "callsign",
            "direction",
            name="uq_analytics_station_hourly_bucket_callsign_direction",
        ),
    )
    op.create_index(
        "ix_analytics_station_hourly_bucket_start",
        "analytics_station_hourly",
        ["bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_station_hourly_callsign_direction_bucket",
        "analytics_station_hourly",
        ["callsign", "direction", "bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_station_hourly_station_id",
        "analytics_station_hourly",
        ["station_id"],
        unique=False,
    )
    op.create_table(
        "analytics_station_daily",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("station_id", sa.BigInteger(), nullable=True),
        sa.Column("callsign", sa.String(length=32), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("observation_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_counterparty_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_sample_count", sa.BigInteger(), nullable=False),
        sa.Column("snr_min_db", sa.Integer(), nullable=True),
        sa.Column("snr_max_db", sa.Integer(), nullable=True),
        sa.Column("snr_avg_db", sa.Double(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "bucket_start",
            "callsign",
            "direction",
            name="uq_analytics_station_daily_bucket_callsign_direction",
        ),
    )
    op.create_index(
        "ix_analytics_station_daily_bucket_start",
        "analytics_station_daily",
        ["bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_station_daily_callsign_direction_bucket",
        "analytics_station_daily",
        ["callsign", "direction", "bucket_start"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_station_daily_station_id",
        "analytics_station_daily",
        ["station_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_analytics_station_daily_station_id",
        table_name="analytics_station_daily",
    )
    op.drop_index(
        "ix_analytics_station_daily_callsign_direction_bucket",
        table_name="analytics_station_daily",
    )
    op.drop_index(
        "ix_analytics_station_daily_bucket_start",
        table_name="analytics_station_daily",
    )
    op.drop_table("analytics_station_daily")

    op.drop_index(
        "ix_analytics_station_hourly_station_id",
        table_name="analytics_station_hourly",
    )
    op.drop_index(
        "ix_analytics_station_hourly_callsign_direction_bucket",
        table_name="analytics_station_hourly",
    )
    op.drop_index(
        "ix_analytics_station_hourly_bucket_start",
        table_name="analytics_station_hourly",
    )
    op.drop_table("analytics_station_hourly")

    op.drop_index(
        "ix_analytics_band_daily_band_mode_bucket",
        table_name="analytics_band_daily",
    )
    op.drop_index(
        "ix_analytics_band_daily_bucket_start",
        table_name="analytics_band_daily",
    )
    op.drop_table("analytics_band_daily")

    op.drop_index(
        "ix_analytics_band_hourly_band_mode_bucket",
        table_name="analytics_band_hourly",
    )
    op.drop_index(
        "ix_analytics_band_hourly_bucket_start",
        table_name="analytics_band_hourly",
    )
    op.drop_table("analytics_band_hourly")
