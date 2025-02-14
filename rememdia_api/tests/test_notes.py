import pytest
from datetime import datetime, timezone

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from api import app

client = TestClient(app)


@pytest.mark.asyncio(loop_scope="session")
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
