"""baseline_habits_and_logs

Revision ID: f4e30b9e76d1
Revises: 
Create Date: 2026-10-28 21:10:17.809745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4e30b9e76d1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "habits" not in existing_tables:
        op.create_table(
            "habits",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False, server_default="General"),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("icon", sa.String(length=20), server_default="🎯"),
            sa.Column("color", sa.String(length=20), server_default="#10b981"),
            sa.Column("daily_target", sa.Integer(), server_default="1"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
            sa.Column("display_order", sa.Integer(), server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id")
        )
        op.create_index("ix_habits_id", "habits", ["id"], unique=False)

    if "habit_logs" not in existing_tables:
        op.create_table(
            "habit_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("habit_id", sa.Integer(), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("value", sa.Integer(), server_default="1"),
            sa.Column("notes", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["habit_id"], ["habits.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("habit_id", "date", name="uq_habit_date")
        )
        op.create_index("ix_habit_logs_id", "habit_logs", ["id"], unique=False)
        op.create_index("ix_habit_logs_habit_id", "habit_logs", ["habit_id"], unique=False)
        op.create_index("ix_habit_logs_date", "habit_logs", ["date"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "habit_logs" in existing_tables:
        op.drop_table("habit_logs")
    if "habits" in existing_tables:
        op.drop_table("habits")
