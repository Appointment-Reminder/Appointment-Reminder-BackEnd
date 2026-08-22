
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer

from app.domain.user.errors.user_errors import UserError
from app.domain.user.models.user import User
from app.domain.user.port.user_repository_port import UserRepositoryPort

from jose import jwt, JWTError

from app.domain.user.service.security import hash_password, verify_password

ALGORITHM = "HS256"
SECRET_KEY = '1293482109740489759sdkfhgsd'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')

def create_user( user_in : User, repository: UserRepositoryPort) -> User:
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password = hash_password(user_in.password),
    )

    repository.create(user)
    return user

def get_user_by_id(user_id: int, repo: UserRepositoryPort) -> User | None:
    return repo.get_by_id(user_id)
def get_user_by_email(email: str, repo: UserRepositoryPort) -> User | None:
    return repo.get_by_email(email)

def authenticate_user(email: str, password: str, repo: UserRepositoryPort) -> User | None:
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
            raise UserError()
        return email, user_id
    except JWTError:
        raise UserError()