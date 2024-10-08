import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from database import Base
from config import create_data
from main import app, get_db_async_session

postgres = PostgresContainer(image="postgres:16.2", driver="asyncpg")
postgres.start()

engine = create_async_engine(postgres.get_connection_url(), poolclass=NullPool)
AsyncTestSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
async def db_session():
    yield AsyncTestSession
    postgres.stop()


@pytest.fixture(scope="session")
async def client(db_session):
    async def override_get_db():
        db: AsyncSession = db_session()
        try:
            yield db
        finally:
            await db.aclose()

    app.dependency_overrides[get_db_async_session] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def create_fixtures(db_session: AsyncSession):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_db_session = db_session()
    await create_data(async_db_session)
