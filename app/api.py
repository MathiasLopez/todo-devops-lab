from fastapi import FastAPI
from app.tasks.controller import router as tasks_router
from app.users.controller import router as user_router

def register_routers(app: FastAPI):
    app.include_router(tasks_router)
    app.include_router(user_router)