"""Update the jotform Form table to add the info from the jotform API

Revision ID: 991d97a09e09
Revises: 5870f6863555
Create Date: 2026-09-13 17:00:11.477961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '991d97a09e09'
down_revision: Union[str, Sequence[str], None] = '5870f6863555'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
