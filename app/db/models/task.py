import datetime
from datetime import datetime as dt

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True)
    description = Column(Text, nullable=True)
    assignee_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    status_id = Column(
        Integer,
        ForeignKey("status.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, default=dt.now(datetime.UTC))
    updated_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    started_work_at = Column(DateTime, nullable=True)

    assignee = relationship("User", back_populates="tasks",  lazy="subquery")
    status = relationship("Status", back_populates="tasks", lazy="subquery")

    def __repr__(self):
        return (
            f"{self.id} - {self.title} - "
            f"{self.assignee} - {self.status} - {self.created_at}"
        )
