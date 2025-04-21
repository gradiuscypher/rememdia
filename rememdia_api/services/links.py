from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models import LinkModel, LinkOrm


async def get_links_from_db(
    db: AsyncSession,
    reminder: bool | None = None,
    reading: bool | None = None,
) -> list[LinkModel]:
    query = select(LinkOrm).options(selectinload(LinkOrm.tags))

    if reminder is not None:
        query = query.where(LinkOrm.reminder == reminder)
    if reading is not None:
        query = query.where(LinkOrm.reading == reading)

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