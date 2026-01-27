import logging
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from app.schemes.auth import LoginData, Token
from app.schemes.user import CreateUser, ResponseUser
from app.security.auth import auth_service
from app.services.user import user_service

auth_router = APIRouter()
logger = logging.getLogger(__name__)
REGISTRATION_TAG = "Регистрация пользователя"


@auth_router.post(
    "/register",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseUser,
    tags=[REGISTRATION_TAG],
)
async def register_user(input: CreateUser):
    try:
        user = await user_service.create_user(input=input)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    return user


@auth_router.post(
    "/token",
    status_code=HTTPStatus.OK,
    response_model=Token,
    tags=[REGISTRATION_TAG],
)
async def login_for_access_token(input: LoginData):
    user = await user_service.get_user_by_email(input.email)

    if not user or not auth_service.verify_password(
        input.password, user.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"Authorization": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}
