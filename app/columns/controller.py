from fastapi import APIRouter, status, Depends
from uuid import UUID
from ..auth.models import AuthContext
from ..database.core.database import DbSession
from . import models
from . import service
from ..tasks.models import TaskCreate, TaskResponse
from ..tasks import service as task_services
from app.auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/columns",
    tags=["Columns"]
)

@router.put("/{id}", response_model=models.ColumnResponse)
def update_column(db: DbSession, id: UUID, data: models.ColumnUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update(db, id, auth_context.user_id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete(db, id, auth_context.user_id)

# Tasks
@router.post("/{column_id}/tasks", response_model=TaskResponse)
def create_task(db: DbSession, column_id: UUID, data: TaskCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return task_services.create_task(db, data, auth_context.user_id, column_id)
