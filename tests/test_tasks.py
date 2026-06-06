# --- task-crud ---


def test_create_task_success(client):
    response = client.post(
        "/tasks",
        json={"title": "Write specs", "priority": "high"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write specs"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={"priority": "high"})
    assert response.status_code == 422


def test_create_task_missing_priority(client):
    response = client.post("/tasks", json={"title": "No priority"})
    assert response.status_code == 422


def test_create_task_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={"title": "Bad priority", "priority": "urgent"},
    )
    assert response.status_code == 422


def test_create_task_invalid_status(client):
    response = client.post(
        "/tasks",
        json={"title": "Bad status", "priority": "high", "status": "invalid_status"},
    )
    assert response.status_code == 422


def test_get_task_success(client, sample_task):
    task_id = sample_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Sample task"
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert "created_at" in data


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_success(client, sample_task):
    task_id = sample_task["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "status": "in_progress",
            "priority": "high",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"


def test_update_task_status_and_priority_only(client, sample_task):
    task_id = sample_task["id"]
    original_title = sample_task["title"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "done", "priority": "low"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["priority"] == "low"
    assert data["title"] == original_title


def test_update_task_invalid_status(client, sample_task):
    task_id = sample_task["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "invalid_status"},
    )
    assert response.status_code == 422


def test_update_task_invalid_priority(client, sample_task):
    task_id = sample_task["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"priority": "urgent"},
    )
    assert response.status_code == 422


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_task_success(client, sample_task):
    task_id = sample_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
