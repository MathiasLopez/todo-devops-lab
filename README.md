# todo-devops-lab 🚧

End-to-end DevOps learning project using a simple TODO app built with FastAPI. Covers CI/CD, containerization, deployment and infrastructure automation.  

## How to Run the Project Locally
Follow these steps to set up and run the application from scratch.
  
### 1. Create a PostgreSQL container using Docker
#### 1.1. Pull the official PostgreSQL image

```
docker pull postgres:latest
```
#### 1.2. Start a new container with the pulled image
```
docker run --name todo-devops-lab-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=tododb \
  -p 5432:5432 \
  -v todo-postgres-data:/var/lib/postgresql/data \
  -d postgres
```

### 2. Create a .env file
#### 2.1. Create a .env file in the root of the project and add the following:
```
DB_USER=admin
DB_PASS=admin123
DB_PORT=5432
DB_HOST=localhost
DB_NAME=taskdb
AUTH_URL=https://auth.localtest.me
```
### 3. Set up a virtual environment
#### 3.1. Create the virtual environment
```
python3 -m venv venv
```
#### 3.2. Activate the virtual environment
- macOS/Linux
```
source venv/bin/activate
```
### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Run migrations
From the root of the project (the folder containing the app)
```
alembic upgrade head
```

### 6. Run the application
From the root of the project:
```
uvicorn app.main:app --reload
```
### 6. Test the API
#### 6.1. Open the browser and go to:
```
http://localhost:8000/docs
```

## How to run the project in docker

### 1. Create a .env file
#### 1.1. Create a .env file in the root of the project and add the following:
```
DB_USER=admin
DB_PASS=admin123
DB_PORT=5432
DB_HOST=db
DB_NAME=taskdb
AUTH_URL=https://auth.localtest.me
```

### 2. Build the containers
```
docker compose build
```

### 3. Lift the database container
```
docker compose up -d db
```

### 4. Run migrations
```
docker compose -f docker-compose.yml run --rm api alembic upgrade head
```

### 5.  start api container
```
docker compose up -d api
```

### 6. Test the API
Open the browser and go to:
```
http://localhost:8000/docs
```

## How to run tests
This project uses pytest for testing.

### 1. Dependencies
#### 1.1. Before running the tests install the development dependecies:
```
pip install -r requirements-dev.txt
```

### 2. Environment variables
#### 2.1. The tests require the API_BASE_URL environment variable to be defined. This variable specifies the base URL where the API is running.
##### 2.1.1. If running the app locally:
###### Define the variable inside a .env file at the root of the project.
```
API_BASE_URL=http://localhost:8000
```

##### 2.1.2. If running the app locally:
###### Export the variable manually in your terminal before running the tests:
```
export API_BASE_URL=http://localhost:8000
export JWT_SECRET=123e4567-e89b-12d3-a456-426614174000
export JWT_ALGORITHM=HS256
```

### 3. Run tests:
```bash
pytest
```

## CORS Configuration

The project uses environment variables to define allowed origins.  
You must configure the `.env` file in the project root with the `ALLOWED_ORIGIN` variable.

### ENV file example `.env`

```
ALLOWED_ORIGIN=https://kanban.mathiaslopez.tech
```