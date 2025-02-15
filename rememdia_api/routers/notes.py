from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import TagOrm, NoteModel, NoteOrm

note_router = APIRouter()


@note_router.post("/note")
async def save_note(note_obj: NoteModel, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        new_note = NoteOrm(
            note=note_obj.note,
            reminder=note_obj.reminder,
            reading=note_obj.reading,
            created_at=datetime.now(timezone.utc),
        )
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
        raise HTTPException(status_code=500, detail=str(e))


@note_router.get("/note")
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
                reminder=note.reminder,
                reading=note.reading,
                created_at=note.created_at,
            )
            note_models.append(note_model)

        return note_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
