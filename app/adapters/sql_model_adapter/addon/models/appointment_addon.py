from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlmodel import SQLModel, Field

from app.domain.addon.models.appointment_addon import AppointmentAddon as AppointmentAddonEntity


class AppointmentAddon(SQLModel, table=True):
    __tablename__ = "appointment_addon"
    __table_args__ = (UniqueConstraint("appointment_id", "addon_id", name="uq_appointment_addon"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(sa_column=Column(ForeignKey("appointments.id", ondelete="CASCADE"), index=True))
    addon_id: int = Field(foreign_key="addon.id", index=True)
    addon_price_id: int = Field(foreign_key="addon_price.id")

    quantity: int = Field(default=1)
    unit_price: float
    unit_duration: int = Field(default=0)
    unit_commission_percent: Optional[float] = Field(default=None)
    unit_commission_amount: Optional[float] = Field(default=None)
    price_total: float
    commission_total: Optional[float] = Field(default=None)

    raw_label: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)


def _to_domain(sql: AppointmentAddon) -> AppointmentAddonEntity:
    return AppointmentAddonEntity(
        id=sql.id,
        appointment_id=sql.appointment_id,
        addon_id=sql.addon_id,
        addon_price_id=sql.addon_price_id,
        quantity=sql.quantity,
        unit_price=sql.unit_price,
        unit_duration=sql.unit_duration,
        unit_commission_percent=sql.unit_commission_percent,
        unit_commission_amount=sql.unit_commission_amount,
        price_total=sql.price_total,
        commission_total=sql.commission_total,
        raw_label=sql.raw_label,
    )


def _apply_sql(sql: AppointmentAddon, obj: AppointmentAddonEntity) -> None:
    sql.quantity = obj.quantity
    sql.unit_commission_percent = obj.unit_commission_percent
    sql.unit_commission_amount = obj.unit_commission_amount
    sql.price_total = obj.price_total
    sql.commission_total = obj.commission_total
