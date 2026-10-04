"""add unresolved addon

Revision ID: a1c0de000005
Revises: a1c0de000004
Create Date: 2026-10-04 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000005'
down_revision: Union[str, Sequence[str], None] = 'a1c0de000004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('unresolved_addon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('raw_label', sa.String(), nullable=False),
    sa.Column('resolved_addon_id', sa.Integer(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['resolved_addon_id'], ['addon.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unresolved_addon_appointment_id'), 'unresolved_addon', ['appointment_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_unresolved_addon_appointment_id'), table_name='unresolved_addon')
    op.drop_table('unresolved_addon')
