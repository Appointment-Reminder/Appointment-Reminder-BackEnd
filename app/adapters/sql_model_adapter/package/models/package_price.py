from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.package.models.package_price import PackagePrice as PackagePriceEntity
class PackagePrice(SQLModel, table=True):
    __tablename__ = "package_price"

    id: Optional[int] = Field(default=None, primary_key=True)
    package_id: Optional[int] = Field(default=None, foreign_key='package.id')
    total_price: int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime

def _to_domain(sql: PackagePrice) -> PackagePriceEntity:
    return PackagePriceEntity(
        id=sql.id,
        package_id=sql.package_id,
        total_price=sql.total_price,
        deposit_amount=sql.deposit_amount,
        remaining_amount=sql.remaining_amount,
        is_personal=sql.is_personal,
        effective_from=sql.effective_from,
    )

def _apply_sql(sql: PackagePrice, obj: PackagePriceEntity) -> None:
    sql.package_id = obj.package_id
    sql.total_price = obj.total_price
    sql.deposit_amount = obj.deposit_amount
    sql.remaining_amount = obj.remaining_amount
    sql.is_personal = obj.is_personal
    sql.effective_from = obj.effective_from
