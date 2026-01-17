from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field

from app.db.models import TaskStatuses

class CreateTask(BaseModel):
    title: str = Field(description="Название задачи", max_length=255, min_length=1)
    description: Optional[str] = Field(description="Описание задачи", default=None)
    assignee_id: Optional[int] = Field(description="Исполнитель задачи", default=None)
    status: Literal[
        TaskStatuses.TO_DO, TaskStatuses.IN_PROGRESS, TaskStatuses.DONE, TaskStatuses.CANCELLED
    ] = Field(description="Статус задачи")


class ResponseTask(BaseModel):
    id: int = Field(description="Id задачи")
    title: str = Field(description="Название задачи")
    description: Optional[str] = Field(description="Описание задачи")
    assignee_id: Optional[int] = Field(description="Исполнитель задачи")
    status: str = Field(description="Статус задачи")
    created_at: datetime = Field(description="Дата создания задачи")
    updated_at: datetime = Field(description="Дата последнего обновления задачи")
    closed_at: Optional[datetime] = Field(description="Дата закрытия задачи")
    started_work_at: Optional[datetime] = Field(description="Дата взятия в работу задачи")


class UpdateTask(BaseModel):
    title: str = Field(description="Название задачи", default=None)
    description: str = Field(description="Описание задачи", default=None)
    assignee_id: Optional[int] = Field(description="Исполнитель задачи", default=None)
    status: str = Field(description="Статус задачи", default=None)
    closed_at: datetime = Field(description="Дата закрытия задачи", default=None)
    started_work_at: datetime = Field(description="Дата взятия в работу задачи", default=None)