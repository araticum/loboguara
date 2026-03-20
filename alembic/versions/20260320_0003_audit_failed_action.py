"""add failed audit action

Revision ID: 20260320_0003
Revises: 20260320_0002
Create Date: 2026-03-20 13:45:00
"""

from alembic import op
import os
import sqlalchemy as sa


revision = "20260320_0003"
down_revision = "20260320_0002"
branch_labels = None
depends_on = None

DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")


def upgrade() -> None:
    op.execute(
        sa.text(
            f"ALTER TYPE {DB_SCHEMA}.audit_action ADD VALUE IF NOT EXISTS 'FAILED'"
        )
    )


def downgrade() -> None:
    pass
