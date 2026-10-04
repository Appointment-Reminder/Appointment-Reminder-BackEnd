"""add addon commission

Revision ID: a1c0de000003
Revises: a1c0de000002
Create Date: 2026-10-04 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000003'
down_revision: Union[str, Sequence[str], None] = 'a1c0de000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('addon_commission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_member_id', sa.Integer(), nullable=False),
    sa.Column('addon_id', sa.Integer(), nullable=False),
    sa.Column('commission_amount', sa.Integer(), nullable=False),
    sa.Column('commission_isPercentage', sa.Boolean(), nullable=False),
    sa.Column('effective_from', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['addon_id'], ['addon.id'], ),
    sa.ForeignKeyConstraint(['business_member_id'], ['business_members.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addon_commission_addon_id'), 'addon_commission', ['addon_id'], unique=False)
    op.create_index(op.f('ix_addon_commission_business_member_id'), 'addon_commission', ['business_member_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_addon_commission_business_member_id'), table_name='addon_commission')
    op.drop_index(op.f('ix_addon_commission_addon_id'), table_name='addon_commission')
    op.drop_table('addon_commission')
