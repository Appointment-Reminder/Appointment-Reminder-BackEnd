"""add appointment addon

Revision ID: a1c0de000004
Revises: a1c0de000003
Create Date: 2026-10-04 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000004'
down_revision: Union[str, Sequence[str], None] = 'a1c0de000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('appointment_addon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('addon_id', sa.Integer(), nullable=False),
    sa.Column('addon_price_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('unit_duration', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('unit_commission_percent', sa.Float(), nullable=True),
    sa.Column('unit_commission_amount', sa.Float(), nullable=True),
    sa.Column('price_total', sa.Float(), nullable=False),
    sa.Column('commission_total', sa.Float(), nullable=True),
    sa.Column('raw_label', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['addon_id'], ['addon.id'], ),
    sa.ForeignKeyConstraint(['addon_price_id'], ['addon_price.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('appointment_id', 'addon_id', name='uq_appointment_addon')
    )
    op.create_index(op.f('ix_appointment_addon_appointment_id'), 'appointment_addon', ['appointment_id'], unique=False)
    op.create_index(op.f('ix_appointment_addon_addon_id'), 'appointment_addon', ['addon_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_appointment_addon_addon_id'), table_name='appointment_addon')
    op.drop_index(op.f('ix_appointment_addon_appointment_id'), table_name='appointment_addon')
    op.drop_table('appointment_addon')
