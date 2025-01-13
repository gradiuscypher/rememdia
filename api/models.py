from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer
from pydantic import BaseModel, ConfigDict


class Base(DeclarativeBase):
    pass


class NoteOrm(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[str] = mapped_column(String, nullable=False)


class NoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    note: str
    tags: list[str]
