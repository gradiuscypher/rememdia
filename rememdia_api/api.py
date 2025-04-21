from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, Base, get_db
from models import TagOrm
from routers import links, notes
from services.links import get_links_from_db


scheduler = AsyncIOScheduler()


@scheduler.scheduled_job('interval', seconds=5)
async def check_reminders():
    print("Checking reminders")
    async for db in get_db():
        reminder_links = await get_links_from_db(db, reminder=True)
        for link in reminder_links:
            print(link)


@scheduler.scheduled_job('interval', seconds=2)
async def check_reading():
    print("Checking reading")
    async for db in get_db():
        reading_links = await get_links_from_db(db, reading=True)
        for link in reading_links:
            print(link)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Start scheduler when app starts
    scheduler.start()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shut down scheduler when app stops
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(links.link_router)
app.include_router(notes.note_router)


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


@app.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)):
    """
    Get any tags that start with the tag_slice, used for autocomplete
    """
    query = select(TagOrm)
    result = await db.execute(query)
    tags = result.scalars().all()
    return [tag.name for tag in tags]
