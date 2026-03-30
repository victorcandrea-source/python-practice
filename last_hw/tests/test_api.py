"""
Comprehensive API tests for Task Management System.
Tests all endpoints with various scenarios including success and error cases.
"""

import pytest


# ==========================================
# Health Check Tests
# ==========================================


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_returns_200(self, test_client):
        """Test that health endpoint returns 200 OK."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_response_format(self, test_client):
        """Test health check response contains expected fields."""
        response = test_client.get("/health")
        data = response.json()
        assert "status" in data
        assert "message" in data


# ==========================================
# Create Task Tests
# ==========================================


class TestCreateTask:
    """Tests for POST /tasks endpoint."""

    def test_create_task_success(self, test_client, sample_task_data):
        """Test successful task creation returns 201."""
        response = test_client.post("/tasks", json=sample_task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["owner"] == sample_task_data["owner"]
        assert data["description"] == sample_task_data["description"]
        assert data["status"] == "todo"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_without_description(self, test_client):
        """Test creating task without optional description field."""
        payload = {"title": "Quick Task", "owner": "Charlie"}
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Quick Task"
        assert data["description"] == ""

    def test_create_task_missing_title(self, test_client):
        """Test create with missing title returns 422."""
        payload = {"owner": "Alice"}
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 422

    def test_create_task_missing_owner(self, test_client):
        """Test create with missing owner returns 422."""
        payload = {"title": "Task"}
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 422

    def test_create_task_empty_title(self, test_client):
        """Test create with empty title returns 422."""
        payload = {"title": "", "owner": "Alice"}
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 422

    def test_create_task_empty_owner(self, test_client):
        """Test create with empty owner returns 422."""
        payload = {"title": "Task", "owner": ""}
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 422

    def test_create_task_with_whitespace(self, test_client):
        """Test creating task with whitespace is handled correctly."""
        payload = {
            "title": "  Task with spaces  ",
            "owner": "  Alice  ",
            "description": "  Description  ",
        }
        response = test_client.post("/tasks", json=payload)
        assert response.status_code == 201
        data = response.json()
        # Whitespace should be trimmed
        assert data["title"] == "Task with spaces"
        assert data["owner"] == "Alice"


# ==========================================
# List Tasks Tests
# ==========================================


class TestListTasks:
    """Tests for GET /tasks endpoint."""

    def test_list_tasks_empty(self, test_client):
        """Test listing tasks when database is empty."""
        response = test_client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_single_task(self, test_client, sample_task_data):
        """Test listing tasks with one task."""
        test_client.post("/tasks", json=sample_task_data)
        response = test_client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == sample_task_data["title"]

    def test_list_tasks_with_multiple_tasks(self, test_client, multiple_tasks_data):
        """Test listing multiple tasks."""
        for task_data in multiple_tasks_data:
            test_client.post("/tasks", json=task_data)

        response = test_client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3

    def test_list_tasks_filter_by_owner(self, test_client):
        """Test filtering tasks by owner."""
        test_client.post("/tasks", json={"title": "Alice Task", "owner": "Alice"})
        test_client.post("/tasks", json={"title": "Bob Task", "owner": "Bob"})
        test_client.post("/tasks", json={"title": "Another Alice", "owner": "Alice"})

        response = test_client.get("/tasks?owner=Alice")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        for task in tasks:
            assert task["owner"] == "Alice"

    def test_list_tasks_filter_by_status(self, test_client):
        """Test filtering tasks by status."""
        # Create tasks
        resp1 = test_client.post("/tasks", json={"title": "Task 1", "owner": "Alice"})
        task1_id = resp1.json()["id"]

        resp2 = test_client.post("/tasks", json={"title": "Task 2", "owner": "Bob"})
        task2_id = resp2.json()["id"]

        # Change one task status
        test_client.post(
            f"/tasks/{task1_id}/status", json={"new_status": "in_progress"}
        )

        # Filter by status
        response = test_client.get("/tasks?task_status=in_progress")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["status"] == "in_progress"

    def test_list_tasks_filter_by_owner_and_status(self, test_client):
        """Test filtering tasks by both owner and status."""
        # Create tasks
        resp1 = test_client.post(
            "/tasks", json={"title": "Task 1", "owner": "Alice"}
        )
        task1_id = resp1.json()["id"]

        test_client.post("/tasks", json={"title": "Task 2", "owner": "Bob"})

        # Change task status
        test_client.post(
            f"/tasks/{task1_id}/status", json={"new_status": "done"}
        )

        # Filter by owner and status
        response = test_client.get("/tasks?owner=Alice&task_status=done")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["owner"] == "Alice"
        assert tasks[0]["status"] == "done"

    def test_list_tasks_sort_by_id(self, test_client, multiple_tasks_data):
        """Test sorting tasks by ID."""
        for task_data in multiple_tasks_data:
            test_client.post("/tasks", json=task_data)

        response = test_client.get("/tasks?sort_by=id")
        assert response.status_code == 200
        tasks = response.json()
        ids = [t["id"] for t in tasks]
        assert ids == sorted(ids)

    def test_list_tasks_sort_by_title(self, test_client):
        """Test sorting tasks by title."""
        test_client.post("/tasks", json={"title": "Zebra", "owner": "Alice"})
        test_client.post("/tasks", json={"title": "Apple", "owner": "Bob"})
        test_client.post("/tasks", json={"title": "Banana", "owner": "Charlie"})

        response = test_client.get("/tasks?sort_by=title")
        assert response.status_code == 200
        tasks = response.json()
        titles = [t["title"] for t in tasks]
        assert titles == ["Apple", "Banana", "Zebra"]

    def test_list_tasks_invalid_sort_defaults_to_id(self, test_client, sample_task_data):
        """Test that invalid sort parameter defaults to id."""
        test_client.post("/tasks", json=sample_task_data)
        response = test_client.get("/tasks?sort_by=invalid_field")
        assert response.status_code == 200
        # Should still work, defaulting to id sort


# ==========================================
# Get Task By ID Tests
# ==========================================


class TestGetTask:
    """Tests for GET /tasks/{id} endpoint."""

    def test_get_task_success(self, test_client, sample_task_data):
        """Test retrieving a task by ID."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]
        assert data["owner"] == sample_task_data["owner"]

    def test_get_task_not_found(self, test_client):
        """Test getting non-existent task returns 404."""
        response = test_client.get("/tasks/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_task_by_id_after_update(self, test_client, sample_task_data):
        """Test that GET reflects updates made via PATCH."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # Update the task
        test_client.patch(f"/tasks/{task_id}", json={"title": "Updated Title"})

        # Get the task
        response = test_client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"


# ==========================================
# Update Task (PATCH) Tests
# ==========================================


class TestPatchTask:
    """Tests for PATCH /tasks/{id} endpoint."""

    def test_patch_task_update_title(self, test_client, sample_task_data):
        """Test PATCH to update only title."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/tasks/{task_id}", json={"title": "New Title"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["owner"] == sample_task_data["owner"]

    def test_patch_task_update_owner(self, test_client, sample_task_data):
        """Test PATCH to update only owner."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/tasks/{task_id}", json={"owner": "Bob"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["owner"] == "Bob"
        assert data["title"] == sample_task_data["title"]

    def test_patch_task_update_description(self, test_client, sample_task_data):
        """Test PATCH to update only description."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/tasks/{task_id}", json={"description": "New Description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New Description"

    def test_patch_task_update_multiple_fields(self, test_client, sample_task_data):
        """Test PATCH with multiple fields."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/tasks/{task_id}",
            json={"title": "New Title", "owner": "David"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["owner"] == "David"

    def test_patch_task_no_fields_fails(self, test_client, sample_task_data):
        """Test PATCH with no fields returns 422."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.patch(f"/tasks/{task_id}", json={})
        assert response.status_code == 422
        assert "must be provided" in response.json()["detail"].lower()

    def test_patch_task_not_found(self, test_client):
        """Test PATCH on non-existent task returns 404."""
        response = test_client.patch(
            "/tasks/999", json={"title": "New"}
        )
        assert response.status_code == 404

    def test_patch_task_in_terminal_status_fails(self, test_client, sample_task_data):
        """Test PATCH on task in terminal status fails."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # Move to terminal status
        test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "canceled"}
        )

        # Try to update
        response = test_client.patch(
            f"/tasks/{task_id}", json={"title": "New Title"}
        )
        assert response.status_code == 422
        assert "terminal status" in response.json()["detail"].lower()

    def test_patch_updates_updated_at_timestamp(self, test_client, sample_task_data):
        """Test that PATCH updates the updated_at timestamp."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]
        created_updated_at = create_resp.json()["updated_at"]

        import time
        time.sleep(0.1)  # Ensure timestamp difference

        response = test_client.patch(
            f"/tasks/{task_id}", json={"title": "New Title"}
        )
        assert response.json()["updated_at"] > created_updated_at


# ==========================================
# Delete Task Tests
# ==========================================


class TestDeleteTask:
    """Tests for DELETE /tasks/{id} endpoint."""

    def test_delete_task_success(self, test_client, sample_task_data):
        """Test successful task deletion returns 204."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        # Verify task is deleted
        get_resp = test_client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_delete_task_not_found(self, test_client):
        """Test deleting non-existent task returns 404."""
        response = test_client.delete("/tasks/999")
        assert response.status_code == 404

    def test_delete_task_in_terminal_status_fails(self, test_client, sample_task_data):
        """Test cannot delete task in terminal status."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # Move to terminal status
        test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "canceled"}
        )

        # Try to delete
        response = test_client.delete(f"/tasks/{task_id}")
        assert response.status_code == 422
        assert "terminal status" in response.json()["detail"].lower()

    def test_delete_removes_from_list(self, test_client):
        """Test that deleted task no longer appears in list."""
        resp1 = test_client.post("/tasks", json={"title": "Task 1", "owner": "Alice"})
        resp2 = test_client.post("/tasks", json={"title": "Task 2", "owner": "Bob"})

        task1_id = resp1.json()["id"]

        # Delete first task
        test_client.delete(f"/tasks/{task1_id}")

        # List should only have second task
        list_resp = test_client.get("/tasks")
        tasks = list_resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 2"


# ==========================================
# Change Task Status Tests
# ==========================================


class TestChangeTaskStatus:
    """Tests for POST /tasks/{id}/status endpoint."""

    def test_change_status_success(self, test_client, sample_task_data):
        """Test successful status change returns 200."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_change_status_from_todo_to_done(self, test_client, sample_task_data):
        """Test todo -> done transition."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "done"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"

    def test_change_status_todo_to_in_progress_to_done(self, test_client, sample_task_data):
        """Test full workflow: todo -> in_progress -> done."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # todo -> in_progress
        resp1 = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "in_progress"}
        )
        assert resp1.json()["status"] == "in_progress"

        # in_progress -> done
        resp2 = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "done"}
        )
        assert resp2.json()["status"] == "done"

    def test_change_status_to_canceled(self, test_client, sample_task_data):
        """Test changing status to canceled."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "canceled"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "canceled"

    def test_change_status_to_blocked(self, test_client, sample_task_data):
        """Test changing status to blocked."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "blocked"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "blocked"

    def test_change_status_from_canceled_fails(self, test_client, sample_task_data):
        """Test cannot change status from canceled."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # Set to canceled
        test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "canceled"}
        )

        # Try to change status
        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "in_progress"}
        )
        assert response.status_code == 409
        assert "terminal" in response.json()["detail"].lower()

    def test_change_status_from_blocked_fails(self, test_client, sample_task_data):
        """Test cannot change status from blocked."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        # Set to blocked
        test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "blocked"}
        )

        # Try to change status
        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "done"}
        )
        assert response.status_code == 409

    def test_change_status_not_found(self, test_client):
        """Test status change on non-existent task returns 404."""
        response = test_client.post(
            "/tasks/999/status", json={"new_status": "done"}
        )
        assert response.status_code == 404

    def test_change_status_invalid_status(self, test_client, sample_task_data):
        """Test changing to invalid status returns 422."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "invalid_status"}
        )
        assert response.status_code == 422

    def test_change_status_updates_timestamp(self, test_client, sample_task_data):
        """Test that status change updates the updated_at timestamp."""
        create_resp = test_client.post("/tasks", json=sample_task_data)
        original_updated_at = create_resp.json()["updated_at"]
        task_id = create_resp.json()["id"]

        import time
        time.sleep(0.1)

        response = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "in_progress"}
        )
        assert response.json()["updated_at"] > original_updated_at


