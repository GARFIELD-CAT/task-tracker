from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    description = Column(Text, nullable=True)
    permissions = Column(Text)

    def __repr__(self):
        return (
            f"{self.id} - {self.name} - {self.permissions}"
        )
