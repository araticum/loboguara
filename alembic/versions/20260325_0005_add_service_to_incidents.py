"""add service to incidents

Revision ID: 20260325_0005
Revises: 20260320_0004
Create Date: 2026-03-25 10:25:00.000000

"""

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = "20260325_0005"
down_revision = "20260320_0004"
branch_labels = None
depends_on = None

DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")


def upgrade() -> None:
    op.add_column(
        "incidents", sa.Column("service", sa.String(), nullable=True), schema=DB_SCHEMA
    )
    op.create_index(
        op.f("ix_incidents_service"),
        "incidents",
        ["service"],
        unique=False,
        schema=DB_SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_incidents_service"), table_name="incidents", schema=DB_SCHEMA
    )
    op.drop_column("incidents", "service", schema=DB_SCHEMA)
