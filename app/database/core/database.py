import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import time

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]

def wait_for_db(max_retries=10, delay=2):
    for _ in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return
        except OperationalError:
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after several attempts.")
