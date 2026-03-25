"""initial schema

Revision ID: 20260320_0001
Revises:
Create Date: 2026-03-20 12:40:00
"""

from alembic import op
import os
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260320_0001"
down_revision = None
branch_labels = None
depends_on = None

DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")

incident_status = sa.Enum(
    "OPEN",
    "ACKNOWLEDGED",
    "RESOLVED",
    "ESCALATED",
    name="incident_status",
    schema=DB_SCHEMA,
)
notification_channel = sa.Enum(
    "VOICE",
    "EMAIL",
    "WHATSAPP",
    "TELEGRAM",
    "CALENDAR",
    name="notification_channel",
    schema=DB_SCHEMA,
)
notification_status = sa.Enum(
    "PENDING",
    "SENT",
    "FAILED",
    "DELIVERED",
    "READ",
    "ANSWERED_VOICE",
    name="notification_status",
    schema=DB_SCHEMA,
)
audit_action = sa.Enum(
    "EVENT_RECEIVED",
    "DUPLICATED_EVENT",
    "RULE_MATCHED",
    "TASK_QUEUED",
    "NOTIFICATION_SENT",
    "CALLBACK_RECEIVED",
    "ACK_RECEIVED",
    "ESCALATED",
    "TWIML_GENERATED",
    "FALLBACK_TASK_QUEUED",
    name="audit_action",
    schema=DB_SCHEMA,
)
incident_status_ref = postgresql.ENUM(
    name="incident_status", schema=DB_SCHEMA, create_type=False
)
notification_channel_ref = postgresql.ENUM(
    name="notification_channel", schema=DB_SCHEMA, create_type=False
)
notification_status_ref = postgresql.ENUM(
    name="notification_status", schema=DB_SCHEMA, create_type=False
)
audit_action_ref = postgresql.ENUM(
    name="audit_action", schema=DB_SCHEMA, create_type=False
)


def upgrade() -> None:
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"'))
    bind = op.get_bind()
    incident_status.create(bind, checkfirst=True)
    notification_channel.create(bind, checkfirst=True)
    notification_status.create(bind, checkfirst=True)
    audit_action.create(bind, checkfirst=True)

    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("whatsapp", sa.String(), nullable=True),
        sa.Column("telegram_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema=DB_SCHEMA,
    )

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema=DB_SCHEMA,
    )

    op.create_table(
        "rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column(
            "condition_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("recipient_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channels", sa.JSON(), nullable=False),
        sa.Column(
            "active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("requires_ack", sa.Boolean(), nullable=True),
        sa.Column("ack_deadline", sa.Integer(), nullable=True),
        sa.Column(
            "fallback_policy_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["recipient_group_id"], [f"{DB_SCHEMA}.groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema=DB_SCHEMA,
    )

    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_event_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column(
            "payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("status", incident_status_ref, nullable=False, server_default="OPEN"),
        sa.Column("matched_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("dedupe_key", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["matched_rule_id"], [f"{DB_SCHEMA}.rules.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source", "external_event_id", name="uq_incidents_source_external_event_id"
        ),
        schema=DB_SCHEMA,
    )
    op.create_index(
        op.f("ix_incidents_external_event_id"),
        "incidents",
        ["external_event_id"],
        unique=False,
        schema=DB_SCHEMA,
    )
    op.create_index(
        op.f("ix_incidents_dedupe_key"),
        "incidents",
        ["dedupe_key"],
        unique=False,
        schema=DB_SCHEMA,
    )

    op.create_table(
        "group_members",
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], [f"{DB_SCHEMA}.contacts.id"]),
        sa.ForeignKeyConstraint(["group_id"], [f"{DB_SCHEMA}.groups.id"]),
        sa.PrimaryKeyConstraint("group_id", "contact_id"),
        schema=DB_SCHEMA,
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", notification_channel_ref, nullable=False),
        sa.Column(
            "status", notification_status_ref, nullable=False, server_default="PENDING"
        ),
        sa.Column("external_provider_id", sa.String(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contact_id"], [f"{DB_SCHEMA}.contacts.id"]),
        sa.ForeignKeyConstraint(["incident_id"], [f"{DB_SCHEMA}.incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema=DB_SCHEMA,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", audit_action_ref, nullable=False),
        sa.Column(
            "details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["incident_id"], [f"{DB_SCHEMA}.incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema=DB_SCHEMA,
    )
    op.create_index(
        op.f("ix_audit_logs_trace_id"),
        "audit_logs",
        ["trace_id"],
        unique=False,
        schema=DB_SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_audit_logs_trace_id"), table_name="audit_logs", schema=DB_SCHEMA
    )
    op.drop_table("audit_logs", schema=DB_SCHEMA)

    op.drop_table("notifications", schema=DB_SCHEMA)
    op.drop_table("group_members", schema=DB_SCHEMA)

    op.drop_index(
        op.f("ix_incidents_dedupe_key"), table_name="incidents", schema=DB_SCHEMA
    )
    op.drop_index(
        op.f("ix_incidents_external_event_id"), table_name="incidents", schema=DB_SCHEMA
    )
    op.drop_table("incidents", schema=DB_SCHEMA)

    op.drop_table("rules", schema=DB_SCHEMA)
    op.drop_table("groups", schema=DB_SCHEMA)
    op.drop_table("contacts", schema=DB_SCHEMA)

    bind = op.get_bind()
    audit_action.drop(bind, checkfirst=True)
    notification_status.drop(bind, checkfirst=True)
    notification_channel.drop(bind, checkfirst=True)
    incident_status.drop(bind, checkfirst=True)
    op.execute(sa.text(f'DROP SCHEMA IF EXISTS "{DB_SCHEMA}"'))
