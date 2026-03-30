"""
Task Management System - OOP implementation.
Contains Task model and TaskManager service class.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from db_handler import get_db_handler
from exceptions import (
    TaskNotFoundError,
    InvalidStatusTransitionError,
    InvalidInputError,
    DatabaseError,
)
import logging

logger = logging.getLogger(__name__)


class Task:
    """
    Task model class.
    Represents a single task with all its properties.
    """

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str,
        owner: str,
        status: str,
        created_at: str,
        updated_at: str,
    ):
        """
        Initialize a Task instance.

        Args:
            task_id: Unique task identifier.
            title: Task title.
            description: Task description.
            owner: Task owner name.
            status: Current task status.
            created_at: ISO timestamp when task was created.
            updated_at: ISO timestamp when task was last updated.
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.owner = owner
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self) -> str:
        """String representation of task."""
        return (
            f"[{self.id}] {self.title} | Owner: {self.owner} | Status: {self.status}"
        )


class TaskManager:
    """
    Task Manager service class.
    Handles all business logic for task operations.
    Interacts with the database through TaskRepository.
    """

    # Valid task statuses
    VALID_STATUSES = {"todo", "in_progress", "done", "canceled", "blocked"}

    # Statuses that prevent further updates
    TERMINAL_STATUSES = {"canceled", "blocked"}

    def __init__(self):
        """Initialize TaskManager with database handler."""
        self.db = get_db_handler()
        self._db_initialized = False
    
    def _ensure_db_ready(self):
        """Ensure database is ready before operations. Call once on first use."""
        if not self._db_initialized:
            try:
                self.db.ensure_tables_exist()
                self._db_initialized = True
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise DatabaseError(f"Database not ready: {e}")

    def create_task(
        self, title: str, owner: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new task.

        Args:
            title: Task title (required).
            owner: Task owner (required).
            description: Task description (optional).

        Returns:
            Dictionary with created task details.

        Raises:
            InvalidInputError: If title or owner are empty.
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()

        # Validate inputs
        if not title or not title.strip():
            raise InvalidInputError("Task title cannot be empty.")
        if not owner or not owner.strip():
            raise InvalidInputError("Task owner cannot be empty.")

        title = title.strip()
        owner = owner.strip()
        description = description.strip() if description else ""

        try:
            now = datetime.now().isoformat()
            query = """
                INSERT INTO tasks (title, description, owner, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            result = self.db.execute_update(
                query, (title, description, owner, "todo", now, now)
            )

            logger.info(f"Task created: id={result}, title={title}, owner={owner}")

            return {
                "id": result,
                "title": title,
                "description": description,
                "owner": owner,
                "status": "todo",
                "created_at": now,
                "updated_at": now,
            }

        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise DatabaseError(f"Failed to create task: {e}")

    def get_task_by_id(self, task_id: int) -> Dict[str, Any]:
        """Retrieve a task by ID.

        Args:
            task_id: The task ID.

        Returns:
            Dictionary with task details.

        Raises:
            TaskNotFoundError: If task does not exist.
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()
        try:
            query = "SELECT * FROM tasks WHERE id = %s;"
            result = self.db.fetch_one(query, (task_id,))

            if not result:
                raise TaskNotFoundError(f"Task with ID {task_id} not found.")

            return result

        except TaskNotFoundError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise DatabaseError(f"Failed to get task: {e}")

    def list_tasks(
        self,
        filter_status: Optional[str] = None,
        filter_owner: Optional[str] = None,
        sort_by: str = "id",
    ) -> List[Dict[str, Any]]:
        """List all tasks with optional filtering and sorting.

        Args:
            filter_status: Filter by task status (optional).
            filter_owner: Filter by task owner (optional).
            sort_by: Field to sort by (default: "id").

        Returns:
            List of task dictionaries.

        Raises:
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()
        try:
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []

            # Apply filters
            if filter_status:
                query += " AND status = %s"
                params.append(filter_status)

            if filter_owner:
                query += " AND owner = %s"
                params.append(filter_owner)

            # Validate sort column to prevent SQL injection
            allowed_sort = ["id", "title", "owner", "status", "created_at", "updated_at"]
            if sort_by not in allowed_sort:
                sort_by = "id"

            query += f" ORDER BY {sort_by};"

            results = self.db.fetch_all(query, tuple(params))
            return results

        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise DatabaseError(f"Failed to list tasks: {e}")

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        owner: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a task (PATCH operation).

        Args:
            task_id: The task ID.
            title: New title (optional).
            owner: New owner (optional).
            description: New description (optional).

        Returns:
            Dictionary with updated task details.

        Raises:
            TaskNotFoundError: If task does not exist.
            InvalidInputError: If no fields provided or task is in terminal status.
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()
        # Validate that at least one field is provided
        if title is None and owner is None and description is None:
            raise InvalidInputError(
                "At least one field (title, owner, or description) must be provided."
            )

        try:
            # Get current task
            task = self.get_task_by_id(task_id)

            # Check if task is in terminal status
            if task["status"] in self.TERMINAL_STATUSES:
                raise InvalidInputError(
                    f"Cannot modify task in terminal status '{task['status']}'."
                )

            # Use provided values or keep existing ones
            new_title = title.strip() if title else task["title"]
            new_owner = owner.strip() if owner else task["owner"]
            new_description = description.strip() if description else task["description"]
            now = datetime.now().isoformat()

            query = """
                UPDATE tasks
                SET title = %s, owner = %s, description = %s, updated_at = %s
                WHERE id = %s;
            """
            self.db.execute_update(
                query, (new_title, new_owner, new_description, now, task_id)
            )

            logger.info(f"Task {task_id} updated.")

            return {
                "id": task_id,
                "title": new_title,
                "owner": new_owner,
                "description": new_description,
                "status": task["status"],
                "created_at": task["created_at"],
                "updated_at": now,
            }

        except (TaskNotFoundError, InvalidInputError):
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise DatabaseError(f"Failed to update task: {e}")

    def delete_task(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: The task ID.

        Raises:
            TaskNotFoundError: If task does not exist.
            InvalidInputError: If task is in terminal status.
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()
        try:
            # Verify task exists
            task = self.get_task_by_id(task_id)

            # Prevent deletion of tasks in terminal status
            if task["status"] in self.TERMINAL_STATUSES:
                raise InvalidInputError(
                    f"Cannot delete task in terminal status '{task['status']}'."
                )

            query = "DELETE FROM tasks WHERE id = %s;"
            self.db.execute_update(query, (task_id,))

            logger.info(f"Task {task_id} deleted.")

        except (TaskNotFoundError, InvalidInputError):
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise DatabaseError(f"Failed to delete task: {e}")

    def change_status(self, task_id: int, new_status: str) -> Dict[str, Any]:
        """Change task status.

        Args:
            task_id: The task ID.
            new_status: The new status.

        Returns:
            Dictionary with updated task details.

        Raises:
            TaskNotFoundError: If task does not exist.
            InvalidStatusTransitionError: If status change is invalid.
            DatabaseError: If database operation fails.
        """
        self._ensure_db_ready()
        # Validate new status
        if new_status not in self.VALID_STATUSES:
            raise InvalidInputError(
                f"Invalid status '{new_status}'. Valid statuses: {self.VALID_STATUSES}"
            )

        try:
            task = self.get_task_by_id(task_id)
            current_status = task["status"]

            # Check if current status is terminal
            if current_status in self.TERMINAL_STATUSES:
                raise InvalidStatusTransitionError(
                    f"Cannot change status from '{current_status}'. "
                    "Task is in a terminal state."
                )

            now = datetime.now().isoformat()

            query = "UPDATE tasks SET status = %s, updated_at = %s WHERE id = %s;"
            self.db.execute_update(query, (new_status, now, task_id))

            logger.info(f"Task {task_id} status changed from {current_status} to {new_status}.")

            return {
                "id": task_id,
                "title": task["title"],
                "description": task["description"],
                "owner": task["owner"],
                "status": new_status,
                "created_at": task["created_at"],
                "updated_at": now,
            }

        except (
            TaskNotFoundError,
            InvalidStatusTransitionError,
            InvalidInputError,
        ):
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Failed to change status for task {task_id}: {e}")
            raise DatabaseError(f"Failed to change status: {e}")


# Global task manager instance
_task_manager = None


def get_task_manager() -> TaskManager:
    """Get or create the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
