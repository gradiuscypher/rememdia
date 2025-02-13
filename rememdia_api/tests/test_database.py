import pytest
from datetime import datetime, timezone

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from api import app

client = TestClient(app)


@pytest.mark.asyncio(loop_scope="session")
async def test_notes() -> None:
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            created_at = datetime.now(timezone.utc).isoformat()
            # validate that you can save a note
            r = await client.post(
                "/note",
                json={
                    "note": "test note",
                    "reminder": False,
                    "reading": False,
                    "created_at": created_at,
                    "tags": ["test1", "test2"],
                },
            )
            assert r.status_code == 200

            # validate the note was saved
            r = await client.get("/note")
            assert r.status_code == 200
            assert r.json()[0]["note"] == "test note"


@pytest.mark.asyncio(loop_scope="session")
async def test_links() -> None:
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
