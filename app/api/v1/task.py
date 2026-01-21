import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException, Query, Depends

from app.db.models import User, UserRoles
from app.schemes.task import ResponseTask, CreateTask, UpdateTask
from app.security.auth import auth_service
from app.services.task import task_service

task_router = APIRouter()
logger = logging.getLogger(__name__)
TASKS_TAG = "Задачи"


@task_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseTask,
    tags=[TASKS_TAG],
)
async def create_task(
    input: CreateTask,
    current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        status = await task_service.create_task(current_user, input=input)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    return status


@task_router.get(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=ResponseTask,
    tags=[TASKS_TAG],
)
async def get_task(
    id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    task = await task_service.get_task(current_user, id)

    if task is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Задача c {id=} не найдена.",
        )

    return task


@task_router.delete(
    "/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    tags=[TASKS_TAG],
)
async def delete_task(
    id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        return await task_service.delete_task(id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@task_router.patch(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=ResponseTask,
    tags=[TASKS_TAG],
)
async def update_task(
    id: int,
    input: UpdateTask,
    current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        status = await task_service.update_task(
            id, current_user, **input.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))

    return status


@task_router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=List[ResponseTask],
    tags=[TASKS_TAG],
)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, gt=0, lt=101),
    sort_by: str = Query("id"),
    ascending: bool = Query(True),
    current_user: User = Depends(auth_service.get_current_user)
):
    await auth_service.check_required_role(
        current_user, [UserRoles.ADMIN, UserRoles.USER]
    )

    try:
        return await task_service.get_tasks(skip, limit, sort_by, ascending, current_user)
    except AttributeError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
