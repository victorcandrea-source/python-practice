"""
API Tests for Task Manager using TestClient
"""

import pytest


# ==========================================
# Health Check Tests
# ==========================================

def test_health_check(test_client):
    """Test health endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ==========================================
# Create Task Tests
# ==========================================

def test_create_task_success(test_client):
    """Test successful task creation returns 201"""
    payload = {
        "title": "Test Task",
        "owner": "Alice",
        "description": "A test task"
    }
    response = test_client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["owner"] == "Alice"
    assert data["description"] == "A test task"
    assert data["status"] == "todo"
    assert data["id"] == 1


def test_create_task_missing_title(test_client):
    """Test create with missing title returns 422"""
    payload = {
        "owner": "Alice",
        "description": "No title"
    }
    response = test_client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_missing_owner(test_client):
    """Test create with missing owner returns 422"""
    payload = {
        "title": "Test",
        "description": "No owner"
    }
    response = test_client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_empty_title(test_client):
    """Test create with empty title returns 422"""
    payload = {
        "title": "",
        "owner": "Alice",
    }
    response = test_client.post("/tasks", json=payload)
    assert response.status_code == 422


# ==========================================
# List Tasks Tests
# ==========================================

def test_list_tasks_empty(test_client):
    """Test list tasks when empty"""
    response = test_client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_with_data(test_client):
    """Test list tasks after creating some"""
    # Create two tasks
    test_client.post("/tasks", json={
        "title": "Task 1",
        "owner": "Alice",
        "description": "First"
    })
    test_client.post("/tasks", json={
        "title": "Task 2",
        "owner": "Bob",
        "description": "Second"
    })
    
    response = test_client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"


def test_list_tasks_filter_by_owner(test_client):
    """Test list tasks with owner filter"""
    resp1 = test_client.post("/tasks", json={
        "title": "Alice Task",
        "owner": "Alice"
    })
    resp2 = test_client.post("/tasks", json={
        "title": "Bob Task",
        "owner": "Bob"
    })
    
    response = test_client.get("/tasks?owner=Alice")
    assert response.status_code == 200
    tasks = response.json()
    # Should only have Alice's tasks
    alice_tasks = [t for t in tasks if t["owner"] == "Alice"]
    assert len(alice_tasks) >= 1
    assert alice_tasks[0]["owner"] == "Alice"


# ==========================================
# Get Task By ID Tests
# ==========================================

def test_get_task_success(test_client):
    """Test get task by ID returns 200"""
    # Create a task first
    test_client.post("/tasks", json={
        "title": "Get Me",
        "owner": "Alice",
        "description": "Find this"
    })
    
    response = test_client.get("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Get Me"
    assert data["owner"] == "Alice"


def test_get_task_not_found(test_client):
    """Test get unknown task returns 404"""
    response = test_client.get("/tasks/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==========================================
# Update Task Tests (PATCH)
# ==========================================

def test_patch_task_success(test_client):
    """Test PATCH update returns 200"""
    # Create a task
    test_client.post("/tasks", json={
        "title": "Original",
        "owner": "Alice",
        "description": "Original desc"
    })
    
    # Patch it
    response = test_client.patch("/tasks/1", json={
        "title": "Updated"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["owner"] == "Alice"  # Unchanged


def test_patch_task_multiple_fields(test_client):
    """Test PATCH with multiple fields"""
    test_client.post("/tasks", json={
        "title": "Original",
        "owner": "Alice",
        "description": "Original desc"
    })
    
    response = test_client.patch("/tasks/1", json={
        "title": "New Title",
        "owner": "Bob",
        "description": "New desc"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["owner"] == "Bob"
    assert data["description"] == "New desc"


def test_patch_task_no_fields(test_client):
    """Test PATCH with no fields returns 422"""
    # Create a task
    create_resp = test_client.post("/tasks", json={
        "title": "Test",
        "owner": "Alice"
    })
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]
    
    # Patch with empty body should fail
    response = test_client.patch(f"/tasks/{task_id}", json={})
    assert response.status_code == 422
    assert "must be provided" in response.json()["detail"].lower()


def test_patch_task_not_found(test_client):
    """Test PATCH unknown task returns 404"""
    response = test_client.patch("/tasks/999", json={"title": "New"})
    assert response.status_code == 404


# ==========================================
# Change Status Tests
# ==========================================

def test_change_status_success(test_client):
    """Test valid status change returns 200"""
    # Create a task
    create_resp = test_client.post("/tasks", json={
        "title": "Status Test",
        "owner": "Alice"
    })
    task_id = create_resp.json()["id"]
    
    response = test_client.post(f"/tasks/{task_id}/status", json={
        "new_status": "in_progress"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"


def test_change_status_from_todo_to_done(test_client):
    """Test status transition from todo to done"""
    create_resp = test_client.post("/tasks", json={
        "title": "Complete this",
        "owner": "Alice"
    })
    task_id = create_resp.json()["id"]
    
    response = test_client.post(f"/tasks/{task_id}/status", json={
        "new_status": "done"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_change_status_not_found(test_client):
    """Test change status for unknown task returns 404"""
    response = test_client.post("/tasks/999/status", json={
        "new_status": "done"
    })
    assert response.status_code == 404


def test_change_status_from_canceled_fails(test_client):
    """Test cannot change status from canceled returns 409"""
    # Create a task first
    create_resp = test_client.post("/tasks", json={
        "title": "Canceled task",
        "owner": "Alice"
    })
    task_id = create_resp.json()["id"]
    
    # Manually update status to canceled using the test database
    import db_handler
    import os
    from pathlib import Path
    
    conn = db_handler.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'canceled' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    # Try to change status
    response = test_client.post(f"/tasks/{task_id}/status", json={
        "new_status": "in_progress"
    })
    assert response.status_code == 409
    assert "cannot change status" in response.json()["detail"].lower()


# ==========================================
# Integration Tests
# ==========================================

def test_full_task_lifecycle(test_client):
    """Test creating, updating, and changing status of a task"""
    # 1. Create task
    response = test_client.post("/tasks", json={
        "title": "Full Lifecycle",
        "owner": "Alice",
        "description": "Start"
    })
    assert response.status_code == 201
    task_id = response.json()["id"]
    
    # 2. Get task
    response = test_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "todo"
    
    # 3. Update task
    response = test_client.patch(f"/tasks/{task_id}", json={
        "description": "Updated"
    })
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"
    
    # 4. Change status to in_progress
    response = test_client.post(f"/tasks/{task_id}/status", json={
        "new_status": "in_progress"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    
    # 5. Change status to done
    response = test_client.post(f"/tasks/{task_id}/status", json={
        "new_status": "done"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "done"
