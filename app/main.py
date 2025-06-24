from fastapi import FastAPI
from .database.core import engine, Base, wait_for_db
from .api import register_routers
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    yield

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

register_routers(app)

# tags_metadata = [
#     {
#         "name": "Users",
#         "description": "Operations related to users: creating, obtaining, updating and deleting."
#     },
#     {
#         "name": "Auth",
#         "description": "Endpoints related to authentication: login, logout and registration."
#     }
# ]
# app = FastAPI(openapi_tags=tags_metadata)

# @app.post('/auth/register', tags=['Auth'])
# def auth_register(password: str = Body(), email: str = Body(), name: str= Body()):
#     return {name}

# @app.post('/auth/login', tags=['Auth'])
# def auth_login():
#     return "User login"

# @app.get('/auth/me', tags=['Auth'])
# def auth_me():
#     return "User details"

# @app.post('/auth/logout', tags=['Auth'])
# def auth_logout():
#     return "Logout"

# # Only an admin will be able to do it
# @app.get('/users', tags=['Users'])
# def users():
#     return "List of users"

# # Only an admin will be able to do it
# @app.get('/users/{id}', tags=['Users'])
# def get_user(id: int):
#     return "Get user"

# @app.put('/users/{id}', tags=['Users'])
# def update_user(id: int, email: str = Body(), name: str= Body()):
#     return "Update user"

# # Only an admin will be able to do it
# @app.delete('/users/{id}', tags=['Users'])
# def delete_user(id: int):
#     return "Delete user"