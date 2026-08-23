from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from sqlmodel import select

from app.domain.package.models.package_price import PackagePrice as PackagePriceEntity

from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice as PackagePriceSQL, _to_domain as package_price_to_domain, _apply_sql as package_price_apply_sql
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort


class SQLModelPackagePriceRepositoryAdapter(PackagePriceRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, package_price: PackagePriceEntity) -> PackagePriceEntity:
        sql_obj = PackagePriceSQL(
            package_id=package_price.package_id,
            total_price=package_price.total_price,
            deposit_amount=package_price.deposit_amount,
            remaining_amount=package_price.remaining_amount,
            is_personal=package_price.is_personal,
            effective_from=package_price.effective_from,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return package_price_to_domain(sql_obj)

    def update(self, package_price: PackagePriceEntity, package_price_id: int) -> PackagePriceEntity:
        existing = self.db.get(PackagePriceSQL, package_price_id)

        if not existing:
            return None

        package_price_apply_sql(existing, package_price)

        self.db.commit()
        self.db.refresh(existing)
        return package_price_to_domain(existing)

    def delete(self, package_price_id: int) -> bool:
        package_price = self.db.get(PackagePriceSQL, package_price_id)

        if not package_price:
            return False

        self.db.delete(package_price)
        self.db.commit()
        return True

    def get_price_at_date(self, package_id: int, date: datetime) -> PackagePriceEntity:
        query = select(PackagePriceSQL)
        query = query.where(PackagePriceSQL.package_id == package_id)

        query = ((query.where(PackagePriceSQL.effective_from <= date)
                  .order_by(PackagePriceSQL.effective_from.desc()))
                 .limit(1))

        result = self.db.exec(query).one_or_none()
        return package_price_to_domain(result) if result else None

    def get_package_price(self, package_price_id: int) -> PackagePriceEntity:
        query = select(PackagePriceSQL).where(PackagePriceSQL.id == package_price_id)

        result = self.db.exec(query).one_or_none()
        return package_price_to_domain(result) if result else None

    def get_current_price(self, package_id: int) -> PackagePriceEntity:
        query = select(PackagePriceSQL)
        query = query.where(PackagePriceSQL.package_id == package_id)
        query = query.order_by(PackagePriceSQL.effective_from.desc()).limit(1)
        result = self.db.exec(query).first()
        return package_price_to_domain(result) if result else None

    def get_price_history(self, package_id: int) -> List[PackagePriceEntity]:
        query = select(PackagePriceSQL)
        query = (query.where(PackagePriceSQL.package_id == package_id)
                 .order_by(PackagePriceSQL.effective_from.desc()))
        result = self.db.exec(query).all()

        return [package_price_to_domain(p) for p in result] if result else []