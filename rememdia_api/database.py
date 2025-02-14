from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase

from settings import ENVIRONMENT, EnvironmentEnum

# Create engine
if ENVIRONMENT == EnvironmentEnum.TEST:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={})
else:
    engine = create_async_engine("sqlite+aiosqlite:///./rememdia.db", connect_args={})

# Create session
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def reset_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
