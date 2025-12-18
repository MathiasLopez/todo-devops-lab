import pytest


@pytest.mark.asyncio
async def test_full_flow(client):
    # Create priority
    r = await client.post(
        "/priorities/",
        json={"title": "High"}
    )
    assert r.status_code == 201
    priority = r.json()

    # Create board
    r = await client.post(
        "/boards/",
        json={"title": "Test E2E", "description": "Board test created in E2E"}
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
            "priority_id": priority["id"],
            "tags": [tag_backend["id"]],
        },
    )
    assert r.status_code == 201
    task = r.json()

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
