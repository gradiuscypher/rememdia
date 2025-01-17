from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from pydantic import BaseModel, ConfigDict

from database import Base


class TagOrm(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    notes: Mapped[list["NoteOrm"]] = relationship(
        "NoteOrm", secondary="note_tags", back_populates="tags"
    )


class NoteOrm(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[list["TagOrm"]] = relationship(
        "TagOrm", secondary="note_tags", back_populates="notes"
    )


class NoteTagOrm(Base):
    __tablename__ = "note_tags"
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class NoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    note: str
    tags: list[str]
