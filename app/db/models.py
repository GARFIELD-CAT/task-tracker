from datetime import datetime as dt
from enum import StrEnum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean, event
)
from sqlalchemy.orm import relationship, DeclarativeBase


class UserRoles(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class TaskStatuses(StrEnum):
    TO_DO = "To Do" # Задача создана
    IN_PROGRESS = "In Progress" # Задача в работе
    DONE = "Done" # Задача выполнена
    CANCELLED = "Cancelled" # Задача отменена


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    password = Column(String(60))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(), default=dt.now())
    role = Column(String(60), default=UserRoles.USER.value)

    tasks = relationship("Task", back_populates="assignee",  lazy="subquery")

    def __repr__(self):
        return (
            f"{self.id} - {self.email} - "
            f"{self.first_name} - {self.last_name} - "
            f"{self.is_active} - {self.created_at}"
        )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text, nullable=True, default="")
    assignee_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
    )
    status = Column(String(20), default=TaskStatuses.TO_DO.value)
    created_at = Column(DateTime, default=dt.now())
    updated_at = Column(DateTime, nullable=True, default=dt.now())
    closed_at = Column(DateTime, nullable=True, default=None)
    started_work_at = Column(DateTime, nullable=True, default=None)

    assignee = relationship("User", back_populates="tasks",  lazy="subquery")

    def __repr__(self):
        return (
            f"{self.id} - {self.title} - "
            f"{self.assignee_id} - {self.status} - {self.created_at}"
        )


# Обработчик события для обновления поля updated_at
@event.listens_for(Task, 'before_update')
def receive_before_update(mapper, connection, target):
    now = dt.now()

    if target.status == TaskStatuses.DONE.value:
        target.closed_at = now
    elif target.status == TaskStatuses.IN_PROGRESS.value:
        target.started_work_at = now

    target.updated_at = now
