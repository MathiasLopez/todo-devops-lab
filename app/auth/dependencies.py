from fastapi import Depends, HTTPException
from app.auth.token import get_token, validate_token

async def get_current_user(token: str = Depends(get_token)) -> dict:
    payload = validate_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    return {"id": user_id, "payload": payload}