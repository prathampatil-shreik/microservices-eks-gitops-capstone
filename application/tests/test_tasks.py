"""
Tests for task CRUD endpoints.
Covers: create, list, get, update, delete, stats, history.
"""
import pytest


TASK_PAYLOAD = {
    "title": "Test Task",
    "description": "A test description",
    "task_type": "DATA_PROCESSING",
    "priority": "MEDIUM",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_task(client, overrides=None):
    payload = {**TASK_PAYLOAD, **(overrides or {})}
    res = client.post("/api/v1/tasks", json=payload)
    assert res.status_code == 201
    return res.json()


# ── Create ─────────────────────────────────────────────────────────────────────

def test_create_task_returns_201(client):
    res = client.post("/api/v1/tasks", json=TASK_PAYLOAD)
    assert res.status_code == 201


def test_create_task_fields(client):
    task = create_task(client)
    assert task["title"] == TASK_PAYLOAD["title"]
    assert task["status"] == "PENDING"
    assert task["priority"] == "MEDIUM"
    assert task["task_type"] == "DATA_PROCESSING"
    assert "id" in task
    assert "created_at" in task


def test_create_task_missing_title_returns_422(client):
    res = client.post("/api/v1/tasks", json={"description": "no title"})
    assert res.status_code == 422


def test_create_task_empty_title_returns_422(client):
    res = client.post("/api/v1/tasks", json={"title": ""})
    assert res.status_code == 422


def test_create_task_all_types(client):
    for task_type in ["DATA_PROCESSING", "REPORT_GENERATION", "EMAIL_NOTIFICATION", "FILE_EXPORT", "CLEANUP"]:
        task = create_task(client, {"title": f"Task {task_type}", "task_type": task_type})
        assert task["task_type"] == task_type


def test_create_task_all_priorities(client):
    for priority in ["LOW", "MEDIUM", "HIGH"]:
        task = create_task(client, {"title": f"Task {priority}", "priority": priority})
        assert task["priority"] == priority


# ── List ───────────────────────────────────────────────────────────────────────

def test_list_tasks_returns_paginated(client):
    create_task(client)
    res = client.get("/api/v1/tasks")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data


def test_list_tasks_filter_by_status(client):
    create_task(client, {"title": "Pending Task"})
    res = client.get("/api/v1/tasks?status=PENDING")
    assert res.status_code == 200
    items = res.json()["items"]
    assert all(t["status"] == "PENDING" for t in items)


def test_list_tasks_search(client):
    create_task(client, {"title": "UniqueSearchTitle123"})
    res = client.get("/api/v1/tasks?search=UniqueSearchTitle123")
    assert res.status_code == 200
    items = res.json()["items"]
    assert any("UniqueSearchTitle123" in t["title"] for t in items)


def test_list_tasks_pagination(client):
    for i in range(5):
        create_task(client, {"title": f"Paginated Task {i}"})
    res = client.get("/api/v1/tasks?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) <= 2


# ── Get single task ────────────────────────────────────────────────────────────

def test_get_task_by_id(client):
    task = create_task(client)
    res = client.get(f"/api/v1/tasks/{task['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == task["id"]


def test_get_task_includes_history(client):
    task = create_task(client)
    res = client.get(f"/api/v1/tasks/{task['id']}")
    assert res.status_code == 200
    assert "history" in res.json()


def test_get_nonexistent_task_returns_404(client):
    res = client.get("/api/v1/tasks/999999")
    assert res.status_code == 404


# ── Update ─────────────────────────────────────────────────────────────────────

def test_update_task_title(client):
    task = create_task(client)
    res = client.put(f"/api/v1/tasks/{task['id']}", json={"title": "Updated Title"})
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Title"


def test_update_task_status(client):
    task = create_task(client)
    res = client.put(f"/api/v1/tasks/{task['id']}", json={"status": "COMPLETED"})
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"


def test_update_nonexistent_task_returns_404(client):
    res = client.put("/api/v1/tasks/999999", json={"title": "x"})
    assert res.status_code == 404


# ── Delete ─────────────────────────────────────────────────────────────────────

def test_delete_task(client):
    task = create_task(client)
    res = client.delete(f"/api/v1/tasks/{task['id']}")
    assert res.status_code == 204


def test_delete_task_then_get_returns_404(client):
    task = create_task(client)
    client.delete(f"/api/v1/tasks/{task['id']}")
    res = client.get(f"/api/v1/tasks/{task['id']}")
    assert res.status_code == 404


def test_delete_nonexistent_task_returns_404(client):
    res = client.delete("/api/v1/tasks/999999")
    assert res.status_code == 404


# ── Stats ──────────────────────────────────────────────────────────────────────

def test_stats_endpoint(client):
    res = client.get("/api/v1/stats")
    assert res.status_code == 200
    data = res.json()
    for key in ["total", "pending", "processing", "completed", "failed"]:
        assert key in data
        assert isinstance(data[key], int)


def test_stats_counts_new_task(client):
    before = client.get("/api/v1/stats").json()
    create_task(client)
    after = client.get("/api/v1/stats").json()
    assert after["total"] >= before["total"] + 1
    assert after["pending"] >= before["pending"] + 1


# ── History ────────────────────────────────────────────────────────────────────

def test_task_history_created_on_task_creation(client):
    task = create_task(client)
    res = client.get(f"/api/v1/tasks/{task['id']}/history")
    assert res.status_code == 200
    history = res.json()
    assert len(history) >= 1
    assert history[0]["current_status"] == "PENDING"


def test_task_history_records_status_change(client):
    task = create_task(client)
    client.put(f"/api/v1/tasks/{task['id']}", json={"status": "COMPLETED"})
    res = client.get(f"/api/v1/tasks/{task['id']}/history")
    statuses = [h["current_status"] for h in res.json()]
    assert "COMPLETED" in statuses


def test_task_history_nonexistent_task_returns_404(client):
    res = client.get("/api/v1/tasks/999999/history")
    assert res.status_code == 404
