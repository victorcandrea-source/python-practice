"""
Unit tests for TaskManager service layer.
Tests business logic without HTTP layer.
"""

import pytest
from datetime import datetime
from exceptions import (
    TaskNotFoundError,
    InvalidStatusTransitionError,
    InvalidInputError,
    DatabaseError,
)


# ==========================================
# Create Task Tests
# ==========================================


class TestTaskManagerCreateTask:
    """Tests for TaskManager.create_task()."""

    def test_create_task_returns_dict(self, task_manager):
        """Test that create_task returns a dictionary with correct structure."""
        result = task_manager.create_task(
            title="Test Task", owner="Alice", description="A test task"
        )
        assert isinstance(result, dict)
        assert "id" in result
        assert "title" in result
        assert "owner" in result
        assert "description" in result
        assert "status" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_create_task_default_status_is_todo(self, task_manager):
        """Test that newly created tasks default to 'todo' status."""
        result = task_manager.create_task(title="New Task", owner="Bob")
        assert result["status"] == "todo"

    def test_create_task_empty_title_raises_error(self, task_manager):
        """Test that empty title raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.create_task(title="", owner="Alice")

    def test_create_task_empty_owner_raises_error(self, task_manager):
        """Test that empty owner raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.create_task(title="Task", owner="")

    def test_create_task_whitespace_title_raises_error(self, task_manager):
        """Test that whitespace-only title raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.create_task(title="   ", owner="Alice")

    def test_create_task_whitespace_owner_raises_error(self, task_manager):
        """Test that whitespace-only owner raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.create_task(title="Task", owner="   ")

    def test_create_task_optional_description(self, task_manager):
        """Test creating task without description."""
        result = task_manager.create_task(title="Task", owner="Alice")
        assert result["description"] == ""

    def test_create_task_with_description(self, task_manager):
        """Test creating task with description."""
        result = task_manager.create_task(
            title="Task",
            owner="Alice",
            description="A detailed description",
        )
        assert result["description"] == "A detailed description"

    def test_create_task_trims_whitespace(self, task_manager):
        """Test that create_task trims whitespace from inputs."""
        result = task_manager.create_task(
            title="  Task  ", owner="  Alice  ", description="  Description  "
        )
        assert result["title"] == "Task"
        assert result["owner"] == "Alice"
        assert result["description"] == "Description"

    def test_create_task_returns_unique_ids(self, task_manager):
        """Test that multiple tasks get unique IDs."""
        result1 = task_manager.create_task(title="Task 1", owner="Alice")
        result2 = task_manager.create_task(title="Task 2", owner="Bob")
        assert result1["id"] != result2["id"]


# ==========================================
# Get Task Tests
# ==========================================


