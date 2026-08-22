import datetime
from typing import Optional

from sqlmodel import select, Session

from app.domain.business.models.business_member_model import BusinessMember
from app.domain.business.models.business_model import Business
from app.domain.business.port.business_repository_port import BusinessRepositoryPort


class SQLModelBusinessRepositoryAdapter(BusinessRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, business: Business) -> Business:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def find_by_name(self, business_name: str) -> Business:
        return self.db.exec(
            select(Business).where(Business.name == business_name)
        ).first()

    def find_by_owner_id(self, business_owner_id: int) -> Business:
        return self.db.exec(
            select(Business).where(Business.owner_id == business_owner_id)
        ).all()

    def find_by_user(self, user_id: int, is_active: Optional[bool] = None) -> Business:
        """Get all businesses where user is a member"""

        statement = (
            select(Business)
            .join(BusinessMember, Business.id == BusinessMember.business_id)
            .where(BusinessMember.user_id == user_id)
        )

        if is_active is not None:
            statement = statement.where(Business.is_active == is_active)

        return self.db.exec(statement).all()

    def find_by_id(self, business_id: int) -> Business:
        return self.db.exec(select(Business).where(Business.id == business_id)).first()

    def find_by_id_and_user(self, business_id: int, user_id: int) -> Business:
        statement = (
            select(Business)
            .join(BusinessMember, Business.id == BusinessMember.business_id)
            .where(Business.id == business_id)
            .where(BusinessMember.user_id == user_id)
            .where(BusinessMember.is_active == True)
        )
        return self.db.exec(statement).first()

    def update(self, business_id: int, business: Business) -> Business:
        business = self.db.get(Business, business_id)

        if not business:
            return None

        update_data = business.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(business, key, value)

        business.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(business)
        return business

    def delete(self, business_id: int) -> Business:
        business = self.db.get(Business, business_id)

        if not business:
            return False

        self.db.delete(business)
        self.db.commit()
        return True