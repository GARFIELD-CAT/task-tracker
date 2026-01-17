import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.schemes.task import CreateTask, ResponseTask

task_router = APIRouter()
logger = logging.getLogger(__name__)


@task_router.get("/{id}")
def get_task(id: int):
    return {"task_id": id}


@task_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ResponseTask,
)
def create_task(input: CreateTask):
    task = ResponseTask(id=1, name=input.name)

    return task