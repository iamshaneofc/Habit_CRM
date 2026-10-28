"""add_user_ownership

Revision ID: 5fb6a13d78f9
Revises: e0c9f3d4842b
Create Date: 2026-10-28 21:23:18.593110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fb6a13d78f9'
down_revision: Union[str, Sequence[str], None] = 'e0c9f3d4842b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('habit_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_habit_logs_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_habit_logs_user_id_users', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('habits', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_habits_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_habits_user_id_users', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('habits', schema=None) as batch_op:
        batch_op.drop_constraint('fk_habits_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_habits_user_id'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('habit_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_habit_logs_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_habit_logs_user_id'))
        batch_op.drop_column('user_id')
