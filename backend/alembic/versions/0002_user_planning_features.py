"""add user planning feature columns and planning tables

Revision ID: 0002_user_planning_features
Revises: 0001_initial
Create Date: 2026-04-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_user_planning_features"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "users" in inspector.get_table_names():
        existing_columns = _column_names(inspector, "users")
        if "monthly_budget_target" not in existing_columns:
            op.add_column("users", sa.Column("monthly_budget_target", sa.Float(), nullable=True))
        if "preferred_savings_rate" not in existing_columns:
            op.add_column("users", sa.Column("preferred_savings_rate", sa.Float(), nullable=True))
        if "category_budget_preferences" not in existing_columns:
            op.add_column("users", sa.Column("category_budget_preferences", sa.JSON(), nullable=True))

    table_names = set(inspector.get_table_names())
    if "goals" not in table_names:
        op.create_table(
            "goals",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("goal_type", sa.String(length=64), nullable=False),
            sa.Column("target_amount", sa.Float(), nullable=False),
            sa.Column("current_amount", sa.Float(), nullable=False, server_default="0"),
            sa.Column("target_months", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        )

    if "recurring_transactions" not in table_names:
        op.create_table(
            "recurring_transactions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("transaction_type", sa.String(length=32), nullable=False),
            sa.Column("frequency", sa.String(length=32), nullable=False, server_default="monthly"),
            sa.Column("day_of_month", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "recurring_transactions" in table_names:
        op.drop_table("recurring_transactions")
    if "goals" in table_names:
        op.drop_table("goals")

    if "users" in table_names:
        existing_columns = _column_names(inspector, "users")
        if "category_budget_preferences" in existing_columns:
            op.drop_column("users", "category_budget_preferences")
        if "preferred_savings_rate" in existing_columns:
            op.drop_column("users", "preferred_savings_rate")
        if "monthly_budget_target" in existing_columns:
            op.drop_column("users", "monthly_budget_target")
