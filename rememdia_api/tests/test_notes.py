import pytest
from datetime import datetime, timezone

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from api import app

client = TestClient(app)


@pytest.mark.asyncio(loop_scope="function")
async def test_save_note() -> None:
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


@pytest.mark.asyncio(loop_scope="function")
async def test_update_note() -> None:
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            # create the note we're updating
            r = await client.post(
                "/note",
                json={
                    "note": "test note",
                    "reminder": False,
                    "reading": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "tags": ["test1", "test2", "test3"],
                },
            )
            assert r.status_code == 200

            # update the note
            r = await client.patch(
                "/note/1",
                json={
                    "note": "Updated test note",
                    "reminder": True,
                    "reading": True,
                    "tags": ["test1", "test3", "test4"],
                },
            )
            assert r.status_code == 200

            # fetch the link and validate the changes
            r = await client.get("/note")
            assert r.status_code == 200
            assert r.json()[0]["note"] == "Updated test note"
            assert r.json()[0]["reminder"]
            assert r.json()[0]["reading"]
            assert r.json()[0]["tags"] == ["test1", "test3", "test4"]
