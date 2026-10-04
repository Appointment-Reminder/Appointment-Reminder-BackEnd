from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UnresolvedAddon:
    """A Jotform Add-on label that could not be booked automatically, kept on the appointment for staff to resolve."""
    appointment_id: Optional[int]
    raw_label: str
    resolved_addon_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    id: Optional[int] = None

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None
