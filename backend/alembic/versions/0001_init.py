"""init tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("agents", sa.Column("id", sa.String(64), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("owner_team", sa.String(120), nullable=False), sa.Column("guardrail_bundle", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("workflows", sa.Column("id", sa.String(120), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("definition", sa.JSON(), nullable=False))
    op.create_table("policy_bundles", sa.Column("id", sa.String(120), primary_key=True), sa.Column("rules", sa.JSON(), nullable=False))
    op.create_table("workflow_runs", sa.Column("id", sa.String(64), primary_key=True), sa.Column("workflow_id", sa.String(120), sa.ForeignKey("workflows.id"), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("provider", sa.String(40), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("output", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("audit_logs", sa.Column("id", sa.String(64), primary_key=True), sa.Column("actor_id", sa.String(120), nullable=False), sa.Column("action", sa.String(120), nullable=False), sa.Column("resource", sa.String(120), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("immutable_hash", sa.String(128), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("maker_checker_tasks", sa.Column("id", sa.String(64), primary_key=True), sa.Column("run_id", sa.String(64), sa.ForeignKey("workflow_runs.id"), nullable=False), sa.Column("maker_id", sa.String(120), nullable=True), sa.Column("checker_id", sa.String(120), nullable=True), sa.Column("status", sa.String(30), nullable=False), sa.Column("reason", sa.Text(), nullable=False), sa.Column("resolved", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_table("maker_checker_tasks")
    op.drop_table("audit_logs")
    op.drop_table("workflow_runs")
    op.drop_table("policy_bundles")
    op.drop_table("workflows")
    op.drop_table("agents")
