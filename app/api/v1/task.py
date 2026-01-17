import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.schemes.task import ResponseTask, CreateTask, UpdateTask
from app.services.task import task_service

task_router = APIRouter()
logger = logging.getLogger(__name__)


@task_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseTask,
)
async def create_task(input: CreateTask):
    try:
        status = await task_service.create_task(input=input)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    return status


@task_router.get(
    "/{id}", status_code=HTTPStatus.OK, response_model=ResponseTask
)
async def get_task(id: int):
    task = await task_service.get_task(id)

    if task is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Задача c {id=} не найдена.",
        )

    return task


@task_router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_task(id: int):
    try:
        return await task_service.delete_task(id)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@task_router.patch(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=ResponseTask,
)
async def update_task(id: int, input: UpdateTask):
    try:
        status = await task_service.update_task(
            id, **input.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))

    return status


@task_router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=List[ResponseTask],
)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, gt=0, lt=101),
    sort_by: str = Query("id"),
    ascending: bool = Query(True)
):
    return await task_service.get_tasks(skip, limit, sort_by, ascending)
