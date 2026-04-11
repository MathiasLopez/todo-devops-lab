# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**todo-devops-lab** is a Kanban/TODO API built with FastAPI + PostgreSQL, used as a DevOps learning project. It demonstrates CI/CD pipelines, containerization, and infrastructure automation on top of a functional task management API.

## Commands

### Local development

```bash
# Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the app (requires a running PostgreSQL and a .env file)
uvicorn app.main:app --reload

# Apply migrations
alembic upgrade head

# Create a new migration after ORM changes
alembic revision --autogenerate -m "short description"
```

### Docker

```bash
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose up -d api
# API available at http://localhost:8000/docs
```

### Tests

Tests are end-to-end and hit a real running API + database. Set these env vars (or use `.env`):

```bash
export API_BASE_URL=http://localhost:8000
export JWT_SECRET=123e4567-e89b-12d3-a456-426614174000
export JWT_ALGORITHM=HS256

pytest                    # all tests
pytest tests/e2e/test_full_flow.py   # single file
pytest -k "test_name"    # single test by name
```

### Required environment variables

```
DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
JWT_SECRET, JWT_ALGORITHM
AUTH_URL          # external auth service base URL
ALLOWED_ORIGIN    # CORS origin
```

## Architecture

### Pattern

Each domain follows **Controller → Service → Entity**:

- `controller.py` — FastAPI router with route handlers and `Depends()` injection
- `service.py` — all business logic and database operations (SQLAlchemy)
- `models.py` — Pydantic schemas for request/response
- `entities/` — SQLAlchemy ORM models (single file per entity, all extend `Base`)

### Domain modules

| Module | Responsibility |
|--------|---------------|
| `auth/` | JWT validation, `get_auth_context` dependency, permission constants |
| `boards/` | Board CRUD, member management, board-level access control |
| `columns/` | Ordered columns within a board |
| `tasks/` | Tasks within columns; supports subtasks (self-referential `parent_id`), tag associations, search |
| `tags/` | Board-scoped labels attached to tasks (many-to-many via `task_tags`) |
| `priorities/` | System priorities (High/Medium/Low) + user-defined; stored with hex color |
| `roles/` | Role definitions with a `level` field for hierarchy |
| `users/` | Proxy to external auth service; no local user table |

### Key data model relationships

- `Board` → `BoardColumn` (cascade delete) → `Task` (cascade delete)
- `Board` → `Tag` (cascade delete); `Task` ↔ `Tag` many-to-many via `task_tags`
- `Task.parent_id` self-references for subtask hierarchy (one level)
- `BoardUserPermission` links `board_id` + `user_id` + `role_id` (unique on board+user)
- All entities carry audit fields via `AuditMixin` (`created_by`, `created_at`, `modified_by`, `modified_at`)

### Auth & permissions

1. `Authorization: Bearer <token>` header on every request
2. `get_auth_context` dependency decodes JWT, extracts `user_id` from `sub`
3. Board-scoped permissions checked via `check_user_permissions(db, board_id, user_id, PERM_*)` before any mutation
4. Permission constants live in each module (e.g., `boards/permissions.py`, `auth/permissions.py`)

### Database

- SQLAlchemy 2.x with synchronous sessions
- DB connection waits via `wait_for_db()` in the FastAPI lifespan handler
- All schema changes require an Alembic migration; note forward/backward compatibility in the PR

## Git & PR conventions (from AGENTS.md)

- Branch naming: `feature/<desc>`, `fix/<desc>`, `hotfix/<desc>`, `chore/<desc>`
- Commits: conventional format `<type>: <short description>` (English), one logical change per commit
- Include schema migrations and test updates in the same commit as the code change
- PR description must include: what was done, why, how to test (exact commands), risks/rollback plan if relevant
- Run the smallest meaningful test set and state what was run; if skipping tests, explain why
