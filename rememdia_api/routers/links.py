from datetime import datetime, timezone
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import LinkModel, LinkUpdateModel, LinkOrm, TagOrm
from helpers import get_link_metadata
from services.links import get_links_from_db

link_router = APIRouter()


@link_router.post("/link")
async def save_link(link_obj: LinkModel, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        meta_title, meta_description = await get_link_metadata(link_obj.url)
        new_link = LinkOrm(
            url=link_obj.url,
            summary=link_obj.summary,
            reminder=link_obj.reminder,
            reading=link_obj.reading,
            created_at=datetime.now(timezone.utc),
            meta_title=meta_title,
            meta_description=meta_description,
        )
        db.add(new_link)

        for tag in link_obj.tags:
            result = await db.execute(select(TagOrm).where(TagOrm.name == tag))
            tag_instance = result.scalar_one_or_none()

            if tag_instance is None:
                tag_instance = TagOrm(name=tag)
                db.add(tag_instance)

            new_link.tags.append(tag_instance)

        await db.commit()
        return {"success": "Link saved"}

    except Exception as e:
        return {"error": str(e)}


@link_router.get("/link")
async def get_links(
    reminder: bool | None = None,
    reading: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[LinkModel] | dict:
    try:
        return await get_links_from_db(db, reminder, reading)
    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}


@link_router.delete("/link/{link_id}")
async def delete_link(link_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    query = select(LinkOrm).where(LinkOrm.id == link_id)
    result = await db.execute(query)
    link = result.scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
        return {"success": "Link deleted"}

    else:
        raise HTTPException(status_code=404, detail="Link not found")


@link_router.patch("/link/{link_id}")
async def update_link(
    link_id: int, link_update: LinkUpdateModel, db: AsyncSession = Depends(get_db)
) -> dict:
    try:
        query = (
            select(LinkOrm)
            .where(LinkOrm.id == link_id)
            .options(selectinload(LinkOrm.tags))
        )
        result = await db.execute(query)
        link = result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        if link_update.url:
            link.url = link_update.url
        if link_update.summary:
            link.summary = link_update.summary
        if link_update.meta_title:
            link.meta_title = link_update.meta_title
        if link_update.meta_description:
            link.meta_description = link_update.meta_description
        if link_update.reminder is not None:
            link.reminder = link_update.reminder
        if link_update.reading is not None:
            link.reading = link_update.reading

        if link_update.tags:
            # remove the previous tags
            for tag in link.tags:
                link.tags.clear()

            # add the updated tags
            for tag in link_update.tags:
                result = await db.execute(select(TagOrm).where(TagOrm.name == tag))
                tag_instance = result.scalar_one_or_none()

                if tag_instance is None:
                    tag_instance = TagOrm(name=tag)
                    db.add(tag_instance)

                link.tags.append(tag_instance)

        await db.commit()
        await db.refresh(link)

        return {"success": "Link updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
