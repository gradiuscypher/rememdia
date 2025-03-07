from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import TagOrm, NoteModel, NoteOrm, NoteUpdateModel

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
async def get_notes(
    reminder: bool | None = None,
    reading: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[NoteModel] | dict:
    try:
        query = select(NoteOrm).options(selectinload(NoteOrm.tags))
        if reminder is not None:
            query = query.where(NoteOrm.reminder == reminder)
        if reading is not None:
            query = query.where(NoteOrm.reading == reading)

        result = await db.execute(query)
        notes = result.scalars().all()

        note_models = []

        for note in notes:
            note_model = NoteModel(
                note_id=note.id,
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


@note_router.patch("/note/{note_id}")
async def update_note(
    note_id: int, note_update: NoteUpdateModel, db: AsyncSession = Depends(get_db)
) -> dict:
    try:
        query = (
            select(NoteOrm)
            .where(NoteOrm.id == note_id)
            .options(selectinload(NoteOrm.tags))
        )
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(status_code=404, detail="Link not found")

        if note_update.note:
            note.note = note_update.note
        if note_update.reminder is not None:
            note.reminder = note_update.reminder
        if note_update.reading is not None:
            note.reading = note_update.reading

        if note_update.tags:
            # remove the previous tags
            for tag in note.tags:
                note.tags.clear()

            # add the updated tags
            for tag in note_update.tags:
                result = await db.execute(select(TagOrm).where(TagOrm.name == tag))
                tag_instance = result.scalar_one_or_none()

                if tag_instance is None:
                    tag_instance = TagOrm(name=tag)
                    db.add(tag_instance)

                note.tags.append(tag_instance)

        await db.commit()
        await db.refresh(note)

        return {"success": "Note updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@note_router.delete("/note/{note_id}")
async def delete_link(note_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    query = select(NoteOrm).where(NoteOrm.id == note_id)
    result = await db.execute(query)
    link = result.scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
        return {"success": "Note deleted"}

    else:
        raise HTTPException(status_code=404, detail="Note not found")
