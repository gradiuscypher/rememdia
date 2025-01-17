import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_db, engine, Base
from models import NoteModel, NoteOrm, TagOrm


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


# ref: https://github.com/tiangolo/fastapi/discussions/6678
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post("/save_note")
async def save_note(note_obj: NoteModel, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        new_note = NoteOrm(note=note_obj.note)
        db.add(new_note)

        for tag in note_obj.tags:
            result = await db.execute(select(TagOrm).where(TagOrm.name == tag))
            tag_instance = result.scalar_one_or_none()

            if tag_instance is None:
                tag_instance = TagOrm(name=tag)
                db.add(tag_instance)

            new_note.tags.append(tag_instance)

        await db.commit()
        return {"success": "Note saved"}

    except Exception as e:
        return {"error": str(e)}


@app.get("/get_notes")
async def get_notes(db: AsyncSession = Depends(get_db)) -> list[NoteModel] | dict:
    try:
        query = select(NoteOrm).options(selectinload(NoteOrm.tags))
        result = await db.execute(query)
        notes = result.scalars().all()

        note_models = []

        for note in notes:
            note_model = NoteModel(
                note=note.note,
                tags=[tag.name for tag in note.tags],
            )
            note_models.append(note_model)

        return note_models

    except Exception as e:
        return {"error": str(e)}


@app.post("/save_link")
async def save_link(link: str, tags: list[str]) -> dict:
    return {"link": link}
