"""add addon catalogue

Revision ID: a1c0de000001
Revises: 531ee6b24fe2
Create Date: 2026-10-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000001'
down_revision: Union[str, Sequence[str], None] = '531ee6b24fe2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('addon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('jotform_alias', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column('has_duration', sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column('has_quantity', sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['package_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addon_business_id'), 'addon', ['business_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_addon_business_id'), table_name='addon')
    op.drop_table('addon')
