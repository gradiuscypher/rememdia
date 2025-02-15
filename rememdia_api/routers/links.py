from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import LinkModel, LinkUpdateModel, LinkOrm, TagOrm
from helpers import get_link_metadata

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
async def get_link(db: AsyncSession = Depends(get_db)) -> list[LinkModel] | dict:
    try:
        query = select(LinkOrm).options(selectinload(LinkOrm.tags))
        result = await db.execute(query)
        links = result.scalars().all()

        link_models = []

        for link in links:
            link_model = LinkModel(
                link_id=link.id,
                url=link.url,
                summary=link.summary,
                tags=[tag.name for tag in link.tags],
                reminder=link.reminder,
                reading=link.reading,
                created_at=link.created_at,
                meta_title=link.meta_title,
                meta_description=link.meta_description,
            )
            link_models.append(link_model)

        return link_models

    except Exception as e:
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
        query = select(LinkOrm).where(LinkOrm.id == link_id)
        result = await db.execute(query)
        link = result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        for field, value in link_update.model_dump(exclude_unset=True).items():
            setattr(link, field, value)

        await db.commit()
        await db.refresh(link)

        return {"success": "Link updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
