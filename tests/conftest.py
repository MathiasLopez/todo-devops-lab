import pytest_asyncio
import httpx
import os

API_BASE_URL = os.getenv("API_BASE_URL")

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(base_url=API_BASE_URL) as c:
        yield c