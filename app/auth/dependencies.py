from fastapi import Depends, HTTPException
from app.auth.token import get_token, validate_token
from . import models

async def get_auth_context(token: str = Depends(get_token)) -> dict:
    payload = validate_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    return models.AuthContext(user_id=user_id, token=token)