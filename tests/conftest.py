import os
import asyncio

import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    sync_url = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/expertlisting_test",
    )
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", sync_url)
    command.upgrade(cfg, "head")


@pytest.fixture(autouse=True)
async def clear_tables():
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM properties"))
        await session.execute(text("DELETE FROM geo_buckets"))
        await session.commit()
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
