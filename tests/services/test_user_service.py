from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.models.userModel import UserCreate
from app.services import user_service
from app.db.models.user import User


@pytest.fixture
def user_repo():
    return Mock()

@pytest.fixture
def user_create():
    return UserCreate(email="test@test.com", name="test", password="secret123")

@pytest.fixture
def fake_user():
    u = User()
    u.id = 1
    u.email = "test@test.com"
    u.name = "test"
    u.hashed_password = "hashed_secret"
    return u

def test_create_user_hashes_password(user_repo, user_create):
    user_repo.create.side_effect = lambda user: user

    result = user_service.create_user(
        user_in=user_create,
        repository = user_repo
    )

    assert result.hashed_password != "secret123"
    assert len(result.hashed_password) > 20

def test_create_user_calls_repo_once(user_repo, user_create):
    user_repo.create.side_effect = lambda user: user

    user_service.create_user(
        user_create,
        user_repo
    )

    user_repo.create.assert_called_once()

def test_authenticate_not_found_user(user_repo):
    user_repo.get_by_email.return_value = None

    result = user_service.authenticate_user(repo=user_repo, email="test@test.com", password="secret123")

    assert result is None

def test_authenticate_user_return_none_when_wrong_password(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    with patch("app.services.user_service.verify_password", return_value=False):
        result = user_service.authenticate_user("test@test.com", "hashed_secret", user_repo)

    assert result is None

def test_authenticate_user_returns_user_when_correct(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    with patch("app.services.user_service.verify_password", return_value=True):
        result = user_service.authenticate_user("test@test.com", "hashed_secret", user_repo)

    assert result is not None
    assert result.email == "test@test.com"

def test_authenticate_user_calls_verify_password_with_correct_args(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    with patch("app.services.user_service.verify_password", return_value=True) as mock_verify:
        user_service.authenticate_user("test@test.com", "secret123", user_repo)

        mock_verify.assert_called_once_with("secret123", "hashed_secret")

def test_authenticate_user_does_not_call_verify_password_when_user_not_found(user_repo):
    user_repo.get_by_email.return_value = None

    with patch("app.services.user_service.verify_password") as mock_verify:
        user_service.authenticate_user("ghost@studio.com", "secret123", user_repo)

        mock_verify.assert_not_called()

def test_authenticate_user_calls_repo_once(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    # patch verify_password to simulate a wrong password
    with patch("app.services.user_service.verify_password", return_value=False):
        result = user_service.authenticate_user("test@test.com", "hashed_secret", user_repo)

    user_repo.get_by_email.assert_called_once()

def test_create_access_token_add_id_to_payload():
    with patch("app.services.user_service.jwt.encode") as mock_encode:
        result = user_service.create_access_token(
            username="test@test.com",
            user_id=1,
            expires_delta=timedelta(minutes=20),
        )

        call_args = mock_encode.call_args
        payload = call_args[0][0]
        assert payload["id"] == 1

def test_create_access_token_add_sub_to_payload():
    with patch("app.services.user_service.jwt.encode") as mock_encode:
        result = user_service.create_access_token(
            username="test@test.com",
            user_id=1,
            expires_delta=timedelta(minutes=20),
        )

        call_args = mock_encode.call_args
        payload = call_args[0][0]
        assert payload["sub"] == "test@test.com"

def test_create_access_token_add_expiracy_data_to_payload():
    with patch("app.services.user_service.jwt.encode") as mock_encode:
        result = user_service.create_access_token(
            username="test@test.com",
            user_id=1,
            expires_delta=timedelta(minutes=20),
        )

        call_args = mock_encode.call_args
        payload = call_args[0][0]
        assert "exp" in payload

def test_create_access_token_return_token():
    with patch("app.services.user_service.jwt.encode", return_value="fake.jwt.token") as mock_encode:
        result = user_service.create_access_token(
            username="test@test.com",
            user_id=1,
            expires_delta=timedelta(minutes=20),
        )

        mock_encode.assert_called_once()

        # Check the specific args it was called with
        call_args = mock_encode.call_args
        payload = call_args[0][0]  # first positional arg
        secret = call_args[0][1]  # second positional arg
        algorithm = call_args[1]["algorithm"]  # keyword arg

        assert secret == user_service.SECRET_KEY
        assert algorithm == user_service.ALGORITHM
        assert result == "fake.jwt.token"

def test_decode_token_returns_email_and_user_id():
    valid_payload = {"sub": "test@test.com", "id":1}

    with patch("app.services.user_service.jwt.decode", return_value=valid_payload):
        email, user_id = user_service.decode_token("fake.jwt.token")

    assert email == "test@test.com"
    assert user_id == 1

def test_decode_token_raises_401_on_invalid_token():
    from jose import JWTError

    with patch("app.services.user_service.jwt.decode", side_effect=JWTError()):
        with pytest.raises(HTTPException) as exc_info:
            user_service.decode_token("bad.token.here")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"

def test_decode_token_raises_401_when_email_missing():
    payload_without_email = {"id": 1}  # no "sub"

    with patch("app.services.user_service.jwt.decode", return_value=payload_without_email):
        with pytest.raises(HTTPException) as exc_info:
            user_service.decode_token("fake.jwt.token")

    assert exc_info.value.status_code == 401

def test_decode_token_raises_401_when_user_id_missing():
    payload_without_id = {"sub": "test@test.com"}  # no "id"

    with patch("app.services.user_service.jwt.decode", return_value=payload_without_id):
        with pytest.raises(HTTPException) as exc_info:
            user_service.decode_token("fake.jwt.token")

    assert exc_info.value.status_code == 401


def test_decode_token_calls_jwt_decode_with_correct_args():
    valid_payload = {"sub": "test@test.com", "id": 1}

    with patch("app.services.user_service.jwt.decode", return_value=valid_payload) as mock_decode:
        user_service.decode_token("fake.jwt.token")

        mock_decode.assert_called_once_with(
            "fake.jwt.token",
            user_service.SECRET_KEY,
            algorithms=[user_service.ALGORITHM],
        )

def test_get_user_by_id_user_found(user_repo, fake_user):
    user_repo.get_by_id.return_value = fake_user

    result = user_service.get_user_by_id(repo=user_repo, user_id=1)

    assert isinstance(result, User)
    assert result is fake_user

def test_get_user_by_id_returns_none_when_user_not_found(user_repo):
    user_repo.get_by_id.return_value = None

    result = user_service.get_user_by_id(repo=user_repo, user_id=1)

    assert result is None

def test_get_user_by_id_calls_repo_get_user_by_id(user_repo, fake_user):
    user_repo.get_by_id.return_value = fake_user

    result = user_service.get_user_by_id(repo=user_repo, user_id=1)

    user_repo.get_by_id.assert_called_once_with(1)

def test_get_user_by_email_returns_none_when_user_not_found(user_repo):
    user_repo.get_by_email.return_value = None

    result = user_service.get_user_by_email(repo=user_repo, email="test@test.com")

    assert result is None

def test_get_user_by_email_user_found(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    result = user_service.get_user_by_email(repo=user_repo, email="test@test.com")

    assert isinstance(result, User)
    assert result is fake_user

def test_get_user_by_email_calls_repo_get_user_by_email(user_repo, fake_user):
    user_repo.get_by_email.return_value = fake_user

    result = user_service.get_user_by_email(repo=user_repo, email="test@test.com")

    user_repo.get_by_email.assert_called_once_with("test@test.com")