from datetime import datetime, date
from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

from app.db.models import TaskStatuses

class CreateTask(BaseModel):
    title: str = Field(description="Название задачи", max_length=255, min_length=1)
    description: Optional[str] = Field(description="Описание задачи", default=None)
    status: Literal[TaskStatuses.TO_DO.value] = Field(description="Статус задачи", default=TaskStatuses.TO_DO)


class ResponseTask(BaseModel):
    id: int = Field(description="Id задачи")
    title: str = Field(description="Название задачи")
    description: Optional[str] = Field(description="Описание задачи")
    assignee_id: int = Field(description="Исполнитель задачи")
    status: str = Field(description="Статус задачи")
    created_at: datetime = Field(description="Дата создания задачи")
    updated_at: datetime = Field(description="Дата последнего обновления задачи")
    closed_at: Optional[datetime] = Field(description="Дата закрытия задачи")
    started_work_at: Optional[datetime] = Field(description="Дата взятия в работу задачи")


class UpdateTask(BaseModel):
    title: str = Field(description="Название задачи", default=None)
    description: str = Field(description="Описание задачи", default=None)
    assignee_id: int = Field(description="Исполнитель задачи", default=None)
    status: str = Field(description="Статус задачи", default=None)
    closed_at: datetime = Field(description="Дата закрытия задачи", default=None)
    started_work_at: datetime = Field(description="Дата взятия в работу задачи", default=None)


class TaskFilter(BaseModel):
    title: Optional[str] = Query(None)
    status: Optional[str] = Query(None)
    assignee_id: Optional[int] = Query(None)
    created_at: Optional[date] = Query(None)
    closed_at: Optional[date] = Query(None)