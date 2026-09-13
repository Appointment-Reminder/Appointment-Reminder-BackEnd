"""Update the jotform Form table to add the info from the jotform API

Revision ID: 5870f6863555
Revises: 21f3701ded67
Create Date: 2026-09-13 16:58:03.091569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5870f6863555'
down_revision: Union[str, Sequence[str], None] = '21f3701ded67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
