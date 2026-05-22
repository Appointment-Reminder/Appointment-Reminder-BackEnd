import pytest
from pydantic import ValidationError
from app.models.userModel import UserCreate

def test_empty_password():
    with pytest.raises(ValidationError):
        UserCreate(email="test@test.com", name="test", password="")

def test_white_space_password():
    with pytest.raises(ValidationError):
        UserCreate(email="test", name="test", password="    ")

def test_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email="test", name="test", password="abc")

def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="test", name="test", password="secret123")

def test_missing_name():
    with pytest.raises(ValidationError):
        UserCreate(email="test", password="secret123")

def test_valid_user_passes():
    user = UserCreate(email="test@test.com", name="test", password="secret123")
    assert user.email == "test@test.com"
