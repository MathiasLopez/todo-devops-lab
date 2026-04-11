import pytest


@pytest.mark.asyncio
async def test_full_flow(client):
    # Get system priorities (seeded)
    r = await client.get("/priorities/")
    assert r.status_code == 200
    priorities = r.json()
    assert len(priorities) >= 3
    high_priority = next((p for p in priorities if p["title"] == "High"), None)
    assert high_priority is not None
    assert high_priority["color"].startswith("#")

    # Create custom priority
    r = await client.post(
        "/priorities/",
        json={"title": "Custom Blue", "color": "#3B82F6"}
    )
    assert r.status_code == 201
    custom_priority = r.json()
    assert custom_priority["color"] == "#3B82F6"

    # Create board
    r = await client.post(
        "/boards/",
        json={
            "title": "Test E2E",
            "description": "Board test created in E2E",
            "members": [
                {
                    "user_id": "be3841af-eb3e-4424-b480-2787381a0b3e",
                    "role_id": "00000000-0000-0000-0000-000000000001",
                }
            ],
        }
    )
    assert r.status_code == 201
    board = r.json()
    
    # Create tag
    r = await client.post(
        f"/boards/{board['id']}/tags",
        json={"title": "backend"},
    )
    assert r.status_code == 201
    tag_backend = r.json()

    # Create column
    r = await client.post(
        f"/boards/{board['id']}/columns",
        json={ "title": "To Do", "description": "To Do column" }
    )
    assert r.status_code == 201
    column_todo = r.json()

    # Create task
    r = await client.post(
        f"/columns/{column_todo['id']}/tasks",
        json={
            "title": "Task E2E",
            "description": "Task created in full flow",
            "priority_id": high_priority["id"],
            "tags": [tag_backend["id"]],
        },
    )
    assert r.status_code == 201
    task = r.json()
    assert task["priority"]["color"] == high_priority["color"]

    # Create another task with the same title (duplicates should be allowed)
    r = await client.post(
        f"/columns/{column_todo['id']}/tasks",
        json={
            "title": "Task E2E",  # duplicate title
            "description": "Second task with same title",
            "priority_id": high_priority["id"],
            "tags": [tag_backend["id"]],
        },
    )
    assert r.status_code == 201

    # Update task
    r = await client.put(
        f"/tasks/{task['id']}",
        json={"description": "Updated description"},
    )
    assert r.status_code == 200
    assert r.json()["description"] == "Updated description"

    # Delete task
    r = await client.delete(f"/tasks/{task['id']}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_subtasks(client):
    # Setup: priorities, board, column, parent task
    r = await client.get("/priorities/")
    high_priority = next(p for p in r.json() if p["title"] == "High")

    r = await client.post(
        "/boards/",
        json={
            "title": "Subtask Board",
            "description": "Board for subtask tests",
            "members": [{"user_id": "be3841af-eb3e-4424-b480-2787381a0b3e", "role_id": "00000000-0000-0000-0000-000000000001"}],
        },
    )
    board = r.json()

    r = await client.post(f"/boards/{board['id']}/columns", json={"title": "Backlog"})
    column = r.json()

    r = await client.post(
        f"/columns/{column['id']}/tasks",
        json={"title": "Parent Task", "priority_id": high_priority["id"]},
    )
    assert r.status_code == 201
    parent = r.json()

    # Create subtask
    r = await client.post(
        f"/columns/{column['id']}/tasks",
        json={"title": "Child Task", "priority_id": high_priority["id"], "parent_id": parent["id"]},
    )
    assert r.status_code == 201
    child = r.json()
    assert child["parent_id"] == parent["id"]

    # GET /tasks/{id} — parent includes subtasks[]
    r = await client.get(f"/tasks/{parent['id']}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["subtasks"]) == 1
    assert data["subtasks"][0]["id"] == child["id"]
    assert data["parent"] is None

    # GET /tasks/{id} — child includes parent info, empty subtasks
    r = await client.get(f"/tasks/{child['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["parent"]["id"] == parent["id"]
    assert data["subtasks"] == []

    # Column list shows both tasks (flat view: roots and subtasks)
    r = await client.get(f"/boards/{board['id']}/columns")
    assert r.status_code == 200
    col_tasks = next(c for c in r.json() if c["id"] == column["id"])["tasks"]
    task_ids = [t["id"] for t in col_tasks]
    assert parent["id"] in task_ids
    assert child["id"] in task_ids

    # Reject subtask of subtask (max 1 level)
    r = await client.post(
        f"/columns/{column['id']}/tasks",
        json={"title": "Grandchild", "priority_id": high_priority["id"], "parent_id": child["id"]},
    )
    assert r.status_code == 400

    # Reject parent_id pointing to a non-existent task
    r = await client.post(
        f"/columns/{column['id']}/tasks",
        json={"title": "Orphan", "priority_id": high_priority["id"], "parent_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code == 404

    # Search: onlyRoot=true excludes subtasks
    r = await client.get(f"/tasks/search?boardId={board['id']}&onlyRoot=true")
    assert r.status_code == 200
    ids = [t["id"] for t in r.json()]
    assert parent["id"] in ids
    assert child["id"] not in ids

    # Search: text query returns matching tasks
    r = await client.get(f"/tasks/search?boardId={board['id']}&q=Child")
    assert r.status_code == 200
    assert any(t["id"] == child["id"] for t in r.json())

    # Update: promote subtask to root by clearing parent_id
    r = await client.put(f"/tasks/{child['id']}", json={"parent_id": None})
    assert r.status_code == 200
    assert r.json()["parent_id"] is None

    # Verify parent no longer has subtasks
    r = await client.get(f"/tasks/{parent['id']}")
    assert r.json()["subtasks"] == []
