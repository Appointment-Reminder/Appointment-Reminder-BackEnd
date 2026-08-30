import pytest
from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.models.business_member_model import MemberRole
from app.domain.business.models.business_model import Business
from app.domain.user.models.user import User


def test_create_business_makes_current_user_owner(business_service, member_repo, current_user):
    saved = business_service.create(
        data=Business(name="Sunset Studio", description="weddings", owner_id=None),
        current_user=current_user,
    )

    assert saved.owner_id == current_user.id
    members = member_repo.get_by_business_id(saved.id)
    assert len(members) == 1
    assert members[0].role == MemberRole.OWNER


def test_get_members_rejects_non_member(business_service, current_user):
    business = business_service.create(
        data=Business(name="Sunset Studio", description=None, owner_id=None),
        current_user=current_user,
    )
    stranger = User(id=99, email="x@x.com", name="Stranger", hashed_password="x")

    with pytest.raises(BusinessError):
        business_service.get_members(business_id=business.id, current_user=stranger)