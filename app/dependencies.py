from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlmodel import Session

from app.db.models.user import User
from app.db.session import get_session
from app.repositories.appointments.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.packages.package_price_repository import PackagePriceRepository
from app.repositories.packages.packages_repository import PackagesRepository
from app.repositories.user_repository import UserRepository
from app.services import user_service
from app.services.User.user_guard import UserGuard
from app.services.business.BusinessGuard import BusinessGuard
from app.services.business.business_service_refactor import BusinessService
from app.services.package.package_guard import PackageGuard
from app.services.package.package_service import PackageService
from app.services.user_service import oauth2_bearer
from app.db.models.Member.member_commision import MemberCommission

def get_user_repository(db:  Annotated[Session, Depends(get_session)]) -> UserRepository:
    return UserRepository(db)

def get_appointment_repository(db:  Annotated[Session, Depends(get_session)]) -> AppointmentRepository:
    return AppointmentRepository(db)

def get_business_member_repository(db:  Annotated[Session, Depends(get_session)]) -> BusinessMemberRepository:
    return BusinessMemberRepository(db)
def get_business_repository(db:  Annotated[Session, Depends(get_session)]) -> BusinessRepository:
    return BusinessRepository(db)

def get_package_repo(db: Annotated[Session, Depends(get_session)]) -> PackagesRepository:
    return PackagesRepository(db)

def get_package_price_repo(db: Annotated[Session, Depends(get_session)]) -> PackagePriceRepository:
    return PackagePriceRepository(db)

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
PACKAGE_REPO = Annotated[PackagesRepository, Depends(get_package_repo)]
PACKAGE_PRICE_REPO = Annotated[PackagePriceRepository, Depends(get_package_price_repo)]
CURRENT_USER_DEPENDENCY = Annotated[User, Depends(get_current_user)]

def get_business_guard(business_repo: BUSINESS_REPO_DEP,
                       member_repo: BUSINESS_MEMBER_REPO_DEP,
                       ) -> BusinessGuard:
    return BusinessGuard(business_repo, member_repo)

def get_user_guard(user_repo: USER_REPOSITORY_DEPENDENCY) -> UserGuard:
    return UserGuard(user_repo=user_repo)

def get_business_service(
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        guard: Annotated[BusinessGuard, Depends(get_business_guard)],
        user_guard: Annotated[UserGuard, Depends(get_user_guard)]
) -> BusinessService:
    return BusinessService(business_repo=business_repo,
                           member_repo=member_repo,
                           guard=guard,
                           user_guard=user_guard)

def get_package_guard(package_repo: PACKAGE_REPO,
                      package_price_repo: PACKAGE_PRICE_REPO,
                      ) -> PackageGuard:
    return PackageGuard(package_repo, package_price_repo)

def get_package_service(package_repo: PACKAGE_REPO,
                        price_repo: PACKAGE_PRICE_REPO,
                        member_repo: BUSINESS_MEMBER_REPO_DEP,
                        business_guard: Annotated[BusinessGuard, Depends(get_business_guard)],
                        package_guard: Annotated[PackageGuard, Depends(get_package_guard)],
                        ) -> PackageService:
    return PackageService(package_repo=package_repo,
                          price_repo=price_repo,
                          member_repo=member_repo,
                          business_guard=business_guard,
                          packages_guard=package_guard)

USER_GUARD_DEPENDENCY = Annotated[User, Depends(get_user_guard)]
BUSINESS_GUARD_DEP = Annotated[BusinessGuard, Depends(get_business_guard)]
BUSINESS_SERVICE_DEP = Annotated[BusinessService, Depends(get_business_service)]
PACKAGE_GUARD_DEP = Annotated[PackageGuard, Depends(get_package_guard)]
PACKAGE_SERVICE_DEP = Annotated[PackageService, Depends(get_package_service)]