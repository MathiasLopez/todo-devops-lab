import pytest_asyncio
import httpx
import os, jwt

API_BASE_URL = os.getenv("API_BASE_URL")
TEST_TOKEN = jwt.encode({"sub": "be3841af-eb3e-4424-b480-2787381a0b3e"}, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(base_url=API_BASE_URL, headers={"Authorization": f"Bearer {TEST_TOKEN}"}, verify=False) as c:
        yield c