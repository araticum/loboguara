"""add incident occurrences

Revision ID: 20260327_0007
Revises: 20260325_0006
Create Date: 2026-03-27 21:50:00.000000

"""

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = "20260327_0007"
down_revision = "20260325_0006"
branch_labels = None
depends_on = None

DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column("occurrences", sa.Integer(), nullable=False, server_default="1"),
        schema=DB_SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("incidents", "occurrences", schema=DB_SCHEMA)
