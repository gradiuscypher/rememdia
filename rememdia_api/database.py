from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase

# Create engine
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
