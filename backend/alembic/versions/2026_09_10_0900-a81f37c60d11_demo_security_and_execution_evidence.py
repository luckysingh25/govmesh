"""demo security and execution evidence

Revision ID: a81f37c60d11
Revises: 4fa8e006b0c0
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a81f37c60d11"
down_revision: Union[str, None] = "4fa8e006b0c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("citizen_id", sa.String(), nullable=True))
    op.create_index("ix_users_citizen_id", "users", ["citizen_id"], unique=True)
    op.add_column("mapping_suggestions", sa.Column("reviewed_by", sa.String(), nullable=True))
    op.add_column("mapping_suggestions", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("mapping_suggestions", sa.Column("mapping_version", sa.Integer(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("protocol", sa.String(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("raw_response", sa.Text(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("source_mapping", sa.JSON(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("normalized_output", sa.JSON(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("duration_ms", sa.Integer(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("correlation_id", sa.String(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("schema_version", sa.Integer(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("mapping_version", sa.Integer(), nullable=True))
    op.add_column("workflow_step_instances", sa.Column("external_job_id", sa.String(), nullable=True))


def downgrade() -> None:
    for name in ("external_job_id", "mapping_version", "schema_version", "correlation_id", "duration_ms", "normalized_output", "source_mapping", "raw_response", "protocol"):
        op.drop_column("workflow_step_instances", name)
    for name in ("mapping_version", "reviewed_at", "reviewed_by"):
        op.drop_column("mapping_suggestions", name)
    op.drop_index("ix_users_citizen_id", table_name="users")
    op.drop_column("users", "citizen_id")
