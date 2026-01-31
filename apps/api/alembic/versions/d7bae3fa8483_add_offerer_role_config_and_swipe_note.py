"""add_offerer_role_config_and_swipe_note

Revision ID: d7bae3fa8483
Revises: 6c878fbde540
Create Date: 2026-01-31 22:26:08.084484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString


# revision identifiers, used by Alembic.
revision: str = 'd7bae3fa8483'
down_revision: Union[str, Sequence[str], None] = '6c878fbde540'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns using batch mode for SQLite compatibility
    with op.batch_alter_table('offerers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_config_id', sa.Uuid(), nullable=True))
        batch_op.create_foreign_key('fk_offerer_role_config', 'offerer_role_configs', ['role_config_id'], ['id'])
    
    with op.batch_alter_table('swipe_decisions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('note', AutoString(length=2000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('swipe_decisions', schema=None) as batch_op:
        batch_op.drop_column('note')
    
    with op.batch_alter_table('offerers', schema=None) as batch_op:
        batch_op.drop_constraint('fk_offerer_role_config', type_='foreignkey')
        batch_op.drop_column('role_config_id')
