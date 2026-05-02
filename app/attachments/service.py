# attachments/service.py
import logging
import os
import re
from io import BytesIO
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..entities.attachment import Attachment
from ..entities.task import Task
from ..boards.access import check_user_permissions
from ..boards.permissions import PERM_BOARD_VIEW, PERM_TASK_UPDATE
from . import storage

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip",
    "application/x-zip-compressed",
    "text/plain",
}

PRESIGNED_URL_EXPIRY = 900  # seconds


def _max_upload_bytes() -> int:
    return int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024


def _sanitize_filename(name: str) -> str:
    # Remove path separators and replace whitespace with underscores
    name = os.path.basename(name)
    return re.sub(r"[^\w.\-]", "_", name)


def _get_task_or_404(db: Session, task_id: UUID) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _get_attachment_or_404(db: Session, attachment_id: UUID) -> Attachment:
    attachment = db.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


def upload_attachment(
    db: Session,
    task_id: UUID,
    filename: str,
    content_type: str,
    content: bytes,
    user_id: UUID,
) -> Attachment:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {content_type}")

    max_bytes = _max_upload_bytes()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_bytes // 1024 // 1024} MB",
        )

    task = _get_task_or_404(db, task_id)
    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_TASK_UPDATE)

    attachment_id = uuid4()
    safe_name = _sanitize_filename(filename)
    key = f"{task_id}/{attachment_id}_{safe_name}"

    storage.upload_file(BytesIO(content), key, content_type)

    try:
        attachment = Attachment(
            id=attachment_id,
            task_id=task_id,
            filename=filename,
            minio_key=key,
            content_type=content_type,
            file_size=len(content),
            created_by=user_id,
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment
    except Exception:
        try:
            storage.delete_file(key)
        except Exception:
            logger.exception("Compensation failed: orphan file in MinIO key=%s", key)
        raise


def list_attachments(db: Session, task_id: UUID, user_id: UUID) -> list[Attachment]:
    task = _get_task_or_404(db, task_id)
    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_BOARD_VIEW)

    return (
        db.query(Attachment)
        .filter(Attachment.task_id == task_id)
        .order_by(Attachment.created_at)
        .all()
    )


def get_download_url(db: Session, attachment_id: UUID, user_id: UUID) -> dict:
    attachment = _get_attachment_or_404(db, attachment_id)
    check_user_permissions(
        db, attachment.task.column.board_id, user_id, required_permission=PERM_BOARD_VIEW
    )

    url = storage.generate_presigned_url(attachment.minio_key, attachment.filename, PRESIGNED_URL_EXPIRY)
    return {"url": url, "expires_in": PRESIGNED_URL_EXPIRY}


def delete_attachment(db: Session, attachment_id: UUID, user_id: UUID) -> None:
    attachment = _get_attachment_or_404(db, attachment_id)
    check_user_permissions(
        db, attachment.task.column.board_id, user_id, required_permission=PERM_TASK_UPDATE
    )

    minio_key = attachment.minio_key
    db.delete(attachment)
    db.commit()
    try:
        storage.delete_file(minio_key)
    except Exception:
        logger.exception("Orphan MinIO file after attachment delete: key=%s", minio_key)
