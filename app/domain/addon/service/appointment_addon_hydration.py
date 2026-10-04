from typing import List

from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.appointment.models.appointment_model import Appointment


def attach_addons(appointments: List[Appointment], repo: AppointmentAddonRepositoryPort) -> List[Appointment]:
    """Load the Appointment Add-ons and the pending Unresolved Add-ons onto each appointment."""
    ids = [a.id for a in appointments]
    addons = repo.list_for_appointments(ids)
    unresolved = repo.list_unresolved_addons_for_appointments(ids)
    for appointment in appointments:
        appointment.addons = addons.get(appointment.id, [])
        appointment.unresolved_addons = unresolved.get(appointment.id, [])
    return appointments
