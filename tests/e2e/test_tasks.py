import pytest

@pytest.mark.asyncio
async def test_crud(client):
        task_values = {"title": "Test E2E", "description": "Test created E2E", "priority": 1}

        # Create new task
        create_response = await client.post(
            "/tasks/", 
            json=task_values
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        assert created_task["title"] == task_values["title"]
        assert not created_task["is_completed"]

        # Get all tasks
        list_response = await client.get("/tasks/")
        assert list_response.status_code == 200
        tasks = list_response.json()

        # Check that the newly created task is on the list
        ids = [task["id"] for task in tasks]
        assert created_task["id"] in ids
        
        # Mark task as completed
        completed_task_response = await client.put(f"/tasks/{created_task['id']}/complete")
        assert completed_task_response.status_code == 200
        
        # Get task
        task_response = await client.get(f"/tasks/{created_task['id']}")
        assert task_response.status_code == 200
        recovered_task = task_response.json()
        assert recovered_task["is_completed"]
        
        # Update task
        update_task_values = {"description": "Test created E2E updated"}
        update_response = await client.put(
            f"/tasks/{created_task['id']}", 
            json=update_task_values
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["description"] == update_task_values["description"]
        
        # Delete task
        delete_task_response = await client.delete(f"/tasks/{created_task['id']}")
        assert delete_task_response.status_code == 204