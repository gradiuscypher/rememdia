import pytest
import pytest_asyncio
from datetime import datetime, timezone

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from api import app
from database import reset_database

client = TestClient(app)


@pytest_asyncio.fixture(autouse=True, loop_scope="module")
async def reset_db():
    await reset_database()
    yield


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def mock_get_link_metadata():
    with patch("routers.links.get_link_metadata", new_callable=AsyncMock) as mock:
        mock.return_value = ("Mocked Title", "Mocked Description")
        yield mock


@pytest.mark.asyncio(loop_scope="function")
async def test_save_link(mock_get_link_metadata) -> None:
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            # validate that you can save a link
            r = await client.post(
                "/link",
                json={
                    "url": "https://www.google.com",
                    "summary": "Google",
                    "reminder": False,
                    "reading": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "tags": ["test1", "test2"],
                },
            )
            assert r.status_code == 200

            # validate the link was created
            r = await client.get("/link")
            assert r.status_code == 200
            assert r.json()[0]["url"] == "https://www.google.com"
            assert r.json()[0]["meta_title"] == "Mocked Title"
            mock_get_link_metadata.assert_called_once_with("https://www.google.com")


@pytest.mark.asyncio(loop_scope="function")
async def test_delete_link() -> None:
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            # validate that you can save a link
            r = await client.post(
                "/link",
                json={
                    "url": "https://www.google.com",
                    "summary": "Google",
                    "reminder": False,
                    "reading": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "tags": ["test1", "test2"],
                },
            )

            # delete the link
            r = await client.delete("/link/1")
            assert r.status_code == 200

            # try to delete the link again and get a 404
            r = await client.delete("/link/1")
            assert r.status_code == 404

            # try to get the link and get an empty list
            r = await client.get("/link")
            assert r.status_code == 200
            assert r.json() == []
