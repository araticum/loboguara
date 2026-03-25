"""performance indices

Revision ID: 20260325_0006
Revises: 20260325_0005
Create Date: 2026-03-25 10:45:00.000000

"""

from alembic import op
import os

# revision identifiers, used by Alembic.
revision = "20260325_0006"
down_revision = "20260325_0005"
branch_labels = None
depends_on = None

DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")


def upgrade() -> None:
    # Composite index for stale sweeper
    op.create_index(
        op.f("ix_incidents_status_created_at"),
        "incidents",
        ["status", "created_at"],
        unique=False,
        schema=DB_SCHEMA,
    )
    # Fast timeline query index
    op.create_index(
        op.f("ix_audit_logs_created_at"),
        "audit_logs",
        ["created_at"],
        unique=False,
        schema=DB_SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_audit_logs_created_at"), table_name="audit_logs", schema=DB_SCHEMA
    )
    op.drop_index(
        op.f("ix_incidents_status_created_at"), table_name="incidents", schema=DB_SCHEMA
    )
