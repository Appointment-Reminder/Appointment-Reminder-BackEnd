from typing import Dict, List, Optional

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

    def get_histories_for_member(self, member_id: int) -> Dict[int, List[AddonCommissionEntity]]:
        rows = self.db.exec(
            select(AddonCommissionSQL)
            .where(AddonCommissionSQL.business_member_id == member_id)
            .order_by(AddonCommissionSQL.effective_from.desc())
        ).all()
        histories: Dict[int, List[AddonCommissionEntity]] = {}
        for row in rows:
            histories.setdefault(row.addon_id, []).append(_to_domain(row))
        return histories

    def get_by_id(self, commission_id: int) -> Optional[AddonCommissionEntity]:
        row = self.db.get(AddonCommissionSQL, commission_id)
        return _to_domain(row) if row else None

    def update(self, commission: AddonCommissionEntity) -> AddonCommissionEntity:
        row = self.db.get(AddonCommissionSQL, commission.id)
        row.commission_amount = commission.commission_amount
        row.commission_isPercentage = commission.commission_isPercentage
        self.db.commit()
        self.db.refresh(row)
        return _to_domain(row)
