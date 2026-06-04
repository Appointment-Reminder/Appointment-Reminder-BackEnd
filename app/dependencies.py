from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlmodel import Session

from app.db.models.user import User
from app.db.session import get_session
from app.repositories.appointments.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.user_repository import UserRepository
from app.services import user_service
from app.services.user_service import oauth2_bearer


def get_user_repository(db:  Annotated[Session, Depends(get_session)]) -> UserRepository:
    return UserRepository(db)

def get_appointment_repository(db:  Annotated[Session, Depends(get_session)]) -> AppointmentRepository:
    return AppointmentRepository(db)

def get_business_member_repository(db:  Annotated[Session, Depends(get_session)]) -> BusinessMemberRepository:
    return BusinessMemberRepository(db)
def get_business_repository(db:  Annotated[Session, Depends(get_session)]) -> BusinessRepository:
    return BusinessRepository(db)


def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    # decode_token raises HTTPException itself if invalid
    _, user_id = user_service.decode_token(token)

    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    assert user.id is not None, "Database user must have an id"

    return user

USER_REPOSITORY_DEPENDENCY = Annotated[UserRepository, Depends(get_user_repository)]
APPOINTMENT_REPOSITORY_DEPENDENCY = Annotated[AppointmentRepository, Depends(get_appointment_repository)]
BUSINESS_MEMBER_REPO_DEP = Annotated[BusinessMemberRepository, Depends(get_business_member_repository)]
BUSINESS_REPO_DEP = Annotated[BusinessRepository, Depends(get_business_repository)]
CURRENT_USER_DEPENDENCY = Annotated[User, Depends(get_current_user)]