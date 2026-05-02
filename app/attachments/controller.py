# attachments/controller.py
from fastapi import APIRouter, Depends, UploadFile, status
from uuid import UUID
from typing import List

from ..auth.models import AuthContext
from ..auth.dependencies import get_auth_context
from ..database.core.database import DbSession
from . import models, service

router = APIRouter(tags=["Attachments"])


@router.post(
    "/tasks/{task_id}/attachments",
    response_model=models.AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    task_id: UUID,
    file: UploadFile,
    db: DbSession,
    auth_context: AuthContext = Depends(get_auth_context),
):
    content = await file.read()
    return service.upload_attachment(
        db,
        task_id,
        filename=file.filename,
        content_type=file.content_type,
        content=content,
        user_id=auth_context.user_id,
    )


@router.get("/tasks/{task_id}/attachments", response_model=List[models.AttachmentResponse])
def list_attachments(
    task_id: UUID,
    db: DbSession,
    auth_context: AuthContext = Depends(get_auth_context),
):
    return service.list_attachments(db, task_id, auth_context.user_id)


@router.get("/attachments/{id}/download", response_model=models.DownloadResponse)
def get_download_url(
    id: UUID,
    db: DbSession,
    auth_context: AuthContext = Depends(get_auth_context),
):
    return service.get_download_url(db, id, auth_context.user_id)


@router.delete("/attachments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    id: UUID,
    db: DbSession,
    auth_context: AuthContext = Depends(get_auth_context),
):
    service.delete_attachment(db, id, auth_context.user_id)
