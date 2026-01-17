from pydantic import BaseModel, Field


class CreateTask(BaseModel):
    name: str = Field(description="Название задачи")


class ResponseTask(BaseModel):
    id: int = Field(description="Id задачи")
    name: str = Field(description="Название задачи")
