from fastapi import FastAPI
from app.tasks.controller import router as tasks_router

def register_routers(app: FastAPI):
    app.include_router(tasks_router)