from typing import Dict, List

from sqlalchemy.orm import Session
from sqlmodel import select

from app.adapters.sql_model_adapter.addon.models.addon_price import AddonPrice as AddonPriceSQL, _to_domain
from app.domain.addon.models.addon_price import AddonPrice as AddonPriceEntity
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort


class SQLModelAddonPriceRepositoryAdapter(AddonPriceRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, addon_price: AddonPriceEntity) -> AddonPriceEntity:
        sql_obj = AddonPriceSQL(
            addon_id=addon_price.addon_id,
            price=addon_price.price,
            effective_from=addon_price.effective_from,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return _to_domain(sql_obj)

    def get_history(self, addon_id: int) -> List[AddonPriceEntity]:
        rows = self.db.exec(
            select(AddonPriceSQL)
            .where(AddonPriceSQL.addon_id == addon_id)
            .order_by(AddonPriceSQL.effective_from.desc())
        ).all()
        return [_to_domain(row) for row in rows]

    def get_histories(self, addon_ids: List[int]) -> Dict[int, List[AddonPriceEntity]]:
        if not addon_ids:
            return {}
        rows = self.db.exec(
            select(AddonPriceSQL)
            .where(AddonPriceSQL.addon_id.in_(addon_ids))
            .order_by(AddonPriceSQL.effective_from.desc())
        ).all()
        histories: Dict[int, List[AddonPriceEntity]] = {}
        for row in rows:
            histories.setdefault(row.addon_id, []).append(_to_domain(row))
        return histories
