from datetime import datetime
from typing import Dict, List, Protocol

from app.domain.appointment.models.appointment_model import Appointment
from app.domain.overview.models.overview import PackageLabel


class OverviewReadPort(Protocol):
    def appointments_touching(self, business_id: int, start: datetime, end: datetime) -> List[Appointment]:
        """Appointments of the business booked or dated in [start, end), with their Appointment Add-ons attached.

        The window is a coarse filter, the caller does the exact day arithmetic."""

    def package_labels(self, business_id: int) -> Dict[int, PackageLabel]: ...
    def addon_names(self, business_id: int) -> Dict[int, str]: ...
    def unresolved_addon_count(self, business_id: int) -> int:
        """Unresolved Add-ons of the business still waiting for resolution."""
