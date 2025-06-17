# todo-devops-lab 🚧

End-to-end DevOps learning project using a simple TODO app built with FastAPI. Covers CI/CD, containerization, deployment and infrastructure automation.  

## How to Run the Project Locally
 Follow these steps to set up and run the application from scratch.
  
### 1. Create a PostgreSQL container using Docker
#### 1.1. Pull the official PostgreSQL image

```bash
docker pull postgres:latest
```
#### 1.2. Start a new container with the pulled image
```bash
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
```bash
DATABASE_URL=postgresql://admin:admin123@localhost:5432/tododb
```
### 3. Set up a virtual environment
#### 3.1. Create the virtual environment
```bash
python3 -m venv venv
```
#### 3.2. Activate the virtual environment
- macOS/Linux
```bash
source venv/bin/activate
```
### 4. Install dependencies
```bash
pip install -r requirements.txt
```
### 5. Run the application
```bash
uvicorn main:app
```
### 6. Test the API
#### 6.1. Open the browser and go to:
```bash
http://localhost:8000/docs
```

