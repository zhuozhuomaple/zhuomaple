from datetime import datetime

from tests.conftest import add_task


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


# --- task-list ---


def test_list_tasks_default_pagination(client):
    for i in range(25):
        client.post(
            "/tasks",
            json={"title": f"Task {i}", "priority": "medium"},
        )

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 20
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_list_tasks_custom_pagination(client):
    for i in range(25):
        client.post(
            "/tasks",
            json={"title": f"Task {i}", "priority": "medium"},
        )

    response = client.get("/tasks?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["page"] == 2


def test_list_tasks_invalid_page(client):
    response = client.get("/tasks?page=0")
    assert response.status_code == 422


def test_list_tasks_filter_by_status(client):
    client.post(
        "/tasks",
        json={"title": "Pending task", "priority": "medium", "status": "pending"},
    )
    client.post(
        "/tasks",
        json={"title": "Done task", "priority": "medium", "status": "done"},
    )

    response = client.get("/tasks?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "pending" for item in data["items"])
    assert data["total"] == 1


def test_list_tasks_filter_empty_result(client):
    client.post(
        "/tasks",
        json={"title": "Done only", "priority": "medium", "status": "done"},
    )

    response = client.get("/tasks?status=in_progress")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_tasks_filter_by_priority(client):
    client.post(
        "/tasks",
        json={"title": "High priority", "status": "pending", "priority": "high"},
    )
    client.post(
        "/tasks",
        json={"title": "Low priority", "status": "pending", "priority": "low"},
    )

    response = client.get("/tasks?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert all(item["priority"] == "high" for item in data["items"])
    assert data["total"] == 1


def test_list_tasks_filter_priority_empty_result(client):
    client.post(
        "/tasks",
        json={"title": "Low only", "status": "pending", "priority": "low"},
    )

    response = client.get("/tasks?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_tasks_filter_by_start_date(client, db_session):
    add_task(
        db_session,
        title="January task",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="June task",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get("/tasks", params={"start_date": "2026-05-01"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "June task"


def test_list_tasks_filter_by_end_date(client, db_session):
    add_task(
        db_session,
        title="January task",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="June task",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get("/tasks", params={"end_date": "2026-03-31"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "January task"


def test_list_tasks_filter_by_date_range(client, db_session):
    add_task(
        db_session,
        title="January task",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="June task",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="December task",
        created_at=datetime(2026, 12, 1, 10, 0, 0),
    )

    response = client.get(
        "/tasks",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert titles == {"January task", "June task"}


def test_list_tasks_filter_date_range_empty(client, db_session):
    add_task(
        db_session,
        title="June task",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get(
        "/tasks",
        params={"start_date": "2026-12-01", "end_date": "2026-12-31"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_tasks_filter_by_status_and_priority(client):
    client.post(
        "/tasks",
        json={"title": "Pending high", "status": "pending", "priority": "high"},
    )
    client.post(
        "/tasks",
        json={"title": "Pending low", "status": "pending", "priority": "low"},
    )
    client.post(
        "/tasks",
        json={"title": "Done high", "status": "done", "priority": "high"},
    )

    response = client.get("/tasks?status=pending&priority=high")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Pending high"


def test_list_tasks_filter_by_status_and_start_date(client, db_session):
    add_task(
        db_session,
        title="Pending June",
        status="pending",
        priority="high",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="Pending January",
        status="pending",
        priority="high",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )

    response = client.get(
        "/tasks",
        params={"status": "pending", "start_date": "2026-05-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Pending June"


def test_list_tasks_filter_by_priority_and_end_date(client, db_session):
    add_task(
        db_session,
        title="High June",
        status="pending",
        priority="high",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="High January",
        status="pending",
        priority="high",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )

    response = client.get(
        "/tasks",
        params={"priority": "high", "end_date": "2026-03-31"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "High January"


def test_list_tasks_filter_combined_all(client, db_session):
    add_task(
        db_session,
        title="Match",
        status="pending",
        priority="high",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="Wrong date",
        status="pending",
        priority="high",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="Wrong priority",
        status="pending",
        priority="low",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get(
        "/tasks",
        params={
            "status": "pending",
            "priority": "high",
            "start_date": "2026-05-01",
            "end_date": "2026-12-31",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Match"


def test_list_tasks_filter_combined_empty(client):
    client.post(
        "/tasks",
        json={"title": "Pending low", "status": "pending", "priority": "low"},
    )

    response = client.get("/tasks?status=pending&priority=high")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_tasks_filter_with_pagination_and_sort(client):
    for i in range(5):
        client.post(
            "/tasks",
            json={
                "title": f"Pending high {i}",
                "status": "pending",
                "priority": "high",
            },
        )

    response = client.get(
        "/tasks",
        params={
            "status": "pending",
            "priority": "high",
            "page": 1,
            "page_size": 2,
            "sort": "asc",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["items"][0]["created_at"] <= data["items"][1]["created_at"]


def test_list_tasks_invalid_priority(client):
    response = client.get("/tasks?priority=urgent")
    assert response.status_code == 422


def test_list_tasks_sort_desc_default(client, db_session):
    add_task(
        db_session,
        title="Older",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="Newer",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get("/tasks")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["title"] == "Newer"
    assert items[1]["title"] == "Older"


def test_list_tasks_sort_asc(client, db_session):
    add_task(
        db_session,
        title="Older",
        created_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    add_task(
        db_session,
        title="Newer",
        created_at=datetime(2026, 6, 1, 10, 0, 0),
    )

    response = client.get("/tasks?sort=asc")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["title"] == "Older"
    assert items[1]["title"] == "Newer"
