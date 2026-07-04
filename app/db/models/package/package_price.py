from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class PackagePrice(SQLModel, table=True):
    __tablename__ = "package_price"

    id: Optional[int] = Field(default=None, primary_key=True)
    package_id: Optional[int] = Field(default=None, foreign_key='package.id')
    total_price: int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime

