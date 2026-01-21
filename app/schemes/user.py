from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.v1 import validator


class CreateUser(BaseModel):
    email: str = Field(description="Почта пользователя", max_length=255, min_length=6)
    password: str = Field(description="Пароль пользователя", max_length=255, min_length=8)
    first_name: str = Field(description="Имя пользователя", max_length=255)
    last_name: str = Field(description="Фамилия пользователя", max_length=255)

    @validator('email')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы, цифры, _ и -')
        return v


class ResponseUser(BaseModel):
    id: int = Field(description="Id пользователя")
    email: str = Field(description="Почта пользователя")
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    is_active: bool = Field(description="Статус пользователя")
    role: str = Field(description="Роль пользователя")
    created_at: datetime = Field(description="Дата создания пользователя")


class UpdateUser(BaseModel):
    email: str = Field(description="Почта пользователя", max_length=255, min_length=6, default=None)
    password: str = Field(description="Пароль пользователя", max_length=255, min_length=8, default=None)
    first_name: str = Field(description="Имя пользователя", max_length=255, default=None)
    last_name: str = Field(description="Фамилия пользователя", max_length=255, default=None)
