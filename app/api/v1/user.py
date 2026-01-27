import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.models import User, UserRoles
from app.schemes.user import CreateUser, ResponseUser, UpdateUser, UserFilter
from app.security.auth import auth_service
from app.services.user import user_service

user_router = APIRouter()
logger = logging.getLogger(__name__)
USERS_TAG = "Пользователи"


@user_router.get(
    "/me",
    status_code=HTTPStatus.OK,
    response_model=ResponseUser,
    tags=[USERS_TAG],
)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    return current_user


@user_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseUser,
    tags=[USERS_TAG],
)
async def create_user(
    input: CreateUser,
    current_user: User = Depends(auth_service.get_current_user),
):
    await auth_service.check_required_role(current_user, [UserRoles.ADMIN])

    try:
        status = await user_service.create_user(input=input)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    return status


@user_router.get(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=ResponseUser,
    tags=[USERS_TAG],
)
async def get_user(
    id: int, current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(current_user, [UserRoles.ADMIN])

    task = await user_service.get_user_by_id(id)

    if task is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Пользователь c {id=} не найден.",
        )

    return task


@user_router.delete(
    "/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    tags=[USERS_TAG],
)
async def delete_user(
    id: int, current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        return await user_service.delete_user(id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@user_router.patch(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=ResponseUser,
    tags=[USERS_TAG],
)
async def update_user(
    id: int,
    input: UpdateUser,
    current_user: User = Depends(auth_service.get_current_user),
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        status = await user_service.update_user(
            id, current_user, **input.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))

    return status


@user_router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=List[ResponseUser],
    tags=[USERS_TAG],
)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, gt=0, lt=101),
    sort_by: str = Query("id"),
    ascending: bool = Query(True),
    filter: UserFilter = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    await auth_service.check_required_role(current_user, [UserRoles.ADMIN])

    try:
        return await user_service.get_users(
            skip, limit, sort_by, ascending, filter
        )
    except AttributeError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
