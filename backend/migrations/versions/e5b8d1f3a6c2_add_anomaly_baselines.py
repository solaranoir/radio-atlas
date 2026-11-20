"""add anomaly baselines

Revision ID: e5b8d1f3a6c2
Revises: d7a4c2e9f1b3
Create Date: 2026-11-20 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5b8d1f3a6c2"
down_revision: str | Sequence[str] | None = "d7a4c2e9f1b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "anomaly_baselines",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("baseline_version", sa.String(length=64), nullable=False),
        sa.Column("dimension_type", sa.String(length=16), nullable=False),
        sa.Column("dimension_key", sa.String(length=128), nullable=False),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("resolution", sa.String(length=8), nullable=False),
        sa.Column("slot", sa.SmallInteger(), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("method", sa.String(length=40), nullable=False),
        sa.Column("quality", sa.String(length=16), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("transform", sa.String(length=16), nullable=False),
        sa.Column("center", sa.Double(), nullable=True),
        sa.Column("scale", sa.Double(), nullable=True),
        sa.Column("mad", sa.Double(), nullable=True),
        sa.Column("expected_value", sa.Double(), nullable=True),
        sa.Column("cohort_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cohort_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "baseline_version",
            "dimension_type",
            "dimension_key",
            "metric",
            "resolution",
            "slot",
            name="uq_anomaly_baselines_snapshot",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("anomaly_baselines")
