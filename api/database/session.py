from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from api.config import settings
from sqlalchemy.orm import sessionmaker

async_engine=create_async_engine(url=settings.url, echo=True)

async_session= sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def create_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session