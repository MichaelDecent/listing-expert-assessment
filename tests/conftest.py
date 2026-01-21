import os

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

def _to_test_db(url: str) -> str:
    if url.endswith("_test"):
        return url
    return url.rsplit("/", 1)[0] + "/" + url.rsplit("/", 1)[1] + "_test"


DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    _to_test_db(
        os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/expertlisting",
        )
    ),
)
DATABASE_URL_SYNC = os.getenv(
    "TEST_DATABASE_URL_SYNC",
    _to_test_db(
        os.getenv(
            "DATABASE_URL_SYNC",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/expertlisting",
        )
    ),
)

os.environ["DATABASE_URL"] = DATABASE_URL
os.environ["DATABASE_URL_SYNC"] = DATABASE_URL_SYNC

from src.main import app
from src.db.session import AsyncSessionLocal


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL_SYNC)
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture(autouse=True)
async def clear_tables():
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("TRUNCATE geo_bucket_aliases, properties, geo_buckets CASCADE")
        )
        await session.commit()
    yield


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
