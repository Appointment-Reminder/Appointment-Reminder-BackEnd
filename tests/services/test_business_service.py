from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.sql.functions import current_user

from app.models.business_model import BusinessCreate
from app.repositories.business_repository import BusinessRepository
from app.db.models.business import Business
from app.services import business_service
from app.db.models.business_member import BusinessMember, MemberRole
from app.db.models.user import User


@pytest.fixture
def business_repo():
    return Mock()

@pytest.fixture
def member_repo():
    return Mock()

@pytest.fixture
def fake_business():
    b = Business(name="Test", owner_id=1)
    b.id = 1
    b.is_active = True
    b.description = None
    b.created_at = datetime.utcnow()
    b.updated_at = datetime.utcnow()
    return b


def test_create_business(business_repo, member_repo, fake_business):
    business_repo.find_by_name.return_value = None
    business_repo.create.return_value = fake_business

    current_user = User(id=42, name="Test")
    member_repo.create.return_value = fake_business
    result = business_service.create_business(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_data = BusinessCreate(name="Test"),
    )

    business_repo.create.assert_called_once()
    member_repo.create.assert_called_once()

    created_member: BusinessMember = member_repo.create.call_args[0][0]
    assert created_member.role == MemberRole.OWNER
    assert created_member.user_id == 42
    assert result.name == "Test"