# ==========================================
# Integration Tests
# ==========================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_task_lifecycle(self, test_client, sample_task_data):
        """Test complete task lifecycle: create -> update -> status changes -> delete."""
        # 1. Create task
        create_resp = test_client.post("/tasks", json=sample_task_data)
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "todo"

        # 2. Update task
        patch_resp = test_client.patch(
            f"/tasks/{task_id}",
            json={"description": "Updated description"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["description"] == "Updated description"

        # 3. Change to in_progress
        status_resp = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "in_progress"}
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "in_progress"

        # 4. Change to done
        status_resp2 = test_client.post(
            f"/tasks/{task_id}/status", json={"new_status": "done"}
        )
        assert status_resp2.status_code == 200
        assert status_resp2.json()["status"] == "done"

        # 5. Verify in list
        list_resp = test_client.get("/tasks")
        tasks = list_resp.json()
        task = [t for t in tasks if t["id"] == task_id][0]
        assert task["status"] == "done"

    def test_multiple_users_multiple_tasks(self, test_client):
        """Test system with multiple users and tasks."""
        users = ["Alice", "Bob", "Charlie"]
        tasks_per_user = 3

        # Create tasks for each user
        for user in users:
            for i in range(tasks_per_user):
                test_client.post(
                    "/tasks",
                    json={
                        "title": f"{user}'s Task {i+1}",
                        "owner": user,
                        "description": f"Task {i+1}",
                    },
                )

        # Verify total count
        all_tasks = test_client.get("/tasks").json()
        assert len(all_tasks) == len(users) * tasks_per_user

        # Verify filtering by owner
        for user in users:
            user_tasks = test_client.get(f"/tasks?owner={user}").json()
            assert len(user_tasks) == tasks_per_user
            for task in user_tasks:
                assert task["owner"] == user

    def test_concurrent_status_updates(self, test_client):
        """Test updating multiple task statuses."""
        # Create 3 tasks
        task_ids = []
        for i in range(3):
            resp = test_client.post(
                "/tasks",
                json={"title": f"Task {i+1}", "owner": "Alice"},
            )
            task_ids.append(resp.json()["id"])

        # Change statuses
        statuses = ["in_progress", "done", "blocked"]
        for task_id, status in zip(task_ids, statuses):
            test_client.post(
                f"/tasks/{task_id}/status", json={"new_status": status}
            )

        # Verify
        all_tasks = test_client.get("/tasks").json()
        for task in all_tasks:
            expected_status = statuses[task_ids.index(task["id"])]
            assert task["status"] == expected_status
