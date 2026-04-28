from datetime import datetime
from typing import Optional, List

from sqlmodel import Session, select

from app.db.models.business_member import BusinessMember
from app.db.models.business import Business


##TODO FIX THE BUSINESS SERVICES WITH THE NEW BUSINESS REPOSITORY, ESPECIALLY FIX THE BUSINESS MEMBER ADD REPOSITORY AND UNIT TEST

class BusinessRepository:

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

    def find_by_owner_id(self, business_owner_id: int) -> List[Business]:
        return self.db.exec(
            select(Business).where(Business.owner_id == business_owner_id)
        ).all()

    def find_by_user(self, user_id: int, is_active: Optional[bool] = True ) -> List[Business]:
        query = (
            select(Business, BusinessMember.role)
            .join(BusinessMember, Business.id == BusinessMember.business_id)
            .where(BusinessMember.user_id == user_id)
        )

        if is_active is not None:
            query = query.where(BusinessMember.is_active == is_active)

        results = self.db.exec(query).all()
        return results

    def find_by_id(self, business_id: int) -> Business:
        return self.db.exec(select(Business).where(Business.id == business_id)).first()

    def update(self, business_id: int, business_data: Business) -> Business:
        business = self.db.get(Business, business_id)

        if not business:
            return None

        update_data = business_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(business, key, value)

        business.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(business)
        return business

    def delete(self, business_id: int) -> bool:
        business = self.db.get(Business, business_id)

        if not business:
            return False

        self.db.delete(business)
        self.db.commit()
        return True