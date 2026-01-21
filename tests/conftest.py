import os

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/expertlisting_test",
)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/expertlisting_test",
)

from src.main import app
from src.db.session import AsyncSessionLocal


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    sync_url = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/expertlisting_test",
    )
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", sync_url)
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture(autouse=True)
async def clear_tables():
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM properties"))
        await session.execute(text("DELETE FROM geo_buckets"))
        await session.commit()
    yield


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
