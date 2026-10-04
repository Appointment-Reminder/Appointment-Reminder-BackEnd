"""migrate legacy adds_ons strings to unresolved addons

Every non-empty appointments.adds_ons string becomes Unresolved Add-ons on its appointment (the raw label is
preserved), then the adds_ons column is dropped.

The legacy string has no fixed format: it is split into labels when it is a JSON or Python list literal or has
several lines, otherwise the whole string is one label. Nothing is priced here: staff resolve them afterwards.

Revision ID: a1c0de000006
Revises: a1c0de000005
Create Date: 2026-10-04 10:50:00.000000

"""
import ast
import json
import re
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c0de000006'
down_revision: Union[str, Sequence[str], None] = 'a1c0de000005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

appointments = sa.table('appointments', sa.column('id', sa.Integer), sa.column('adds_ons', sa.String))
unresolved_addon = sa.table(
    'unresolved_addon',
    sa.column('id', sa.Integer),
    sa.column('appointment_id', sa.Integer),
    sa.column('raw_label', sa.String),
    sa.column('created_at', sa.DateTime),
)


def split_labels(raw):
    """The add-on labels held by a legacy adds_ons string. Empty for null, blank and 'None'."""
    if raw is None:
        return []
    text = str(raw).strip()
    if not text or text.lower() == 'none':
        return []

    items = None
    if text.startswith('['):
        for parse in (json.loads, ast.literal_eval):
            try:
                parsed = parse(text)
            except (ValueError, SyntaxError):
                continue
            if isinstance(parsed, (list, tuple)):
                items = parsed
                break
    if items is None:
        items = re.split(r'[\r\n]+', text)

    labels = []
    for item in items:
        label = str(item).strip()
        if label and label not in labels:
            labels.append(label)
    return labels


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    rows = bind.execute(
        sa.select(appointments.c.id, appointments.c.adds_ons).where(appointments.c.adds_ons.is_not(None))
    ).all()

    now = datetime.now()
    for appointment_id, adds_ons in rows:
        for label in split_labels(adds_ons):
            bind.execute(sa.insert(unresolved_addon).values(
                appointment_id=appointment_id, raw_label=label, created_at=now))

    op.drop_column('appointments', 'adds_ons')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('appointments', sa.Column('adds_ons', sa.String(), nullable=True))

    bind = op.get_bind()
    labels_by_appointment = {}
    for appointment_id, raw_label in bind.execute(
        sa.select(unresolved_addon.c.appointment_id, unresolved_addon.c.raw_label).order_by(unresolved_addon.c.id)
    ).all():
        labels_by_appointment.setdefault(appointment_id, []).append(raw_label)

    for appointment_id, labels in labels_by_appointment.items():
        bind.execute(
            sa.update(appointments).where(appointments.c.id == appointment_id).values(adds_ons='\n'.join(labels)))
