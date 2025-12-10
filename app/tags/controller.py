from fastapi import APIRouter, status, Depends
from uuid import UUID
from ..auth.models import AuthContext
from ..database.core.database import DbSession
from . import models
from . import service
from app.auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)

@router.put("/{id}", response_model=models.TagResponse)
def update_tag(db: DbSession, id: UUID, data: models.TagUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_tag(db, id, data, auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_tag(db, id, auth_context.user_id)