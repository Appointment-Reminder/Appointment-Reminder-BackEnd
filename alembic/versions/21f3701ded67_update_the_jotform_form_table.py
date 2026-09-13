"""Update the jotform Form table

Revision ID: 21f3701ded67
Revises: 7a833dd559c5
Create Date: 2026-09-13 16:55:13.438870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21f3701ded67'
down_revision: Union[str, Sequence[str], None] = '7a833dd559c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
