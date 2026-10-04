"""add addon price

Revision ID: a1c0de000002
Revises: a1c0de000001
Create Date: 2026-10-04 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000002'
down_revision: Union[str, Sequence[str], None] = 'a1c0de000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('addon_price',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('addon_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('effective_from', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['addon_id'], ['addon.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addon_price_addon_id'), 'addon_price', ['addon_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_addon_price_addon_id'), table_name='addon_price')
    op.drop_table('addon_price')
