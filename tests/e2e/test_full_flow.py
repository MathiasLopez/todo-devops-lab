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
            "priority_id": high_priority["id"],
            "tags": [tag_backend["id"]],
        },
    )
    assert r.status_code == 201
    task = r.json()
    assert task["priority"]["color"] == high_priority["color"]

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
