import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.fixture
async def fake_session():
    """Gives each test its own empty in-memory database.
    Creates the engine, its connection to the fake database, and the fake tables
    inside it, then yields an async session bound to that engine. check_same_thread
    False lets the connection be used from another thread, and StaticPool makes the
    test and the app share the same connection so they both see the same database.
    Everything exists for as long as the test invoking this fixture runs, and
    disappears once it's done.
    """
    url = "sqlite+aiosqlite://"
    connect_args = {"check_same_thread": False}
    async_engine = create_async_engine(
        url=url, echo=True, connect_args=connect_args, poolclass=StaticPool
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
