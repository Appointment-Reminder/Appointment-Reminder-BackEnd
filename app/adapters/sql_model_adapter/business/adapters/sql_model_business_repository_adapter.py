import datetime
from typing import Optional, List

from sqlmodel import select, Session

from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember as BusinessMemberSQL
from app.domain.business.port.business_repository_port import BusinessRepositoryPort

from app.adapters.sql_model_adapter.business.models.business import Business as BusinessSQL, _to_domain as business_to_domain, _apply_to_sql as business_apply_to_sql
from app.domain.business.models.business_model import Business as BusinessEntity


class SQLModelBusinessRepositoryAdapter(BusinessRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, business: BusinessEntity) -> BusinessEntity:
        sql_business = BusinessSQL(
            name=business.name,
            description=business.description,
            owner_id=business.owner_id,
        )
        self.db.add(sql_business)
        self.db.commit()
        self.db.refresh(sql_business)
        return business_to_domain(sql_business)

    def find_by_name(self, business_name: str) -> BusinessEntity:
        result = self.db.exec(
            select(BusinessSQL).where(BusinessSQL.name == business_name)
        ).first()
        return business_to_domain(result)

    def find_by_owner_id(self, business_owner_id: int) -> BusinessEntity:
        result = self.db.exec(
            select(BusinessSQL).where(BusinessSQL.owner_id == business_owner_id)
        ).all()
        return business_to_domain(result)


    def find_by_user(self, user_id: int, is_active: Optional[bool] = None) -> List[BusinessEntity]:
        """Get all businesses where user is a member"""

        statement = (
            select(BusinessSQL)
            .join(BusinessMemberSQL, BusinessSQL.id == BusinessMemberSQL.business_id)
            .where(BusinessMemberSQL.user_id == user_id)
        )

        if is_active is not None:
            statement = statement.where(BusinessSQL.is_active == is_active)

        resut = self.db.exec(statement).all()
        return [business_to_domain(business) for business in resut]

    def find_by_id(self, business_id: int) -> BusinessEntity:
        return self.db.exec(select(BusinessSQL).where(BusinessSQL.id == business_id)).first()

    def find_by_id_and_user(self, business_id: int, user_id: int) -> BusinessEntity:
        statement = (
            select(BusinessSQL)
            .join(BusinessMemberSQL, BusinessSQL.id == BusinessMemberSQL.business_id)
            .where(BusinessSQL.id == business_id)
            .where(BusinessMemberSQL.user_id == user_id)
            .where(BusinessMemberSQL.is_active == True)
        )
        result =  self.db.exec(statement).first()
        return business_to_domain(result)

    def update(self, business_id: int, business: BusinessEntity) -> BusinessEntity:
        existing = self.db.get(BusinessSQL, business_id)

        if not existing:
            return None

        business_apply_to_sql(entity=business, sql=existing)

        existing.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(existing)
        return business_to_domain(existing)

    def delete(self, business_id: int) -> bool:
        business = self.db.get(BusinessSQL, business_id)

        if not business:
            return False

        self.db.delete(business)
        self.db.commit()
        return True