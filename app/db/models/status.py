from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)

    def __repr__(self):
        return (
            f"{self.id} - {self.name}"
        )
