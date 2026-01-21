import re
from datetime import datetime, date
from typing import Optional, ClassVar

from fastapi import Query
from pydantic import BaseModel, Field, field_validator


class CreateUser(BaseModel):
    email: str = Field(description="Почта пользователя", max_length=255, min_length=6)
    password: str = Field(description="Пароль пользователя", max_length=255, min_length=8)
    first_name: str = Field(description="Имя пользователя", max_length=255, min_length=1)
    last_name: str = Field(description="Фамилия пользователя", max_length=255, min_length=1)

    PASSWORD_REGEX: ClassVar[str] = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    EMAIL_REGEX: ClassVar[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


    @field_validator('email', mode='after')
    def validate_email(cls, value):
        if not re.match(cls.EMAIL_REGEX, value):
            raise ValueError('Некорректный формат почты. Почта должна содержать как минимум 1 символ . и @')

        return value

    @field_validator('password', mode='after')
    def validate_password(cls, value):
        if not re.match(cls.PASSWORD_REGEX, value):
            raise ValueError(
                'Пароль должен содержать не менее 8 символов, '
                'включая одну заглавную букву и одну цифру.'
            )

        return value


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
    first_name: str = Field(description="Имя пользователя", max_length=255, min_length=1, default=None)
    last_name: str = Field(description="Фамилия пользователя", max_length=255, min_length=1, default=None)

    PASSWORD_REGEX: ClassVar[str] = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    EMAIL_REGEX: ClassVar[
        str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    @field_validator('email', mode='after')
    def validate_email(cls, value):
        if not re.match(cls.EMAIL_REGEX, value):
            raise ValueError(
                'Некорректный формат почты. Почта должна содержать как минимум 1 символ . и @')

        return value

    @field_validator('password', mode='after')
    def validate_password(cls, value):
        if not re.match(cls.PASSWORD_REGEX, value):
            raise ValueError(
                'Пароль должен содержать не менее 8 символов, '
                'включая одну заглавную букву и одну цифру.'
            )

        return value


class UserFilter(BaseModel):
    email: Optional[str] = Query(None)
    first_name: Optional[str] = Query(None)
    last_name: Optional[str] = Query(None)
    created_at: Optional[date] = Query(None)