class TestTaskManagerGetTask:
    """Tests for TaskManager.get_task_by_id()."""

    def test_get_task_existing_task(self, task_manager):
        """Test retrieving an existing task."""
        created = task_manager.create_task(title="Test", owner="Alice")
        retrieved = task_manager.get_task_by_id(created["id"])
        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == "Test"

    def test_get_task_non_existent_raises_error(self, task_manager):
        """Test getting non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task_by_id(999)

    def test_get_task_returns_all_fields(self, task_manager):
        """Test that get_task returns all required fields."""
        created = task_manager.create_task(
            title="Complete Task", owner="Alice", description="Full details"
        )
        retrieved = task_manager.get_task_by_id(created["id"])

        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == "Complete Task"
        assert retrieved["owner"] == "Alice"
        assert retrieved["description"] == "Full details"
        assert retrieved["status"] == "todo"
        assert "created_at" in retrieved
        assert "updated_at" in retrieved


# ==========================================
# List Tasks Tests
# ==========================================


class TestTaskManagerListTasks:
    """Tests for TaskManager.list_tasks()."""

    def test_list_tasks_empty(self, task_manager):
        """Test listing tasks when database is empty."""
        result = task_manager.list_tasks()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_tasks_returns_all(self, task_manager):
        """Test that list returns all tasks."""
        task_manager.create_task(title="Task 1", owner="Alice")
        task_manager.create_task(title="Task 2", owner="Bob")
        result = task_manager.list_tasks()
        assert len(result) == 2

    def test_list_tasks_filter_by_owner(self, task_manager):
        """Test filtering tasks by owner."""
        task_manager.create_task(title="Alice Task", owner="Alice")
        task_manager.create_task(title="Bob Task", owner="Bob")
        task_manager.create_task(title="Another Alice", owner="Alice")

        result = task_manager.list_tasks(filter_owner="Alice")
        assert len(result) == 2
        for task in result:
            assert task["owner"] == "Alice"

    def test_list_tasks_filter_by_status(self, task_manager):
        """Test filtering tasks by status."""
        t1 = task_manager.create_task(title="Task 1", owner="Alice")
        t2 = task_manager.create_task(title="Task 2", owner="Bob")

        task_manager.change_status(t1["id"], "done")

        result = task_manager.list_tasks(filter_status="done")
        assert len(result) == 1
        assert result[0]["status"] == "done"

    def test_list_tasks_filter_by_owner_and_status(self, task_manager):
        """Test filtering by both owner and status."""
        t1 = task_manager.create_task(title="Alice 1", owner="Alice")
        t2 = task_manager.create_task(title="Alice 2", owner="Alice")
        task_manager.create_task(title="Bob 1", owner="Bob")

        task_manager.change_status(t1["id"], "done")

        result = task_manager.list_tasks(
            filter_owner="Alice", filter_status="done"
        )
        assert len(result) == 1
        assert result[0]["owner"] == "Alice"
        assert result[0]["status"] == "done"

    def test_list_tasks_sort_by_id(self, task_manager):
        """Test sorting by id."""
        task_manager.create_task(title="Task 1", owner="Alice")
        task_manager.create_task(title="Task 2", owner="Bob")
        task_manager.create_task(title="Task 3", owner="Charlie")

        result = task_manager.list_tasks(sort_by="id")
        ids = [t["id"] for t in result]
        assert ids == sorted(ids)

    def test_list_tasks_sort_by_title(self, task_manager):
        """Test sorting by title."""
        task_manager.create_task(title="Zebra", owner="Alice")
        task_manager.create_task(title="Apple", owner="Bob")
        task_manager.create_task(title="Banana", owner="Charlie")

        result = task_manager.list_tasks(sort_by="title")
        titles = [t["title"] for t in result]
        assert titles == ["Apple", "Banana", "Zebra"]

    def test_list_tasks_invalid_sort_defaults_to_id(self, task_manager):
        """Test that invalid sort column defaults to id."""
        task_manager.create_task(title="Task 1", owner="Alice")
        task_manager.create_task(title="Task 2", owner="Bob")

        # Should not raise, defaults to id sort
        result = task_manager.list_tasks(sort_by="invalid_field")
        assert len(result) == 2


# ==========================================
# Update Task Tests
# ==========================================


class TestTaskManagerUpdateTask:
    """Tests for TaskManager.update_task()."""

    def test_update_task_title(self, task_manager):
        """Test updating task title."""
        created = task_manager.create_task(title="Original", owner="Alice")
        result = task_manager.update_task(created["id"], title="Updated")
        assert result["title"] == "Updated"
        assert result["owner"] == "Alice"

    def test_update_task_owner(self, task_manager):
        """Test updating task owner."""
        created = task_manager.create_task(title="Task", owner="Alice")
        result = task_manager.update_task(created["id"], owner="Bob")
        assert result["owner"] == "Bob"

    def test_update_task_description(self, task_manager):
        """Test updating task description."""
        created = task_manager.create_task(
            title="Task", owner="Alice", description="Original"
        )
        result = task_manager.update_task(
            created["id"], description="Updated"
        )
        assert result["description"] == "Updated"

    def test_update_task_multiple_fields(self, task_manager):
        """Test updating multiple fields."""
        created = task_manager.create_task(
            title="Original", owner="Alice", description="Original desc"
        )
        result = task_manager.update_task(
            created["id"],
            title="New Title",
            owner="Bob",
            description="New desc",
        )
        assert result["title"] == "New Title"
        assert result["owner"] == "Bob"
        assert result["description"] == "New desc"

    def test_update_task_no_fields_raises_error(self, task_manager):
        """Test that updating with no fields raises InvalidInputError."""
        created = task_manager.create_task(title="Task", owner="Alice")
        with pytest.raises(InvalidInputError):
            task_manager.update_task(created["id"])

    def test_update_task_not_found_raises_error(self, task_manager):
        """Test updating non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.update_task(999, title="New")

    def test_update_task_terminal_status_raises_error(self, task_manager):
        """Test that updating task in terminal status raises error."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.change_status(created["id"], "canceled")

        with pytest.raises(InvalidInputError):
            task_manager.update_task(created["id"], title="New Title")

    def test_update_task_updates_timestamp(self, task_manager):
        """Test that update changes the updated_at timestamp."""
        created = task_manager.create_task(title="Task", owner="Alice")
        original_updated = created["updated_at"]

        import time
        time.sleep(0.1)

        result = task_manager.update_task(created["id"], title="New")
        assert result["updated_at"] > original_updated

    def test_update_task_preserves_status(self, task_manager):
        """Test that update preserves task status."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.change_status(created["id"], "in_progress")

        result = task_manager.update_task(created["id"], title="Updated")
        assert result["status"] == "in_progress"


# ==========================================
# Delete Task Tests
# ==========================================


