from fastapi import FastAPI, Body

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations related to users: creating, obtaining, updating and deleting."
    },
    {
        "name": "Auth",
        "description": "Endpoints related to authentication: login, logout and registration."
    },
    {
        "name": "Tasks",
        "description": "Administración de tareas asignadas a los usuarios."
    }
]
app = FastAPI(openapi_tags=tags_metadata)

@app.post('/auth/register', tags=['Auth'])
def auth_register(password: str = Body(), email: str = Body(), name: str= Body()):
    return {name}

@app.post('/auth/login', tags=['Auth'])
def auth_login():
    return "User login"

@app.get('/auth/me', tags=['Auth'])
def auth_me():
    return "User details"

@app.post('/auth/logout', tags=['Auth'])
def auth_logout():
    return "Logout"

# Only an admin will be able to do it
@app.get('/users', tags=['Users'])
def users():
    return "List of users"

# Only an admin will be able to do it
@app.get('/users/{id}', tags=['Users'])
def get_user(id: int):
    return "Get user"

@app.put('/users/{id}', tags=['Users'])
def update_user(id: int, email: str = Body(), name: str= Body()):
    return "Update user"

# Only an admin will be able to do it
@app.delete('/users/{id}', tags=['Users'])
def delete_user(id: int):
    return "Delete user"


@app.get('/tasks/{id}', tags=['Tasks'])
def tasks(id: int):
    return "List of tasks for a specific user"

@app.get('/tasks/{id}', tags=['Tasks'])
def get_task(id: int):
    return "Get task"

@app.post('/tasks', tags=['Tasks'])
def add_task(title: str = Body(), description: str = Body()):
    return "Create new task"

@app.post('/tasks/{id}', tags=['Tasks'])
def update_task(id: int, title: str = Body(), description: str = Body()):
    return "Update task"

@app.delete('/tasks/{id}', tags=['Tasks'])
def delete_task(id: int):
    return "Delete task"

@app.patch('/tasks/{id}', tags=['Tasks'])
def mark_task_as_done(id: int):
    return "Mark as a task done"