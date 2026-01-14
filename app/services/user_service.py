import logging
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import false
from sqlmodel import Session, select
from app.models.userModel import UserRead, UserCreate
from app.db.models.user import User
from app.services.Security import hash_password, verify_password
from jose import jwt, JWTError


ALGORITHM = "HS256"
SECRET_KEY = '1293482109740489759sdkfhgsd'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')

def create_user( user_in : UserCreate, session: Session) -> User:
    print("Add user")
    print(user_in.password)
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password = hash_password(user_in.password),
        is_active = True
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_id(session: Session, id: int) -> User | None:
    return session.get(User, id)
def get_user_by_email(session: Session, email: str) -> User:
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()

def authenticate_user(username: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id:int, expires_delta: timedelta):
    encode = {'sub': username, 'id':user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")