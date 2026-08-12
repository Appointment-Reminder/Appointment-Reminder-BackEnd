from typing import List

from sqlmodel import Session, select

from app.db.models.Jotform.jotform import JotformCredential
from app.services.business.BusinessGuard import BusinessGuard


class JotformRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_credential(self, credential: JotformCredential) -> JotformCredential:
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def get_credential_by_business_id(self, business_id: int) -> List[JotformCredential]:
        return self.db.exec(
            select(JotformCredential)
            .where(JotformCredential.business_id == business_id)
        ).all()