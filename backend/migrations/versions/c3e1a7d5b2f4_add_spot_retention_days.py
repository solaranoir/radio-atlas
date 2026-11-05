"""add spot retention days

Revision ID: c3e1a7d5b2f4
Revises: 8aab0b72d8f1
Create Date: 2026-11-04 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3e1a7d5b2f4"
down_revision: str | Sequence[str] | None = "8aab0b72d8f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "spot_retention_days",
        sa.Column("day_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "rolled_up_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("day_start"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("spot_retention_days")
