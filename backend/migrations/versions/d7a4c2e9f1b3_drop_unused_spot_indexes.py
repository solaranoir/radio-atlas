"""drop unused spot indexes

No query filters spots by callsign or station id, and the station id columns
are never populated. ix_spots_band is covered by ix_spots_band_observed_at.

Revision ID: d7a4c2e9f1b3
Revises: c3e1a7d5b2f4
Create Date: 2026-11-08 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7a4c2e9f1b3"
down_revision: str | Sequence[str] | None = "c3e1a7d5b2f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UNUSED_INDEXES = {
    "ix_spots_band": "band",
    "ix_spots_receiver_callsign": "receiver_callsign",
    "ix_spots_receiver_station_id": "receiver_station_id",
    "ix_spots_sender_callsign": "sender_callsign",
    "ix_spots_sender_station_id": "sender_station_id",
}


def upgrade() -> None:
    """Upgrade schema."""
    for name in UNUSED_INDEXES:
        op.drop_index(name, table_name="spots")


def downgrade() -> None:
    """Downgrade schema."""
    for name, column in UNUSED_INDEXES.items():
        op.create_index(name, "spots", [column], unique=False)
