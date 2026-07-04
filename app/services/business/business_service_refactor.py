from datetime import datetime
from typing import Any, Optional, List


from app.models.business_member_model import BusinessMemberInvite, BusinessMemberUpdate
from app.models.business_model import BusinessCreate, BusinessUpdate
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.services.User.user_guard import UserGuard
from app.services.business.BusinessGuard import BusinessGuard
from app.db.models.business_member import BusinessMember, MemberRole
from app.db.models.user import User
from app.db.models.business import Business
from app.services.errors.BusinessErrors import OwnerRoleEditing, MemberRemoval



class BusinessService:
    def __init__(self,
                 business_repo: BusinessRepository,
                 member_repo: BusinessMemberRepository,
                 guard: BusinessGuard,
                 user_guard: UserGuard,
                 ):
        self.business_repo = business_repo
        self.member_repo = member_repo
        self.guard = guard
        self.user_guard = user_guard

    def create(self, data: BusinessCreate, current_user: User) -> BusinessMember:
        business = Business(
            name=data.name,
            description=data.description,
            owner_id=current_user.id,  # Pass the actual integer value
            is_active=True,
        )
        saved = self.business_repo.create(business)

        member = BusinessMember(
            business_id=saved.id,
            user_id=current_user.id,
            role=MemberRole.OWNER,
            joined_at=datetime.now(),
        )

        self.member_repo.create(member)
        return saved

    def get_for_user(self, current_user: User, is_active: Optional[bool], business_id: Optional[int]) -> BusinessMember:
        if business_id:
            return self.guard.ensure_exists(business_id=business_id)
        if is_active:
            return self.business_repo.find_by_user(user_id=current_user.id, is_active=is_active)

        return self.business_repo.find_by_user(user_id=current_user.id)

    def update(self, business_id: int, data: BusinessUpdate, current_user: User) -> BusinessMember:
        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        return self.business_repo.update(business_id=business_id, business_data=data)

    def delete(self, business_id: int, current_user: User) -> BusinessMember:
        self.delete_all_members(business_id=business_id, current_user=current_user)
        return self.business_repo.delete(business_id=business_id)

    def delete_all_members(self, business_id: int, current_user: User) -> BusinessMember:
        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        members = self.member_repo.get_by_business_id(business_id)

        for member in members:
            self.member_repo.delete(member.id)


    def invite_member(self, business_id: int, current_user: User, invite_data: BusinessMemberInvite) -> BusinessMember:
        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)

        invited = self.user_guard.ensure_user_email_exists(invite_data.user_email)
        self.guard.ensure_not_a_member(business_id=business_id, user_id=invited.id)

        new_member = BusinessMember(
            business_id=business_id,
            user_id=invited.id,
            role=invite_data.role,
            invited_by=current_user.id
        )

        return  self.member_repo.create(new_member)

    def get_members(self, business_id: int, current_user: User) -> List[BusinessMember]:
        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        return self.member_repo.get_by_business_id(business_id=business_id)

    def update_member(self, data: BusinessMemberUpdate, member_id: int, business_id: int, current_user: User) -> BusinessMember:

        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        member = self.guard.ensure_member_exist(member_id)
        self.guard.ensure_is_a_member(business_id= business_id, user_id=member.user_id)

        if member.role == MemberRole.OWNER and data.role != MemberRole.OWNER:
            raise OwnerRoleEditing(current_user.id, business_id)()

        if (data.role == MemberRole.OWNER and
                member.role != MemberRole.OWNER):
            raise OwnerRoleEditing(current_user.id, business_id)

        if data.role is not None:
            member.role = data.role
        if data.is_active is not None:
            member.is_active = data.is_active

        updated_member = self.member_repo.update(member)
        return updated_member

    def delete_member(self, business_id: int, member_id: int, current_user: User) -> BusinessMember:
        self.guard.ensure_exists(business_id=business_id)
        self.guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        member = self.guard.ensure_is_a_member(business_id=business_id, user_id=member_id)

        if member.role == MemberRole.OWNER:
            raise OwnerRoleEditing(current_user.id, member.business_id)

        if member.user_id == current_user.id:
            raise MemberRemoval(current_user.id, member.user_id, member.business_id)

        self.member_repo.delete(member.id)



    def _to_dict(self, data: Business, role: str) -> dict[str, Any]:
        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            "owner_id": data.owner_id,
            "is_active": data.is_active,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "my_role": role,
        }

