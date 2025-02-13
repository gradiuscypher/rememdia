from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Integer, ForeignKey
from pydantic import BaseModel, ConfigDict

from database import Base


class LinkModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    link_id: int | None = None
    url: str
    summary: str
    meta_title: str | None = None
    meta_description: str | None = None
    reminder: bool
    reading: bool
    tags: list[str]
    created_at: datetime


class LinkOrm(Base):
    __tablename__ = "links"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    meta_title: Mapped[str] = mapped_column(String)
    meta_description: Mapped[str] = mapped_column(String)
    reminder: Mapped[bool] = mapped_column(Boolean)
    reading: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    tags: Mapped[list["TagOrm"]] = relationship(
        "TagOrm", secondary="link_tags", back_populates="links"
    )


class LinkTagOrm(Base):
    __tablename__ = "link_tags"
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class TagOrm(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    notes: Mapped[list["NoteOrm"]] = relationship(
        "NoteOrm", secondary="note_tags", back_populates="tags"
    )
    links: Mapped[list["LinkOrm"]] = relationship(
        "LinkOrm", secondary="link_tags", back_populates="tags"
    )


class NoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    note: str
    reminder: bool
    reading: bool
    created_at: datetime
    tags: list[str]


class NoteOrm(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=False)
    reminder: Mapped[bool] = mapped_column(Boolean)
    reading: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    tags: Mapped[list["TagOrm"]] = relationship(
        "TagOrm", secondary="note_tags", back_populates="notes"
    )


class NoteTagOrm(Base):
    __tablename__ = "note_tags"
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
