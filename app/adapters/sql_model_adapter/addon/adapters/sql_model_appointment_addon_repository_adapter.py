from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select

from app.adapters.sql_model_adapter.addon.models.appointment_addon import AppointmentAddon as AppointmentAddonSQL, \
    _to_domain, _apply_sql
from app.domain.addon.models.appointment_addon import AppointmentAddon as AppointmentAddonEntity
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort


class SQLModelAppointmentAddonRepositoryAdapter(AppointmentAddonRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, line: AppointmentAddonEntity) -> AppointmentAddonEntity:
        sql_obj = AppointmentAddonSQL(
            appointment_id=line.appointment_id,
            addon_id=line.addon_id,
            addon_price_id=line.addon_price_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            unit_duration=line.unit_duration,
            unit_commission_percent=line.unit_commission_percent,
            unit_commission_amount=line.unit_commission_amount,
            line_total=line.line_total,
            line_commission=line.line_commission,
            raw_label=line.raw_label,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return _to_domain(sql_obj)

    def update(self, line: AppointmentAddonEntity) -> Optional[AppointmentAddonEntity]:
        existing = self.db.get(AppointmentAddonSQL, line.id)
        if not existing:
            return None
        _apply_sql(existing, line)
        self.db.commit()
        self.db.refresh(existing)
        return _to_domain(existing)

    def remove(self, line_id: int) -> bool:
        existing = self.db.get(AppointmentAddonSQL, line_id)
        if not existing:
            return False
        self.db.delete(existing)
        self.db.commit()
        return True

    def get(self, appointment_id: int, addon_id: int) -> Optional[AppointmentAddonEntity]:
        row = self.db.exec(
            select(AppointmentAddonSQL)
            .where(AppointmentAddonSQL.appointment_id == appointment_id)
            .where(AppointmentAddonSQL.addon_id == addon_id)
        ).first()
        return _to_domain(row) if row else None

    def list_for_appointment(self, appointment_id: int) -> List[AppointmentAddonEntity]:
        return self.list_for_appointments([appointment_id]).get(appointment_id, [])

    def list_for_appointments(self, appointment_ids: Iterable[int]) -> Dict[int, List[AppointmentAddonEntity]]:
        ids = list(appointment_ids)
        grouped: Dict[int, List[AppointmentAddonEntity]] = {}
        if not ids:
            return grouped
        rows = self.db.exec(
            select(AppointmentAddonSQL)
            .where(AppointmentAddonSQL.appointment_id.in_(ids))
            .order_by(AppointmentAddonSQL.id)
        ).all()
        for row in rows:
            grouped.setdefault(row.appointment_id, []).append(_to_domain(row))
        return grouped

    def exists_for_addon(self, addon_id: int) -> bool:
        return self.db.exec(
            select(AppointmentAddonSQL.id).where(AppointmentAddonSQL.addon_id == addon_id).limit(1)
        ).first() is not None
