from datetime import timedelta
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject, DishkaRoute
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.models.userModel import UserCreate, UserRead
from app.domain.user.models.token import Token

from app.domain.user.models.user import User
from app.domain.user.port.user_repository_port import UserRepositoryPort
from app.domain.user.service import user_service




userRouter = APIRouter(
    prefix="/users",
    tags=["user"],
    route_class=DishkaRoute,
)

@userRouter.post("/token", response_model=Token)
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: FromDishka[UserRepositoryPort],
):
    user = user_service.authenticate_user(form_data.username, form_data.password, repo)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = user_service.create_access_token(user.email, user.id, timedelta(days=60))
    return {"access_token": token, "token_type": "bearer", "user": user}

@userRouter.post("", response_model=UserRead, status_code=201)
def create_user(user_in: UserCreate, repo: FromDishka[UserRepositoryPort]):
    if user_service.get_user_by_email(user_in.email, repo):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(user_in, repo)

@userRouter.get("/me", response_model=UserRead)
def get_me(current_user: FromDishka[User]):
    return current_user

@userRouter.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, repo: FromDishka[UserRepositoryPort]):
    user = user_service.get_user_by_id(user_id, repo)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




