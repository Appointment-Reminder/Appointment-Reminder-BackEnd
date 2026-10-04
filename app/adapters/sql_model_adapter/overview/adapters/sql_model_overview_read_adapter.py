from datetime import datetime
from typing import Dict, List

from sqlmodel import Session, or_, select

from app.adapters.sql_model_adapter.addon.models.addon import Addon as AddonSQL
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment as AppointmentSQL, _to_domain
from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.addon.service.appointment_addon_hydration import attach_addons
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.overview.models.overview import PackageLabel
from app.domain.overview.port.overview_read_port import OverviewReadPort


class SQLModelOverviewReadAdapter(OverviewReadPort):
    """Fetches rows for the overview service, which does all the arithmetic."""

    def __init__(self, db: Session, appointment_addon_repo: AppointmentAddonRepositoryPort) -> None:
        self.db = db
        self.appointment_addon_repo = appointment_addon_repo

    def appointments_touching(self, business_id: int, start: datetime, end: datetime) -> List[Appointment]:
        rows = self.db.exec(
            select(AppointmentSQL)
            .where(AppointmentSQL.business_id == business_id)
            .where(or_(AppointmentSQL.created_at.between(start, end),
                       AppointmentSQL.appointment_date.between(start, end)))
        ).all()
        return attach_addons([_to_domain(row) for row in rows], self.appointment_addon_repo)

    def package_labels(self, business_id: int) -> Dict[int, PackageLabel]:
        categories = {c.id: c.name for c in self.db.exec(
            select(PackageCategorySQL).where(PackageCategorySQL.business_id == business_id)).all()}
        packages = self.db.exec(select(PackageSQL).where(PackageSQL.business_id == business_id)).all()
        return {p.id: PackageLabel(name=p.name, category_id=p.category_id, category_name=categories.get(p.category_id))
                for p in packages}

    def addon_names(self, business_id: int) -> Dict[int, str]:
        rows = self.db.exec(select(AddonSQL).where(AddonSQL.business_id == business_id)).all()
        return {a.id: a.name for a in rows}

    def unresolved_addon_count(self, business_id: int) -> int:
        ids = self.appointment_addon_repo.appointment_ids_with_unresolved_addons(business_id)
        pending = self.appointment_addon_repo.list_unresolved_addons_for_appointments(ids)
        return sum(len(items) for items in pending.values())
