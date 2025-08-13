import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_get_books():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as ac:
        resp = await ac.get("/books")
        assert resp.status_code == 200
        print(resp.json())

@pytest.mark.asyncio
async def test_post_books():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as ac:
        resp = await ac.post("/books", json={
            "title": "hhh",
            "author": "mmm"
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data == {"ok": True}