import datetime
from datetime import datetime as dt

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    password = Column(String(60))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.now(datetime.UTC))
    role = Column(
        Integer,
        ForeignKey("role.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self):
        return (
            f"{self.id} - {self.email} - "
            f"{self.first_name} - {self.last_name} - "
            f"{self.is_active} - {self.created_at}"
        )
