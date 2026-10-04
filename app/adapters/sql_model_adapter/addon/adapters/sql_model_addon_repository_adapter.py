from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlmodel import select

from app.adapters.sql_model_adapter.addon.models.addon import Addon as AddonSQL, _to_domain, _apply_sql
from app.domain.addon.models.addon import Addon as AddonEntity
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort


class SQLModelAddonRepositoryAdapter(AddonRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, addon: AddonEntity) -> AddonEntity:
        sql_obj = AddonSQL(
            business_id=addon.business_id,
            category_id=addon.category_id,
            name=addon.name,
            jotform_alias=addon.jotform_alias,
            is_active=addon.is_active,
            has_duration=addon.has_duration,
            has_quantity=addon.has_quantity,
            duration_minutes=addon.duration_minutes,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return _to_domain(sql_obj)

    def update(self, addon: AddonEntity) -> Optional[AddonEntity]:
        existing = self.db.get(AddonSQL, addon.id)
        if not existing:
            return None
        _apply_sql(existing, addon)
        self.db.commit()
        self.db.refresh(existing)
        return _to_domain(existing)

    def get_by_id(self, addon_id: int) -> Optional[AddonEntity]:
        row = self.db.get(AddonSQL, addon_id)
        return _to_domain(row) if row else None

    def list_by_business(self, business_id: int, is_active: Optional[bool] = None) -> List[AddonEntity]:
        query = select(AddonSQL).where(AddonSQL.business_id == business_id)
        if is_active is not None:
            query = query.where(AddonSQL.is_active == is_active)
        return [_to_domain(row) for row in self.db.exec(query.order_by(AddonSQL.name)).all()]

    def find_by_alias(self, business_id: int, alias: str) -> List[AddonEntity]:
        normalized = alias.replace(" ", " ").strip()
        rows = self.db.exec(
            select(AddonSQL)
            .where(AddonSQL.business_id == business_id)
            .where(func.trim(func.replace(AddonSQL.jotform_alias, " ", " ")) == normalized)
        ).all()
        return [_to_domain(row) for row in rows]
