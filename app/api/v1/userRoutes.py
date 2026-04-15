from datetime import timedelta
from typing import Annotated

from fastapi import routing, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.userModel import UserCreate, UserRead
from app.db.models.user import User
from app.db.models.token import Token
from app.services import user_service
from app.services.user_service import authenticate_user, create_access_token, get_current_user

userRouter = APIRouter(
    prefix="/users",
    tags=["user"]
)

@userRouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(user.email, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer", "user": user};

@userRouter.post("", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    existing = user_service.get_user_by_email(session, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return user_service.create_user(user, session)

@userRouter.get("/{user_id}", response_model=UserRead)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user= user_service.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.get("/by-email/{email}", response_model=UserRead)
def get_user_by_email(
    email: str,
    session: Session = Depends(get_session),
):
    user = user_service.get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.get("", response_model=list[UserRead])
def get_users(
    session: Session = Depends(get_session),
):
    users = session.exec(select(User)).all()
    return users

@userRouter.get("/", status_code=200)
async def user( current_user: Annotated[User, Depends(get_current_user)]):
    print("Get current user")
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"User": current_user}

