from fastapi import FastAPI
from app.tasks.controller import router as tasks_router
from app.users.controller import router as user_router
from app.boards.controller import router as boards_router
from app.columns.controller import router as columns_router

def register_routers(app: FastAPI):
    app.include_router(tasks_router)
    app.include_router(user_router)
    app.include_router(boards_router)
    app.include_router(columns_router)