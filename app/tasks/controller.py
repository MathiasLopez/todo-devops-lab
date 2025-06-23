from fastapi import APIRouter, status
from typing import List
from uuid import UUID
from ..database.core import DbSession
from . import models
from . import service

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=models.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(db: DbSession, task: models.TaskCreate):
    return service.create_task(db, task)

@router.get("/{id}", response_model=models.TaskResponse)
def get_task(db: DbSession, id: UUID):
    return service.get_task_by_id(db, id)

@router.get("/", response_model=List[models.TaskResponse])
def get_tasks(db: DbSession):
    return service.get_tasks(db)

@router.put("/{id}", response_model=models.TaskResponse)
def update_task(db: DbSession, id: UUID, task_to_update: models.TaskUpdate):
    return service.update_task(db, id, task_to_update)

@router.put("/{id}/complete", response_model=models.TaskResponse)
def complete_task(db: DbSession, id: UUID):
    return service.complete_task(db, id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(db: DbSession, id: UUID):
    service.delete_task(db, id)