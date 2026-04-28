import logging
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.userModel import UserRead, UserCreate
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.Security import hash_password, verify_password
from jose import jwt, JWTError


ALGORITHM = "HS256"
SECRET_KEY = '1293482109740489759sdkfhgsd'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')

def create_user( user_in : UserCreate, repository: UserRepository) -> User:
    print("Add user")
    print(user_in.password)
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password = hash_password(user_in.password),
        is_active = True
    )

    repository.create(user)
    return user


def get_user_by_id(user_id: int, repo: UserRepository) -> User | None:
    return repo.get_by_id(user_id)
def get_user_by_email(email: str, repo: UserRepository) -> User | None:
    return repo.get_by_email(email)

def authenticate_user(email: str, password: str, repo: UserRepository) -> User | None:
    user = repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    payload = {
        "sub": username,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> tuple[str, int]:
    """Decode JWT and return (email, user_id). Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email, user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")