"""
Mock in-memory database for development without PostgreSQL.
Stores tasks in memory and simulates database operations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MockDatabaseHandler:
    """Mock database that stores data in memory."""

    _instance = None
    _tasks_storage = {}
    _next_id = 1

    def __init__(self):
        """Initialize mock database."""
        self._initialize_tables()

    def _initialize_tables(self):
        """Initialize mock database tables."""
        logger.info("Mock database initialized (in-memory storage)")

    def get_connection(self):
        """Dummy connection method."""
        return None

    def ensure_tables_exist(self):
        """Dummy table creation (tables already exist in memory)."""
        logger.info("Mock tables verified (in-memory storage)")

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Mock INSERT/UPDATE/DELETE operations.
        Returns the ID of inserted row or affected rows count.
        """
        query_lower = query.strip().upper()

        if "INSERT" in query_lower:
            return self._handle_insert(query, params)
        elif "UPDATE" in query_lower:
            return self._handle_update(query, params)
        elif "DELETE" in query_lower:
            return self._handle_delete(query, params)
        else:
            raise ValueError(f"Unsupported query: {query}")

    def _handle_insert(self, query: str, params: tuple) -> int:
        """Handle INSERT queries."""
        # Extract values: INSERT INTO tasks (title, description, owner, status, created_at, updated_at) VALUES ...
        if "tasks" not in query.lower():
            raise ValueError("Only tasks table supported")

        task_id = self._next_id
        self._next_id += 1

        # params: (title, description, owner, status, created_at, updated_at)
        self._tasks_storage[task_id] = {
            "id": task_id,
            "title": params[0],
            "description": params[1],
            "owner": params[2],
            "status": params[3],
            "created_at": params[4],
            "updated_at": params[5],
        }
        logger.debug(f"Mock INSERT: task_id={task_id}")
        return task_id

    def _handle_update(self, query: str, params: tuple) -> int:
        """Handle UPDATE queries."""
        if "WHERE id = %s" not in query:
            raise ValueError("Only UPDATE by id supported")

        # For UPDATE ... SET ... WHERE id = %s
        # Extract task_id from the last param
        task_id = params[-1]

        if task_id not in self._tasks_storage:
            return 0

        # Parse which fields are being updated
        if "SET title" in query and "SET owner" in query and "SET description" in query:
            # UPDATE tasks SET title = %s, owner = %s, description = %s, updated_at = %s WHERE id = %s;
            self._tasks_storage[task_id]["title"] = params[0]
            self._tasks_storage[task_id]["owner"] = params[1]
            self._tasks_storage[task_id]["description"] = params[2]
            self._tasks_storage[task_id]["updated_at"] = params[3]
        elif "SET status" in query:
            # UPDATE tasks SET status = %s, updated_at = %s WHERE id = %s;
            self._tasks_storage[task_id]["status"] = params[0]
            self._tasks_storage[task_id]["updated_at"] = params[1]

        logger.debug(f"Mock UPDATE: task_id={task_id}")
        return 1

    def _handle_delete(self, query: str, params: tuple) -> int:
        """Handle DELETE queries."""
        if "WHERE id = %s" not in query:
            raise ValueError("Only DELETE by id supported")

        task_id = params[0]

        if task_id in self._tasks_storage:
            del self._tasks_storage[task_id]
            logger.debug(f"Mock DELETE: task_id={task_id}")
            return 1
        return 0

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Get a single row."""
        if "WHERE id = %s" not in query:
            raise ValueError("Only fetch by id supported")

        task_id = params[0]
        result = self._tasks_storage.get(task_id)
        logger.debug(f"Mock FETCH_ONE: task_id={task_id}, found={result is not None}")
        return result

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Get all rows with optional filtering and sorting."""
        results = list(self._tasks_storage.values())

        # Apply filters from WHERE clause
        params_idx = 0
        if "WHERE status = %s" in query and "WHERE owner = %s" in query:
            # Both filters
            status_filter = params[params_idx]
            owner_filter = params[params_idx + 1]
            results = [
                t
                for t in results
                if t["status"] == status_filter and t["owner"] == owner_filter
            ]
            params_idx += 2
        elif "WHERE status = %s" in query:
            # Status filter only
            status_filter = params[params_idx]
            results = [t for t in results if t["status"] == status_filter]
            params_idx += 1
        elif "WHERE owner = %s" in query:
            # Owner filter only
            owner_filter = params[params_idx]
            results = [t for t in results if t["owner"] == owner_filter]
            params_idx += 1

        # Apply sorting
        if "ORDER BY id" in query:
            results.sort(key=lambda x: x["id"])
        elif "ORDER BY title" in query:
            results.sort(key=lambda x: x["title"])
        elif "ORDER BY owner" in query:
            results.sort(key=lambda x: x["owner"])
        elif "ORDER BY status" in query:
            results.sort(key=lambda x: x["status"])
        elif "ORDER BY created_at" in query:
            results.sort(key=lambda x: x["created_at"])
        elif "ORDER BY updated_at" in query:
            results.sort(key=lambda x: x["updated_at"])

        logger.debug(f"Mock FETCH_ALL: returned {len(results)} rows")
        return results


def get_mock_db_handler() -> MockDatabaseHandler:
    """Get or create the mock database handler instance."""
    global _mock_db_handler
    if _mock_db_handler is None:
        _mock_db_handler = MockDatabaseHandler()
    return _mock_db_handler


_mock_db_handler = None
