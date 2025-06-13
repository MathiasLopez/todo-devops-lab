from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return "todo-devops-lab is running!"