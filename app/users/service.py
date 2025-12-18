# users/service.py
from ..auth.models import AuthContext
from .models import User
from ..utils.http_client import get_http_client
import os

AUTH_URL = os.getenv("AUTH_URL")

async def get_users(auth_context: AuthContext) -> list[User]:
    """
    Call the /api/users endpoint of the authentication service (SSO) and return a list of users.
    """
    async with get_http_client() as client:
        response = await client.get(
            f"{AUTH_URL}/api/users",
            headers={"Authorization": f"Bearer {auth_context.token}"}
        )
        response.raise_for_status()
        data = response.json()
        return [User(**user) for user in data]
     