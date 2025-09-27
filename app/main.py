from fastapi import FastAPI
from .database.core import engine, Base, wait_for_db
from .api import register_routers
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    os.getenv("ALLOWED_ORIGIN")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

register_routers(app)