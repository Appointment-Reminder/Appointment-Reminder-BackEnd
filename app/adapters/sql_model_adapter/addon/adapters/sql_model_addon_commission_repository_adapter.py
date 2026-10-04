from typing import List

from sqlalchemy.orm import Session
from sqlmodel import select

from app.adapters.sql_model_adapter.addon.models.addon_commission import AddonCommission as AddonCommissionSQL, \
    _to_domain
from app.domain.addon.models.addon_commission import AddonCommission as AddonCommissionEntity
from app.domain.addon.port.addon_commission_repository_port import AddonCommissionRepositoryPort


class SQLModelAddonCommissionRepositoryAdapter(AddonCommissionRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, commission: AddonCommissionEntity) -> AddonCommissionEntity:
        sql_obj = AddonCommissionSQL(
            business_member_id=commission.business_member_id,
            addon_id=commission.addon_id,
            commission_amount=commission.commission_amount,
            commission_isPercentage=commission.commission_isPercentage,
            effective_from=commission.effective_from,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return _to_domain(sql_obj)

    def get_history(self, member_id: int, addon_id: int) -> List[AddonCommissionEntity]:
        rows = self.db.exec(
            select(AddonCommissionSQL)
            .where(AddonCommissionSQL.business_member_id == member_id)
            .where(AddonCommissionSQL.addon_id == addon_id)
            .order_by(AddonCommissionSQL.effective_from.desc())
        ).all()
        return [_to_domain(row) for row in rows]