class TestTaskManagerDeleteTask:
    """Tests for TaskManager.delete_task()."""

    def test_delete_task_success(self, task_manager):
        """Test successful task deletion."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.delete_task(created["id"])

        # Verify it's deleted
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task_by_id(created["id"])

    def test_delete_task_not_found_raises_error(self, task_manager):
        """Test deleting non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task(999)

    def test_delete_task_in_terminal_status_raises_error(self, task_manager):
        """Test that deleting task in terminal status raises error."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.change_status(created["id"], "canceled")

        with pytest.raises(InvalidInputError):
            task_manager.delete_task(created["id"])

    def test_delete_removes_from_list(self, task_manager):
        """Test that deleted task no longer appears in list."""
        t1 = task_manager.create_task(title="Task 1", owner="Alice")
        t2 = task_manager.create_task(title="Task 2", owner="Bob")

        task_manager.delete_task(t1["id"])

        result = task_manager.list_tasks()
        assert len(result) == 1
        assert result[0]["id"] == t2["id"]


# ==========================================
# Change Status Tests
# ==========================================


class TestTaskManagerChangeStatus:
    """Tests for TaskManager.change_status()."""

    def test_change_status_success(self, task_manager):
        """Test successful status change."""
        created = task_manager.create_task(title="Task", owner="Alice")
        result = task_manager.change_status(created["id"], "in_progress")
        assert result["status"] == "in_progress"

    def test_change_status_valid_transitions(self, task_manager):
        """Test various valid status transitions."""
        created = task_manager.create_task(title="Task", owner="Alice")

        # todo -> in_progress
        task_manager.change_status(created["id"], "in_progress")
        # in_progress -> done
        task_manager.change_status(created["id"], "done")
        # Verify final status
        task = task_manager.get_task_by_id(created["id"])
        assert task["status"] == "done"

    def test_change_status_to_blocked(self, task_manager):
        """Test changing status to blocked."""
        created = task_manager.create_task(title="Task", owner="Alice")
        result = task_manager.change_status(created["id"], "blocked")
        assert result["status"] == "blocked"

    def test_change_status_to_canceled(self, task_manager):
        """Test changing status to canceled."""
        created = task_manager.create_task(title="Task", owner="Alice")
        result = task_manager.change_status(created["id"], "canceled")
        assert result["status"] == "canceled"

    def test_change_status_invalid_status_raises_error(self, task_manager):
        """Test that invalid status raises InvalidInputError."""
        created = task_manager.create_task(title="Task", owner="Alice")
        with pytest.raises(InvalidInputError):
            task_manager.change_status(created["id"], "invalid_status")

    def test_change_status_from_canceled_raises_error(self, task_manager):
        """Test that cannot transition from canceled (terminal)."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.change_status(created["id"], "canceled")

        with pytest.raises(InvalidStatusTransitionError):
            task_manager.change_status(created["id"], "done")

    def test_change_status_from_blocked_raises_error(self, task_manager):
        """Test that cannot transition from blocked (terminal)."""
        created = task_manager.create_task(title="Task", owner="Alice")
        task_manager.change_status(created["id"], "blocked")

        with pytest.raises(InvalidStatusTransitionError):
            task_manager.change_status(created["id"], "done")

    def test_change_status_not_found_raises_error(self, task_manager):
        """Test changing status of non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.change_status(999, "done")

    def test_change_status_updates_timestamp(self, task_manager):
        """Test that status change updates updated_at."""
        created = task_manager.create_task(title="Task", owner="Alice")
        original_updated = created["updated_at"]

        import time
        time.sleep(0.1)

        result = task_manager.change_status(created["id"], "in_progress")
        assert result["updated_at"] > original_updated


# ==========================================
# Task Model Tests
# ==========================================


class TestTaskModel:
    """Tests for Task model class."""

    def test_task_creation(self):
        """Test Task object creation."""
        from task_system import Task

        task = Task(
            task_id=1,
            title="Test",
            description="Desc",
            owner="Alice",
            status="todo",
            created_at="2026-01-01T10:00:00",
            updated_at="2026-01-01T10:00:00",
        )
        assert task.id == 1
        assert task.title == "Test"

    def test_task_to_dict(self):
        """Test Task.to_dict() method."""
        from task_system import Task

        task = Task(
            task_id=1,
            title="Test",
            description="Desc",
            owner="Alice",
            status="todo",
            created_at="2026-01-01T10:00:00",
            updated_at="2026-01-01T10:00:00",
        )
        task_dict = task.to_dict()
        assert isinstance(task_dict, dict)
        assert task_dict["id"] == 1
        assert task_dict["title"] == "Test"

    def test_task_str(self):
        """Test Task.__str__() method."""
        from task_system import Task

        task = Task(
            task_id=1,
            title="Test",
            description="Desc",
            owner="Alice",
            status="todo",
            created_at="2026-01-01T10:00:00",
            updated_at="2026-01-01T10:00:00",
        )
        str_repr = str(task)
        assert "[1]" in str_repr
        assert "Test" in str_repr
        assert "Alice" in str_repr
