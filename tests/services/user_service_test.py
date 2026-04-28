from unittest.mock import Mock

import pytest

from app.models.userModel import UserCreate
from app.services import user_service


@pytest.fixture
def user_repo():
    return Mock()

def test_create_user_hashes_password(user_repo):
    user_repo.create.side_effect = lambda user: user

    result = user_service.create_user(
        user_in=UserCreate(email="test@test.com", name="test", password="secret123"),
        repository = user_repo
    )

    assert result.hashed_password != "secret123"
    assert len(result.hashed_password) > 20