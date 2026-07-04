from typing import List

from sqlmodel import Session, select

from app.db.models.package.package_price import PackagePrice
from datetime import datetime

class PackagePriceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, package_price: PackagePrice) -> PackagePrice:
        self.db.add(package_price)
        self.db.commit()
        self.db.refresh(package_price)
        return package_price

    def update(self, package_price_data: PackagePrice, package_price_id: int) -> PackagePrice:
        package_price = self.db.get(PackagePrice, package_price_id)

        if not package_price:
            return None

        update_data = package_price_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(package_price, key, value)

        self.db.commit()
        self.db.refresh(package_price)
        return package_price

    def delete(self, package_price_id: int) -> bool:
        package_price = self.db.get(PackagePrice, package_price_id)

        if not package_price:
            return False

        self.db.delete(package_price)
        self.db.commit()
        return True

    def get_price_at_date(self, package_id: int, date: datetime, is_personal: bool = True) -> PackagePrice:
        query = select(PackagePrice)
        query = query.where(PackagePrice.package_id == package_id)
        if is_personal:
            query = query.where(PackagePrice.is_personal == is_personal)

        query = ((query.where(PackagePrice.effective_from <= date)
                 .order_by(PackagePrice.effective_from.desc()))
                 .limit(1))

        return self.db.exec(query).one_or_none()

    def get_package_price(self, package_price_id: int) -> PackagePrice:
        query = select(PackagePrice, package_price_id)

        return self.db.exec(query).one_or_none()

    def get_current_price(self, package_id: int, is_personal) -> PackagePrice:
        query = select(PackagePrice)
        query = query.where(PackagePrice.package_id == package_id)
        if is_personal:
            query = query.where(PackagePrice.is_personal == is_personal)
        query = query.order_by(PackagePrice.effective_from.desc()).limit(1)
        return self.db.exec(query).first()

    def get_price_history(self, package_id: int) -> List[PackagePrice]:
        query = select(PackagePrice)
        query = (query.where(PackagePrice.package_id == package_id)
                 .order_by(PackagePrice.effective_from.desc()))

        return self.db.exec(query).all()
